import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const evidenciasDir = path.resolve(__dirname, '..', 'docs', 'evidencias');

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function run() {
  console.log('Capturando consulta Langflow respondida y fallo provocado...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1600,1000']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1000 });

  // 1. Login
  console.log('1. Autenticación...');
  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle2' });
  await sleep(1500);

  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Administrador del Sistema')) {
      await btn.click();
      await sleep(500);
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

  // 2. Ejecutar consulta en Langflow
  console.log('2. Navegando a Asistente Langflow...');
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Langflow')) {
      await btn.click();
      await sleep(2500);
      break;
    }
  }

  // Seleccionar la primera pregunta sugerida verificada
  const suggestedBtn = await page.$('button::-p-text("¿Cuál es el pronóstico nacional")').catch(() => null);
  if (suggestedBtn) {
    await suggestedBtn.click();
    await sleep(500);
  } else {
    const chatInput = await page.$('input[type="text"]');
    if (chatInput) {
      await chatInput.click({ clickCount: 3 });
      await chatInput.type('¿Cuál es el pronóstico del modelo campeón y las camas UCI verificadas de Kiambu?');
    }
  }

  // Clic en "Ejecutar Flujo"
  console.log('Haciendo clic en "Ejecutar Flujo"...');
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Ejecutar Flujo')) {
      await btn.click();
      console.log('Flujo enviado. Esperando respuesta de Ollama (6-8s)...');
      await sleep(8000);
      break;
    }
  }

  const answeredPath = path.join(evidenciasDir, 'v4_langflow_query_answered.png');
  await page.screenshot({ path: answeredPath, fullPage: true });
  console.log(`✓ Capturado: ${answeredPath}`);

  // 3. Provocar fallo de backend en simulación
  console.log('3. Provocando fallo de backend en /api/v1/simulations/run...');
  await page.setRequestInterception(true);
  page.on('request', (req) => {
    if (req.url().includes('/api/v1/simulations/run')) {
      console.log('Interceptando y bloqueando simulación para provocar fallo controlado (503)...');
      req.abort('failed');
    } else {
      req.continue();
    }
  });

  // Navegar de vuelta al Dashboard (Fase 6 o Fase 4)
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Fase 6: Despliegue NPIs')) {
      await btn.click();
      await sleep(2000);
      break;
    }
  }

  // Intentar ejecutar simulación que fallará
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Ejecutar Simulación')) {
      await btn.click();
      await sleep(3000);
      break;
    }
  }

  const failurePath = path.join(evidenciasDir, 'v4_provoked_backend_failure.png');
  await page.screenshot({ path: failurePath, fullPage: true });
  console.log(`✓ Capturado: ${failurePath}`);

  await browser.close();
  console.log('Finalizado.');
}

run().catch((err) => {
  console.error('Error:', err);
  process.exit(1);
});
