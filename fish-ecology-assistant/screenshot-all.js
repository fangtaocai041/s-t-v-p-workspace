// screenshot-all.js — 五主题全量长图
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const HTML_PATH = path.resolve(__dirname, 'THREE_PROJECTS_EVOLUTION.html');
const OUT_DIR = path.resolve('D:/Reasonix/docs');

const THEMES = [
  { name: 'dark',   label: '暗色·GitHub风格', scheme: 'dark'  },
  { name: 'light',  label: '亮色·简洁白',      scheme: 'light' },
  { name: 'warm',   label: '暖色·羊皮纸',      scheme: 'light' },
  { name: 'forest', label: '森林·暗绿',        scheme: 'dark'  },
  { name: 'ocean',  label: '海洋·深蓝',        scheme: 'dark'  },
];

(async () => {
  console.log('🚀 启动 Chrome...');
  const browser = await chromium.launch({
    headless: true,
    channel: 'chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  for (const t of THEMES) {
    const outFile = path.join(OUT_DIR, `THREE_PROJECTS_EVOLUTION_${t.name}.png`);
    console.log(`\n🎨 [${t.label}] 渲染中...`);

    const context = await browser.newContext({
      viewport: { width: 1080, height: 900 },
      deviceScaleFactor: 2,
      colorScheme: t.scheme,
    });

    const page = await context.newPage();
    await page.goto('file:///' + HTML_PATH.replace(/\\/g, '/'), {
      waitUntil: 'networkidle',
      timeout: 15000
    });

    // 切换主题 & 隐藏切换器
    await page.evaluate((theme) => {
      document.documentElement.setAttribute('data-theme', theme);
      const picker = document.getElementById('themePicker');
      if (picker) picker.style.display = 'none';
    }, t.name);

    await page.waitForTimeout(1200);

    await page.screenshot({ path: outFile, fullPage: true, type: 'png' });

    const stat = fs.statSync(outFile);
    console.log(`   ✅ ${outFile}`);
    console.log(`   📏 ${(stat.size / 1024 / 1024).toFixed(2)} MB`);

    await context.close();
  }

  await browser.close();
  console.log('\n🎉 五主题全部完成！');
})();
