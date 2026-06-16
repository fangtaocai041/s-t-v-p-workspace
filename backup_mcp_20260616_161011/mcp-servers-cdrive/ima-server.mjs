#!/usr/bin/env node
/**
 * ima (腾讯AI工作台) MCP Server
 * 连接 Reasonix 智能体到您的 ima 知识库和笔记
 *
 * 认证方式：环境变量 IMA_CLIENT_ID + IMA_API_KEY
 * 或配置文件 ~/.config/ima/client_id + ~/.config/ima/api_key
 */

import https from 'node:https';
import fs from 'node:fs';
import path from 'node:path';
import { homedir } from 'node:os';

// ====== 配置 ======
const BASE_URL = 'ima.qq.com';
const CONFIG_DIR = path.join(homedir(), '.config', 'ima');
const CLIENT_ID_FILE = path.join(CONFIG_DIR, 'client_id');
const API_KEY_FILE = path.join(CONFIG_DIR, 'api_key');

// ====== 凭证读取 ======
function loadCredentials() {
  let clientId = process.env.IMA_CLIENT_ID || process.env.IMA_OPENAPI_CLIENTID || '';
  let apiKey = process.env.IMA_API_KEY || process.env.IMA_OPENAPI_APIKEY || '';

  if (!clientId || !apiKey) {
    try {
      if (fs.existsSync(CLIENT_ID_FILE)) {
        clientId = fs.readFileSync(CLIENT_ID_FILE, 'utf8').trim();
      }
      if (fs.existsSync(API_KEY_FILE)) {
        apiKey = fs.readFileSync(API_KEY_FILE, 'utf8').trim();
      }
    } catch (e) {
      // ignore
    }
  }

  if (!clientId || !apiKey) {
    return null;
  }
  return { clientId, apiKey };
}

// ====== HTTP 请求 ======
function imaPost(pathname, body, creds) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const options = {
      hostname: BASE_URL,
      path: pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
        'ima-openapi-clientid': creds.clientId,
        'ima-openapi-apikey': creds.apiKey,
      },
    };

    const req = https.request(options, (res) => {
      let chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(Buffer.concat(chunks).toString('utf8'));
          const code = parsed.code ?? parsed.retcode;
          if (code === 0) {
            resolve(parsed.data || parsed);
          } else {
            const msg = parsed.msg || parsed.errmsg || `API error ${code}`;
            reject(new Error(msg));
          }
        } catch (e) {
          reject(new Error(`JSON parse error: ${e.message}`));
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// ====== MCP Protocol ======
const creds = loadCredentials();

process.stdin.setEncoding('utf8');
let buffer = '';

process.stdin.on('data', (chunk) => {
  buffer += chunk;
  const lines = buffer.split('\n');
  buffer = lines.pop(); // keep incomplete line
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed) {
      try {
        const msg = JSON.parse(trimmed);
        handleMessage(msg);
      } catch (e) {
        sendError(null, -32700, `Parse error: ${e.message}`);
      }
    }
  }
});

function sendMessage(msg) {
  process.stdout.write(JSON.stringify(msg) + '\n');
}

function sendResult(id, result) {
  sendMessage({ jsonrpc: '2.0', id, result });
}

function sendError(id, code, message) {
  sendMessage({ jsonrpc: '2.0', id, error: { code, message } });
}

