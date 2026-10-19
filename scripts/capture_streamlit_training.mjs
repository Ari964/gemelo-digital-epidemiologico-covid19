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
  console.log('Iniciando captura automatizada de evidencias de Streamlit...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1600,1200']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1200 });

  // Navegar directamente a Fase 4 (Modelado)
  console.log('1. Navegando a http://localhost:8501/Fase_4_Modelado...');
  await page.goto('http://localhost:8501/Fase_4_Modelado', { waitUntil: 'networkidle2', timeout: 35000 });
  await sleep(4000);

  // Esperar a que el botón primario de Streamlit esté completamente renderizado
  console.log('2. Esperando botón de ejecución de entrenamiento...');
  try {
    await page.waitForSelector('button[data-testid="baseButton-primary"], button[kind="primary"]', { timeout: 15000 });
  } catch (e) {
    console.log('Timeout esperando selector primario, buscando cualquier botón...');
  }

  const buttons = await page.$$('button');
  let trainBtn = null;
  for (const btn of buttons) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && (text.includes('Ejecutar Entrenamiento') || text.includes('Canónica'))) {
      trainBtn = btn;
      console.log(`Encontrado botón: "${text.trim()}"`);
      break;
    }
  }

  if (trainBtn) {
    console.log('3. Haciendo clic en el botón de entrenamiento canónico...');
    await trainBtn.click();
    
    // Esperar 1.5 segundos para capturar durante la ejecución real (con la barra de progreso / texto de estado)
    await sleep(1800);
    const inProgressPath = path.join(evidenciasDir, 'streamlit_entrenamiento_en_ejecucion.png');
    await page.screenshot({ path: inProgressPath, fullPage: true });
    console.log(`✓ Capturado durante ejecución: ${inProgressPath}`);

    // Esperar a que concluya el entrenamiento y recargue los datos
    console.log('4. Esperando finalización del entrenamiento y guardado de artefactos...');
    await sleep(8000);

    const completedPath = path.join(evidenciasDir, 'streamlit_fase4_entrenamiento_completado.png');
    await page.screenshot({ path: completedPath, fullPage: true });
    console.log(`✓ Capturado completado: ${completedPath}`);
  } else {
    console.error('No se pudo encontrar el botón de entrenamiento');
  }

  // 5. Cambiar a la pestaña de los 5 Pliegues CV (Tab 2)
  console.log('5. Cambiando a pestaña "Grillas de Hiperparámetros y 5 Pliegues CV"...');
  await sleep(2000);
  const tabElements = await page.$$('[role="tab"]');
  console.log(`Pestañas encontradas con role="tab": ${tabElements.length}`);
  
  let tabFolds = null;
  for (const t of tabElements) {
    const tText = await page.evaluate(el => el.textContent, t);
    console.log(`- Pestaña: "${tText.trim()}"`);
    if (tText && (tText.includes('5 Pliegues') || tText.includes('Pliegues') || tText.includes('Hiperparámetros'))) {
      tabFolds = t;
      break;
    }
  }

  if (tabFolds) {
    console.log('Haciendo clic en la pestaña de 5 pliegues...');
    await tabFolds.click();
    await sleep(3000);

    const foldsScreenshot = path.join(evidenciasDir, 'streamlit_fase4_cinco_pliegues_cv.png');
    await page.screenshot({ path: foldsScreenshot, fullPage: true });
    console.log(`✓ Capturado: ${foldsScreenshot}`);
  } else if (tabElements.length >= 2) {
    console.log('Haciendo clic en la segunda pestaña por índice...');
    await tabElements[1].click();
    await sleep(3000);
    const foldsScreenshot = path.join(evidenciasDir, 'streamlit_fase4_cinco_pliegues_cv.png');
    await page.screenshot({ path: foldsScreenshot, fullPage: true });
    console.log(`✓ Capturado: ${foldsScreenshot}`);
  }

  // 6. Navegar a Fase 5 (Evaluación Científica)
  console.log('6. Navegando a http://localhost:8501/Fase_5_Evaluacion...');
  await page.goto('http://localhost:8501/Fase_5_Evaluacion', { waitUntil: 'networkidle2', timeout: 35000 });
  await sleep(3500);

  const f5Tab1Path = path.join(evidenciasDir, 'streamlit_fase5_evaluacion_trazable.png');
  await page.screenshot({ path: f5Tab1Path, fullPage: true });
  console.log(`✓ Capturado Fase 5 Tab 1: ${f5Tab1Path}`);

  // Clic en Tab 2 de Fase 5 (Batería de Pruebas Bioestadísticas)
  const tabsF5 = await page.$$('[role="tab"]');
  if (tabsF5.length >= 2) {
    console.log('Haciendo clic en Tab 2 de Fase 5 (Bioestadística)...');
    await tabsF5[1].click();
    await sleep(2500);
    const f5BioPath = path.join(evidenciasDir, 'streamlit_fase5_pruebas_bioestadisticas_sin_fallbacks.png');
    await page.screenshot({ path: f5BioPath, fullPage: true });
    console.log(`✓ Capturado Fase 5 Tab 2: ${f5BioPath}`);
  }

  await browser.close();
  console.log('Todas las evidencias de Streamlit han sido capturadas exitosamente.');
}

run().catch(err => {
  console.error('Error durante la captura:', err);
  process.exit(1);
});
