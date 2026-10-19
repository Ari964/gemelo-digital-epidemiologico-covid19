import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const evidenciasDir = path.resolve(__dirname, '..', 'docs', 'evidencias');

if (!fs.existsSync(evidenciasDir)) {
  fs.mkdirSync(evidenciasDir, { recursive: true });
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function run() {
  console.log('Iniciando captura automatizada de evidencias...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1600,1000']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1000 });

  // 1. Pantalla de Login inicial
  console.log('1. Navegando a http://localhost:3000/ (Login)...');
  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle2' });
  await sleep(1500);

  const loginPath = path.join(evidenciasDir, 'v4_login_screen_es.png');
  await page.screenshot({ path: loginPath, fullPage: true });
  console.log(`✓ Capturado: ${loginPath}`);

  // Autocompletar con Admin
  console.log('Autenticando con cuenta Admin...');
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Administrador del Sistema')) {
      await btn.click();
      await sleep(500);
      break;
    }
  }

  // Click en Iniciar Sesión
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Iniciar Sesión')) {
      await btn.click();
      console.log('Iniciando sesión...');
      await sleep(2500);
      break;
    }
  }

  // 2. Estado inicial sin simulación (Dashboard limpio)
  console.log('2. Verificando estado sin simulación activa...');
  const emptyStatePath = path.join(evidenciasDir, 'v4_unsimulated_empty_state.png');
  await page.screenshot({ path: emptyStatePath, fullPage: true });
  console.log(`✓ Capturado: ${emptyStatePath}`);

  // 3. Ejecutar Simulación
  console.log('3. Ejecutando simulación en Dashboard...');
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Ejecutar Simulación')) {
      await btn.click();
      console.log('Click en botón Ejecutar Simulación. Esperando cálculo...');
      await sleep(4500);
      break;
    }
  }
  const simSuccessPath = path.join(evidenciasDir, 'v4_simulated_scenario_results.png');
  await page.screenshot({ path: simSuccessPath, fullPage: true });
  console.log(`✓ Capturado: ${simSuccessPath}`);

  // 4. Vista de Equidad
  console.log('4. Navegando a Equidad...');
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Equidad')) {
      await btn.click();
      await sleep(2000);
      break;
    }
  }
  const equityPath = path.join(evidenciasDir, 'v4_equity_audited_view.png');
  await page.screenshot({ path: equityPath, fullPage: true });
  console.log(`✓ Capturado: ${equityPath}`);

  // 5. Vista Asistente Langflow
  console.log('5. Navegando a Asistente Langflow...');
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Langflow')) {
      await btn.click();
      await sleep(3000);
      break;
    }
  }
  
  // Escribir consulta en el input del asistente si está presente
  const chatInput = await page.$('input[placeholder*="Pregunte"], textarea[placeholder*="Pregunte"], input[type="text"]');
  if (chatInput) {
    await chatInput.type('¿Cuál es la proyección de persistencia y capacidad hospitalaria en Kenia?');
    for (const btn of await page.$$('button')) {
      const text = await page.evaluate(el => el.textContent, btn);
      if (text && (text.includes('Enviar') || text.includes('Consultar') || text.includes('Preguntar'))) {
        await btn.click();
        console.log('Consulta enviada a Langflow. Esperando respuesta de Ollama...');
        await sleep(6500);
        break;
      }
    }
  }
  const langflowPath = path.join(evidenciasDir, 'v4_langflow_dual_badges_answered.png');
  await page.screenshot({ path: langflowPath, fullPage: true });
  console.log(`✓ Capturado: ${langflowPath}`);

  // 6. Tema Claro y Multilingüe (EN)
  console.log('6. Probando cambio de tema y lenguaje...');
  for (const btn of await page.$$('button')) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.trim() === 'EN') {
      await btn.click();
      await sleep(1000);
      break;
    }
  }
  const themeToggle = await page.$('button[aria-label*="modo"], button[aria-label*="theme"], button:has(svg.lucide-sun), button:has(svg.lucide-moon)');
  if (themeToggle) {
    await themeToggle.click();
    await sleep(1000);
  }
  const lightI18nPath = path.join(evidenciasDir, 'v4_light_theme_i18n_en.png');
  await page.screenshot({ path: lightI18nPath, fullPage: true });
  console.log(`✓ Capturado: ${lightI18nPath}`);

  await browser.close();
  console.log('Captura de evidencias completada exitosamente.');
}

run().catch((err) => {
  console.error('Error en captura:', err);
  process.exit(1);
});
