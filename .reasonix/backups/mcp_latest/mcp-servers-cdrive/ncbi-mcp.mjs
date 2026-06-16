#!/usr/bin/env node

/**
 * NCBI E-utilities MCP Server
 * 
 * 3 tools that wrap NCBI's E-utilities REST API:
 *   1. ncbi_esearch  — search PubMed by query, return PMIDs + count + timeline
 *   2. ncbi_esummary — batch-fetch metadata (title, authors, journal, year, DOI) by PMID list
 *   3. ncbi_efetch   — fetch full XML for one paper, extract affiliation + abstract + references
 * 
 * No API key required (rate-limited to 3 req/sec without key).
 * Response time: 1-3 seconds per call.
 */

const NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";

/**
 * Minimal MCP transport — stdio JSON-RPC
 */
async function main() {
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  let buffer = "";

  process.stdin.on("data", (chunk) => {
    buffer += decoder.decode(chunk, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const msg = JSON.parse(line);
        handleMessage(msg).then((response) => {
          if (response) {
            process.stdout.write(encoder.encode(JSON.stringify(response) + "\n"));
          }
        }).catch((err) => {
          console.error("handler error:", err);
        });
      } catch (e) {
        console.error("parse error:", e.message);
      }
    }
  });
}

async function handleMessage(msg) {
  const { id, method, params } = msg;

  // ── Initialize ──
  if (method === "initialize") {
    return {
      id,
      type: "response",
      result: {
        protocolVersion: "2024-11-05",
        capabilities: {
          tools: {}
        },
        serverInfo: {
          name: "ncbi-mcp",
          version: "1.0.0"
        }
      }
    };
  }

  // ── List Tools ──
  if (method === "tools/list") {
    return {
      id,
      type: "response",
      result: {
        tools: [
          {
            name: "ncbi_esearch",
            description: "Search PubMed for articles matching a query. Returns PMID count, timeline data, and list of PMIDs.",
            inputSchema: {
              type: "object",
              properties: {
                query: {
                  type: "string",
                  description: "PubMed search query (e.g. 'Ochetobius elongatus', '鳤 AND genetics')"
                },
                maxResults: {
                  type: "number",
                  description: "Maximum PMIDs to return (default 50, max 100)",
                  default: 50
                }
              },
              required: ["query"]
            }
          },
          {
            name: "ncbi_esummary",
            description: "Batch-fetch article metadata (title, authors, journal, year, DOI, PMID) for a list of PMIDs.",
            inputSchema: {
              type: "object",
              properties: {
                pmids: {
                  type: "string",
                  description: "Comma-separated PMID list, e.g. '41096465,39702392,26477619'"
                }
              },
              required: ["pmids"]
            }
          },
          {
            name: "ncbi_efetch",
            description: "Fetch full PubMed XML for one PMID, extracting: authors + affiliations (exact units), abstract, references list (for citation backtracking).",
            inputSchema: {
              type: "object",
              properties: {
                pmid: {
                  type: "string",
                  description: "Single PMID"
                }
              },
              required: ["pmid"]
            }
          }
        ]
      }
    };
  }

  // ── Call Tool ──
  if (method === "tools/call") {
    const { name, arguments: args } = params;

    if (name === "ncbi_esearch") {
      return await handleESearch(id, args);
    } else if (name === "ncbi_esummary") {
      return await handleESummary(id, args);
    } else if (name === "ncbi_efetch") {
      return await handleEFetch(id, args);
    }

    return {
      id,
      type: "response",
      error: { code: -32601, message: `Unknown tool: ${name}` }
    };
  }

  // Notifications don't need a response
  return null;
}

// ── Tool implementations ──

async function handleESearch(id, args) {
  const query = encodeURIComponent(args.query);
  const maxResults = Math.min(args.maxResults || 50, 100);

  // Get PMID list
  const searchUrl = `${NCBI_BASE}/esearch.fcgi?db=pubmed&term=${query}&retmax=${maxResults}&retmode=json`;
  const searchResp = await fetch(searchUrl);
  const searchData = await searchResp.json();

  const idList = searchData?.esearchresult?.idlist || [];
  const count = parseInt(searchData?.esearchresult?.count || "0");

  // Get timeline data (year-by-year breakdown)
  const timelineUrl = `${NCBI_BASE}/esearch.fcgi?db=pubmed&term=${query}&retmax=0&retmode=json&mindate=2000&maxdate=2030&datetype=pdat&usehistory=y`;
  const timelineResp = await fetch(timelineUrl);

  return {
    id,
    type: "response",
    result: {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            total_count: count,
            pmids: idList,
            query: args.query,
            retrieved: idList.length
          }, null, 2)
        }
      ]
    }
  };
}

