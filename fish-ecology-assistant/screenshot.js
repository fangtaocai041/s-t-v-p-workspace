// screenshot.js — 将 HTML 渲染为抖音长图 (1080px 宽, 2x 高清)
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const HTML_PATH = path.resolve(__dirname, 'THREE_PROJECTS_EVOLUTION.html');
const OUT_PATH   = path.resolve(__dirname, 'THREE_PROJECTS_EVOLUTION_长图.png');

(async () => {
  console.log('🚀 启动 Chrome (系统安装版)...');
  const browser = await chromium.launch({
    headless: true,
    channel: 'chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1080, height: 900 },
    deviceScaleFactor: 2,    // 2x Retina 高清，手机屏清晰
    colorScheme: 'dark',
  });

  const page = await context.newPage();

  console.log('📄 加载 HTML...');
  await page.goto('file:///' + HTML_PATH.replace(/\\/g, '/'), {
    waitUntil: 'networkidle',
    timeout: 15000
  });

  // 隐藏右下角主题切换器，保持截图干净
  await page.evaluate(() => {
    const picker = document.getElementById('themePicker');
    if (picker) picker.style.display = 'none';
  });

  // 等字体/渲染稳定
  await page.waitForTimeout(1500);

  console.log('📸 全页截图 (fullPage)...');
  await page.screenshot({
    path: OUT_PATH,
    fullPage: true,
    type: 'png'
  });

  const stat = fs.statSync(OUT_PATH);
  console.log('✅ 生成完毕:', OUT_PATH);
  console.log('📏 文件大小:', (stat.size / 1024 / 1024).toFixed(2), 'MB');

  // 获取页面总高度（供参考）
  const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
  const vpWidth = 1080 * 2;  // 实际像素宽
  console.log('📐 分辨率:', vpWidth, '×', Math.round(bodyHeight * 2), 'px');
  console.log('📱 可直接发布抖音 (长图模式)');

  await browser.close();
})();