// ====== Tool Definitions ======
const TOOLS = [
  {
    name: 'ima_list_knowledge_bases',
    description: '列出你有权限添加内容的 ima 知识库',
    inputSchema: {
      type: 'object',
      properties: {
        cursor: { type: 'string', description: '翻页游标，首次留空' },
        limit: { type: 'number', description: '每页数量 (1-50)', default: 20 },
      },
    },
    handler: async (args) => {
      return await imaPost('/openapi/wiki/v1/get_addable_knowledge_base_list', {
        cursor: args.cursor || '',
        limit: args.limit || 20,
      }, creds);
    },
  },
  {
    name: 'ima_search_knowledge_bases',
    description: '搜索 ima 知识库（按名称）',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        cursor: { type: 'string', description: '翻页游标，首次留空' },
        limit: { type: 'number', description: '每页数量 (1-50)', default: 20 },
      },
      required: ['query'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/wiki/v1/search_knowledge_base', {
        query: args.query,
        cursor: args.cursor || '',
        limit: args.limit || 20,
      }, creds);
    },
  },
  {
    name: 'ima_get_knowledge_base',
    description: '获取 ima 知识库详细信息',
    inputSchema: {
      type: 'object',
      properties: {
        ids: {
          type: 'array',
          items: { type: 'string' },
          description: '知识库 ID 列表 (1-20个)',
        },
      },
      required: ['ids'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/wiki/v1/get_knowledge_base', {
        ids: args.ids,
      }, creds);
    },
  },
  {
    name: 'ima_browse_knowledge',
    description: '浏览 ima 知识库内的文件和文件夹',
    inputSchema: {
      type: 'object',
      properties: {
        knowledge_base_id: { type: 'string', description: '知识库 ID' },
        folder_id: { type: 'string', description: '文件夹 ID（省略则浏览根目录）' },
        cursor: { type: 'string', description: '翻页游标，首次留空' },
        limit: { type: 'number', description: '每页数量 (1-50)', default: 20 },
      },
      required: ['knowledge_base_id'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/wiki/v1/get_knowledge_list', {
        knowledge_base_id: args.knowledge_base_id,
        folder_id: args.folder_id || '',
        cursor: args.cursor || '',
        limit: args.limit || 20,
      }, creds);
    },
  },
  {
    name: 'ima_search_knowledge',
    description: '在指定 ima 知识库中搜索内容',
    inputSchema: {
      type: 'object',
      properties: {
        knowledge_base_id: { type: 'string', description: '知识库 ID' },
        query: { type: 'string', description: '搜索关键词' },
        cursor: { type: 'string', description: '翻页游标，首次留空' },
      },
      required: ['knowledge_base_id', 'query'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/wiki/v1/search_knowledge', {
        knowledge_base_id: args.knowledge_base_id,
        query: args.query,
        cursor: args.cursor || '',
      }, creds);
    },
  },
  {
    name: 'ima_import_url',
    description: '将网页URL导入 ima 知识库（替代手动收藏）',
    inputSchema: {
      type: 'object',
      properties: {
        knowledge_base_id: { type: 'string', description: '目标知识库 ID' },
        folder_id: { type: 'string', description: '目标文件夹 ID（根目录传 knowledge_base_id）' },
        urls: { type: 'array', items: { type: 'string' }, description: 'URL 列表 (1-10个)' },
      },
      required: ['knowledge_base_id', 'folder_id', 'urls'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/wiki/v1/import_urls', {
        knowledge_base_id: args.knowledge_base_id,
        folder_id: args.folder_id,
        urls: args.urls,
      }, creds);
    },
  },
  {
    name: 'ima_list_notebooks',
    description: '列出 ima 中的所有笔记本（笔记分类目录）',
    inputSchema: {
      type: 'object',
      properties: {
        cursor: { type: 'string', description: '翻页游标，第一页传 "0"' },
        limit: { type: 'number', description: '每页数量', default: 50 },
      },
    },
    handler: async (args) => {
      return await imaPost('/openapi/note/v1/list_note_folder_by_cursor', {
        cursor: args.cursor || '0',
        limit: args.limit || 50,
      }, creds);
    },
  },
  {
    name: 'ima_list_notes',
    description: '列出指定笔记本中的笔记',
    inputSchema: {
      type: 'object',
      properties: {
        folder_id: { type: 'string', description: '笔记本 ID（留空=全部笔记）' },
        cursor: { type: 'string', description: '翻页游标，首次传空字符串' },
        limit: { type: 'number', description: '每页数量', default: 20 },
      },
    },
    handler: async (args) => {
      return await imaPost('/openapi/note/v1/list_note_by_folder_id', {
        folder_id: args.folder_id || '',
        cursor: args.cursor || '',
        limit: args.limit || 20,
      }, creds);
    },
  },
  {
    name: 'ima_search_notes',
    description: '搜索 ima 笔记（标题或正文）',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        search_type: { type: 'number', description: '0=标题检索, 1=正文检索', default: 0 },
        start: { type: 'number', description: '翻页起始', default: 0 },
        end: { type: 'number', description: '翻页结束', default: 20 },
      },
      required: ['query'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/note/v1/search_note_book', {
        search_type: args.search_type ?? 0,
        query_info: { title: args.query, content: args.query },
        start: args.start ?? 0,
        end: args.end ?? 20,
      }, creds);
    },
  },
  {
    name: 'ima_read_note',
    description: '读取 ima 笔记的纯文本内容',
    inputSchema: {
      type: 'object',
      properties: {
        doc_id: { type: 'string', description: '笔记 ID' },
      },
      required: ['doc_id'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/note/v1/get_doc_content', {
        doc_id: args.doc_id,
        target_content_format: 0,
      }, creds);
    },
  },
  {
    name: 'ima_create_note',
    description: '在 ima 中新建一篇笔记（Markdown格式）',
    inputSchema: {
      type: 'object',
      properties: {
        content: { type: 'string', description: '笔记正文（Markdown格式）' },
        folder_id: { type: 'string', description: '目标笔记本 ID（可选）' },
      },
      required: ['content'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/note/v1/import_doc', {
        content_format: 1,
        content: args.content,
        folder_id: args.folder_id || '',
      }, creds);
    },
  },
  {
    name: 'ima_append_note',
    description: '追加内容到 ima 已有笔记末尾',
    inputSchema: {
      type: 'object',
      properties: {
        doc_id: { type: 'string', description: '目标笔记 ID' },
        content: { type: 'string', description: '要追加的内容（Markdown格式）' },
      },
      required: ['doc_id', 'content'],
    },
    handler: async (args) => {
      return await imaPost('/openapi/note/v1/append_doc', {
        doc_id: args.doc_id,
        content_format: 1,
        content: args.content,
      }, creds);
    },
  },
  // ====== 新工具 ======
  {
    name: 'ima_discover_knowledge_bases',
    description: '动态发现你所有的 ima 知识库（自有+订阅）。先调这个获取最新 kb_id 列表，避免硬编码过期。',
    inputSchema: {
      type: 'object',
      properties: {
        search_terms: {
          type: 'array',
          items: { type: 'string' },
          description: '搜索词列表，用于发现订阅库。默认 ["鱼","统计","R","机器学习","大模型","DeepSeek","学习","代码"]',
        },
      },
    },
    handler: async (args) => {
      const terms = args.search_terms || ['鱼', '统计', 'R', '机器学习', '大模型', 'DeepSeek', '学习', '代码'];

      // 1. 获取可添加的知识库（自己的）
      const addable = await imaPost('/openapi/wiki/v1/get_addable_knowledge_base_list', { cursor: '', limit: 50 }, creds);
      const ownMap = {};
      for (const kb of (addable.addable_knowledge_base_list || [])) {
        ownMap[kb.name] = { id: kb.id, role: '创建者', source: 'addable' };
      }

      // 2. 用多个关键词搜订阅库
      const seen = new Set(Object.keys(ownMap));
      for (const term of terms) {
        try {
          const res = await imaPost('/openapi/wiki/v1/search_knowledge_base', { query: term, cursor: '', limit: 20 }, creds);
          for (const kb of (res.info_list || [])) {
            const name = kb.kb_name || kb.name;
            if (!seen.has(name)) {
              seen.add(name);
              ownMap[name] = {
                id: kb.kb_id || kb.id,
                role: kb.role_type || '订阅(只读)',
                creator: kb.creator || '',
                member_count: kb.member_count || '',
                content_count: kb.content_count || '',
                description: kb.description || '',
                source: 'subscribed',
              };
            }
          }
        } catch (e) { /* skip failed searches */ }
      }

      // 3. 按领域分类
      const DOMAIN_KEYWORDS = {
        '🐟鱼类学': ['鱼', '鱼类', '增养殖', '物种共存', '同位素', '性二态', '几何形态'],
        '🔬遗传学': ['遗传', '基因', 'SNP', '形态测量', 'DAPC'],
        '📊统计': ['统计', 'R语言', 'R', '生态数据', 'SPSS'],
        '🤖机器学习': ['机器学习', '随机森林', 'mlr3', 'MaxEnt'],
        '💻编程/AI': ['大模型', 'DeepSeek', 'Transformer', 'LLM', '编程', '学习'],
      };

      const classified = {};
      for (const [name, info] of Object.entries(ownMap)) {
        let domain = '📚通用';
        for (const [d, keywords] of Object.entries(DOMAIN_KEYWORDS)) {
          if (keywords.some(kw => name.includes(kw))) {
            domain = d;
            break;
          }
        }
        if (!classified[domain]) classified[domain] = [];
        classified[domain].push({ name, ...info });
      }

      return {
        total: Object.keys(ownMap).length,
        classified,
        raw_list: Object.entries(ownMap).map(([name, info]) => ({ name, ...info })),
        note: '调用 ima_search_by_domain 时传入 kb_ids（从本结果提取）即可一次搜多个库',
      };
    },
  },
  {
    name: 'ima_search_by_domain',
    description: '一次搜索多个知识库，合并返回结果。比逐个搜节省N-1次MCP调用。',
    inputSchema: {
      type: 'object',
      properties: {
        kb_ids: {
          type: 'array',
          items: { type: 'string' },
          description: '要搜索的知识库 ID 列表（先调 ima_discover_knowledge_bases 获取最新ID）',
        },
        kb_names: {
          type: 'string',
          description: '知识库名称关键词（和 kb_ids 二选一）。如 "鱼类" 会匹配名称含"鱼"的库',
        },
        query: { type: 'string', description: '搜索关键词' },
        max_per_kb: { type: 'number', description: '每个库最多返回几条', default: 8 },
      },
      required: ['query'],
    },
    handler: async (args) => {
      let ids = args.kb_ids || [];

      // 如果给的是名称关键词，先搜索匹配的库
      if (args.kb_names && ids.length === 0) {
        try {
          const discover = await imaPost('/openapi/wiki/v1/get_addable_knowledge_base_list', { cursor: '', limit: 50 }, creds);
          for (const kb of (discover.addable_knowledge_base_list || [])) {
            if (kb.name.includes(args.kb_names)) ids.push(kb.id);
          }
          // 也搜订阅库
          const searchRes = await imaPost('/openapi/wiki/v1/search_knowledge_base', { query: args.kb_names, cursor: '', limit: 20 }, creds);
          for (const kb of (searchRes.info_list || [])) {
            const kbId = kb.kb_id || kb.id;
            if (!ids.includes(kbId)) ids.push(kbId);
          }
        } catch (e) { /* continue with whatever IDs we have */ }
      }

      if (ids.length === 0) {
        return { error: '未指定知识库。请先用 ima_discover_knowledge_bases 获取kb_id列表，或在 kb_names 中传入名称关键词' };
      }

      // 并行搜索所有KB
      const promises = ids.map(async (id) => {
        try {
          const res = await imaPost('/openapi/wiki/v1/search_knowledge', {
            knowledge_base_id: id,
            query: args.query,
            cursor: '',
          }, creds);
          return { kb_id: id, results: (res.info_list || []).slice(0, args.max_per_kb || 8), total: (res.info_list || []).length };
        } catch (e) {
          return { kb_id: id, error: e.message, results: [] };
        }
      });

      const allResults = await Promise.all(promises);
      const totalFound = allResults.reduce((sum, r) => sum + r.results.length, 0);

      return {
        query: args.query,
        kbs_searched: ids.length,
        total_found: totalFound,
        results: allResults,
      };
    },
  },
];