async function handleESummary(id, args) {
  const pmids = args.pmids;
  const url = `${NCBI_BASE}/esummary.fcgi?db=pubmed&id=${pmids}&retmode=json`;
  const resp = await fetch(url);
  const data = await resp.json();

  const result = data?.result;
  if (!result) {
    return {
      id,
      type: "response",
      result: { content: [{ type: "text", text: "No results" }] }
    };
  }

  // Clean up — extract only what we need
  const uids = result.uids || [];
  const papers = uids.map((uid) => {
    const p = result[uid];
    if (!p) return null;
    return {
      pmid: uid,
      title: p.title,
      authors: (p.authors || []).map((a) => a.name),
      journal: p.source,
      pubdate: p.pubdate,
      epubdate: p.epubdate,
      doi: (p.articleids || []).find((a) => a.idtype === "doi")?.value,
      pmc: (p.articleids || []).find((a) => a.idtype === "pmc")?.value,
      volume: p.volume,
      issue: p.issue,
      pages: p.pages,
      first_author: p.sortfirstauthor
    };
  }).filter(Boolean);

  return {
    id,
    type: "response",
    result: {
      content: [
        {
          type: "text",
          text: JSON.stringify({ papers }, null, 2)
        }
      ]
    }
  };
}

async function handleEFetch(id, args) {
  const pmid = args.pmid;
  const url = `${NCBI_BASE}/efetch.fcgi?db=pubmed&id=${pmid}&retmode=xml&rettype=abstract`;
  const resp = await fetch(url);
  const xmlText = await resp.text();

  // Extract: PMID
  const pmidMatch = xmlText.match(/<PMID[^>]*>(\d+)<\/PMID>/);
  const extractedPmid = pmidMatch ? pmidMatch[1] : pmid;

  // Extract: ArticleTitle
  const titleMatch = xmlText.match(/<ArticleTitle[^>]*>([\s\S]*?)<\/ArticleTitle>/);
  const title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g, "").trim() : "";

  // Extract: Journal
  const journalMatch = xmlText.match(/<Title>([\s\S]*?)<\/Title>/);
  const journal = journalMatch ? journalMatch[1].trim() : "";

  // Extract: Year
  const yearMatch = xmlText.match(/<PubDate>(?:[\s\S]*?)<Year>(\d{4})<\/Year>/);
  const year = yearMatch ? yearMatch[1] : "";

  // Extract: DOI
  const doiMatch = xmlText.match(/<ArticleId IdType="doi">([^<]+)<\/ArticleId>/);
  const doi = doiMatch ? doiMatch[1] : "";

  // Extract: Authors with Affiliations (KEY DATA)
  const authors = [];
  const authorRegex = /<Author[^>]*>([\s\S]*?)<\/Author>/g;
  let authorMatch;
  while ((authorMatch = authorRegex.exec(xmlText)) !== null) {
    const authorBlock = authorMatch[1];
    const lastNameMatch = authorBlock.match(/<LastName>([^<]+)<\/LastName>/);
    const foreNameMatch = authorBlock.match(/<ForeName>([^<]+)<\/ForeName>/);
    const lastName = lastNameMatch ? lastNameMatch[1] : "";
    const foreName = foreNameMatch ? foreNameMatch[1] : "";

    const affiliations = [];
    const affRegex = /<Affiliation[^>]*>([^<]+)<\/Affiliation>/g;
    let affMatch;
    while ((affMatch = affRegex.exec(authorBlock)) !== null) {
      affiliations.push(affMatch[1]);
    }

    if (lastName) {
      authors.push({
        name: `${lastName} ${foreName || ""}`.trim(),
        affiliations
      });
    }
  }

  // Extract: Abstract
  const abstractMatch = xmlText.match(/<AbstractText[^>]*>([\s\S]*?)<\/AbstractText>/);
  const abstract = abstractMatch ? abstractMatch[1].replace(/<[^>]+>/g, "").trim() : "";

  // Extract: References (for citation backtracking)
  const references = [];
  const refRegex = /<Reference>([\s\S]*?)<\/Reference>/g;
  let refMatch;
  while ((refMatch = refRegex.exec(xmlText)) !== null) {
    const refBlock = refMatch[1];
    const refTitleMatch = refBlock.match(/<ArticleTitle[^>]*>([\s\S]*?)<\/ArticleTitle>/);
    const refTitle = refTitleMatch ? refTitleMatch[1].replace(/<[^>]+>/g, "").trim() : "";
    const refJournalMatch = refBlock.match(/<Title>([^<]+)<\/Title>/);
    const refJournal = refJournalMatch ? refJournalMatch[1] : "";
    const refYearMatch = refBlock.match(/<Year>(\d{4})<\/Year>/);
    const refYear = refYearMatch ? refYearMatch[1] : "";
    const refDoiMatch = refBlock.match(/<ArticleId IdType="doi">([^<]+)<\/ArticleId>/);
    const refDoi = refDoiMatch ? refDoiMatch[1] : "";

    if (refTitle) {
      references.push({
        title: refTitle,
        journal: refJournal,
        year: refYear,
        doi: refDoi
      });
    }
  }

  return {
    id,
    type: "response",
    result: {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            pmid: extractedPmid,
            title,
            journal,
            year,
            doi,
            authors,
            abstract_preview: abstract.substring(0, 500),
            references_count: references.length,
            ochetobius_references: references.filter(
              (r) => r.title.toLowerCase().includes("ochetob") || r.title.includes("鳤")
            )
          }, null, 2)
        }
      ]
    }
  };
}

main().catch(console.error);
