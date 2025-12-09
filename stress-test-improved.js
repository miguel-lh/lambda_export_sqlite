/**
 * Prueba de estrés mejorada para endpoint de exportación de DB
 *
 * Este script está diseñado para operaciones PESADAS (exportación completa de DB)
 * No para APIs REST ligeras.
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Métricas personalizadas
const exportSuccessRate = new Rate('export_success_rate');
const exportDuration = new Trend('export_duration_seconds');
const filesDownloaded = new Counter('files_downloaded_count');

export const options = {
  stages: [
    { duration: '30s', target: 3 },   // Calentamiento muy gradual (3 VUs)
    { duration: '1m', target: 5 },    // Carga baja (5 VUs = ~5 exports/seg)
    { duration: '2m', target: 10 },   // Carga media (10 VUs)
    { duration: '1m', target: 15 },   // Pico de estrés (15 VUs)
    { duration: '30s', target: 5 },   // Descenso
    { duration: '30s', target: 0 },   // Cooldown
  ],

  // Thresholds REALISTAS para exportación de DB
  thresholds: {
    // Latencia: El 95% de las exportaciones debe completarse en menos de 10s
    'http_req_duration': ['p(95)<10000', 'p(99)<15000'],

    // Errores: Menos del 5% de fallos (considerando cold starts de Lambda)
    'http_req_failed': ['rate<0.05'],

    // Métricas custom
    'export_success_rate': ['rate>0.95'],  // 95% de éxito
    'export_duration_seconds': ['p(95)<10'],
  },
};

export default function () {
  const url = 'https://1h1bwgaoz1.execute-api.us-west-2.amazonaws.com/dev/export/64127';

  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/octet-stream',
  };

  const params = {
    headers: headers,
    timeout: '30s', // Timeout de 30s para operación pesada
  };

  // Ejecutar request
  const startTime = new Date();
  const res = http.get(url, params);
  const duration = (new Date() - startTime) / 1000;

  // Validaciones
  const checksOk = check(res, {
    'status es 200': (r) => r.status === 200,
    'tiene Content-Type correcto': (r) =>
      r.headers['Content-Type']?.includes('application/octet-stream'),
    'respuesta no está vacía': (r) => r.body && r.body.length > 0,
    'latencia < 10s': (r) => r.timings.duration < 10000,
    'latencia < 8s (objetivo)': (r) => r.timings.duration < 8000,
    'tiene header X-File-Size': (r) => r.headers['X-File-Size'] !== undefined,
  });

  // Registrar métricas personalizadas
  exportSuccessRate.add(res.status === 200);
  exportDuration.add(duration);

  if (res.status === 200) {
    filesDownloaded.add(1);

    // Log de éxito con detalles
    console.log(
      `✓ Export OK | ` +
      `Duration: ${duration.toFixed(2)}s | ` +
      `Size: ${res.headers['X-File-Size'] || 'unknown'} bytes | ` +
      `Exec time: ${res.headers['X-Execution-Time-Ms'] || 'unknown'}ms`
    );
  } else {
    console.error(
      `✗ Export FAILED | ` +
      `Status: ${res.status} | ` +
      `Duration: ${duration.toFixed(2)}s | ` +
      `Error: ${res.body?.substring(0, 100)}`
    );
  }

  // Sleep entre 3-7 segundos (más realista para operación pesada)
  // Esto simula usuarios reales que no hacen exportaciones cada segundo
  const sleepTime = 3 + Math.random() * 4; // 3-7s
  sleep(sleepTime);
}

/**
 * Setup: Se ejecuta una vez al inicio
 */
export function setup() {
  console.log('🚀 Iniciando prueba de estrés de exportación de DB');
  console.log('📊 Configuración:');
  console.log('   - Max VUs: 15 (realista para operación pesada)');
  console.log('   - Duración total: ~6 minutos');
  console.log('   - Threshold p95: <10s');
  console.log('   - Sleep entre requests: 3-7s (patrón humano)');
  console.log('');
}

/**
 * Teardown: Se ejecuta una vez al final
 */
export function teardown(data) {
  console.log('');
  console.log('✅ Prueba de estrés completada');
}
