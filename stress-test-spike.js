/**
 * Prueba de SPIKE - Encuentra el punto de quiebre
 *
 * Esta prueba aumenta gradualmente la carga hasta encontrar
 * cuántas exportaciones concurrentes puede manejar el sistema.
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const successRate = new Rate('success_rate');
const duration = new Trend('request_duration');

export const options = {
  stages: [
    { duration: '1m', target: 5 },    // Fase 1: 5 VUs
    { duration: '1m', target: 10 },   // Fase 2: 10 VUs
    { duration: '1m', target: 20 },   // Fase 3: 20 VUs
    { duration: '1m', target: 30 },   // Fase 4: 30 VUs (probablemente empiece a fallar)
    { duration: '1m', target: 40 },   // Fase 5: 40 VUs (punto de quiebre)
    { duration: '30s', target: 0 },   // Descenso
  ],

  thresholds: {
    'http_req_duration': ['p(95)<15000'],  // Más permisivo para encontrar límites
    'http_req_failed': ['rate<0.15'],      // Toleramos 15% de errores en spike test
    'success_rate': ['rate>0.80'],         // Al menos 80% de éxito
  },
};

export default function () {
  const url = 'https://1h1bwgaoz1.execute-api.us-west-2.amazonaws.com/dev/export/64127';

  const res = http.get(url, {
    timeout: '30s',
    tags: { name: 'ExportDB' },
  });

  const success = check(res, {
    'status 200': (r) => r.status === 200,
    'no timeout': (r) => r.status !== 0,
    'latencia < 15s': (r) => r.timings.duration < 15000,
  });

  successRate.add(success);
  duration.add(res.timings.duration / 1000);

  // Log para análisis
  if (__ITER % 10 === 0) {
    console.log(`VU: ${__VU} | Iter: ${__ITER} | Status: ${res.status} | Duration: ${(res.timings.duration/1000).toFixed(2)}s`);
  }

  sleep(2 + Math.random() * 3); // 2-5s
}

export function setup() {
  console.log('🔥 SPIKE TEST - Buscando punto de quiebre del sistema');
  console.log('⚠️  Este test PUEDE fallar - es el objetivo para encontrar límites');
}