// ====== 消息处理 ======
function handleMessage(msg) {
  const { id, method, params } = msg;

  switch (method) {
    case 'initialize': {
      sendResult(id, {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: 'ima-mcp-server', version: '1.0.0' },
      });
      break;
    }
    case 'notifications/initialized': {
      // no response needed
      break;
    }
    case 'tools/list': {
      if (!creds) {
        sendResult(id, {
          tools: [{
            name: 'ima_configure',
            description: '⚠️ 需要配置 ima 凭证。请执行：\n1. 打开 https://ima.qq.com/agent-interface\n2. 获取 Client ID 和 API Key\n3. 创建 ~/.config/ima/client_id 和 ~/.config/ima/api_key 文件\n或设置环境变量 IMA_OPENAPI_CLIENTID 和 IMA_OPENAPI_APIKEY',
            inputSchema: { type: 'object', properties: {}, required: [] },
          }],
        });
        return;
      }
      sendResult(id, { tools: TOOLS.map(t => ({ name: t.name, description: t.description, inputSchema: t.inputSchema })) });
      break;
    }
    case 'tools/call': {
      if (!creds) {
        sendError(id, -32001, 'ima 凭证未配置。请先获取 API Key: https://ima.qq.com/agent-interface');
        return;
      }
      const tool = TOOLS.find(t => t.name === params.name);
      if (!tool) {
        sendError(id, -32601, `Unknown tool: ${params.name}`);
        return;
      }
      tool.handler(params.arguments || {})
        .then((result) => {
          const text = typeof result === 'string' ? result : JSON.stringify(result, null, 2);
          sendResult(id, { content: [{ type: 'text', text }] });
        })
        .catch((err) => {
          sendError(id, -32000, err.message);
        });
      break;
    }
    default: {
      // Unknown method — just ack for protocol compliance
      sendResult(id, {});
      break;
    }
  }
}
