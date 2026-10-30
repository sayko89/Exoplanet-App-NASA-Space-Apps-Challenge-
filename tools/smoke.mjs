// Opens the deployed demo in Chromium, waits for Streamlit to boot inside Pyodide,
// visits every page and fails on any Python exception. Screenshots go to <outDir>.
//   node tools/smoke.mjs https://sayko89.github.io/Exoplanet-App-NASA-Space-Apps-Challenge-/ smoke
import { mkdirSync } from 'node:fs';
import { chromium } from 'playwright';

const [base, out = 'smoke'] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
const errors = [];
page.on('pageerror', e => { if (!/Landbot/.test(e.message)) errors.push(e.message); });

await page.goto(base, { timeout: 120000 });
await page.waitForSelector('text=Exoplanet Explorer >> nth=1', { timeout: 180000 }).catch(() => {});
await page.waitForSelector('[data-testid="stSidebarNav"]', { timeout: 180000 });

const links = ['Home', 'Exoplanet List', 'Exoplanet Details', 'AI Classifier', 'Chatbot'];
let failed = false;
for (const [i, name] of links.entries()) {
  await page.locator('[data-testid="stSidebarNav"] a', { hasText: name }).first().click();
  await page.waitForTimeout(2500);
  await page.waitForFunction(() => !document.querySelector('[data-testid="stStatusWidget"]'), null, { timeout: 90000 }).catch(() => {});
  await page.waitForTimeout(1500);
  const exc = await page.locator('[data-testid="stException"]').allInnerTexts();
  console.log(`${name}: ${exc.length ? 'EXCEPTION\n' + exc.join('\n') : 'ok'}`);
  if (exc.length) failed = true;
  await page.screenshot({ path: `${out}/${i + 1}-${name.toLowerCase().replace(/ /g, '-')}.png`, fullPage: true });
}
if (errors.length) console.log('page errors:', errors);
await browser.close();
process.exit(failed ? 1 : 0);
