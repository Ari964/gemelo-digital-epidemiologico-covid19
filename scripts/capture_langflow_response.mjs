import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const evidenciasDir = path.resolve(__dirname, '..', 'docs', 'evidencias');

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function run() {
  console.log('Capturando respuesta completa de Langflow con Ollama...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1600,1000']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1000 });

  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle2' });
  await sleep(1500);

  // Login
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Administrador del Sistema')) {
      await btn.click();
      await sleep(400);
      break;
    }
  }
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Iniciar Sesión')) {
      await btn.click();
      await sleep(2500);
      break;
    }
  }

  // Navegar a Langflow
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Langflow')) {
      await btn.click();
      await sleep(2000);
      break;
    }
  }

  // Escribir pregunta
  const input = await page.$('input[type="text"]');
  if (input) {
    await input.click({ clickCount: 3 });
    await input.type('¿Cuál es el pronóstico nacional del modelo campeón y las camas UCI verificadas de Kiambu según Barasa et al. (2020)?');
  }

  // Clic en Ejecutar Flujo
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Ejecutar Flujo')) {
      await btn.click();
      console.log('Ejecutar Flujo presionado. Esperando inferencia local...');
      break;
    }
  }

  // Esperar a que el botón vuelva a su estado normal (no disabled / no loading)
  await sleep(14000);

  const answeredPath = path.join(evidenciasDir, 'v4_langflow_query_answered.png');
  await page.screenshot({ path: answeredPath, fullPage: true });
  console.log(`✓ Capturado: ${answeredPath}`);

  await browser.close();
  console.log('Finalizado.');
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
