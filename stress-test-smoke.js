/**
 * Smoke Test - Validación rápida para CI/CD
 *
 * Verifica que el endpoint funciona correctamente con carga mínima.
 * Ideal para ejecutar en pipeline antes de deployment.
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 3,              // Solo 3 usuarios virtuales
  duration: '1m',      // 1 minuto de prueba

  thresholds: {
    'http_req_duration': ['p(95)<12000'],  // 12s
    'http_req_failed': ['rate<0.05'],      // Menos de 5% de errores
    'checks': ['rate>0.95'],               // 95% de checks pasando
  },
};

export default function () {
  const url = 'https://1h1bwgaoz1.execute-api.us-west-2.amazonaws.com/dev/export/64127';

  const res = http.get(url, {
    timeout: '30s',
  });

  check(res, {
    '✓ status es 200': (r) => r.status === 200,
    '✓ tiene contenido': (r) => r.body.length > 1000,
    '✓ es base64 encoded': (r) => r.json('isBase64Encoded') !== false,
    '✓ tiempo razonable': (r) => r.timings.duration < 12000,
  }) || console.error(`❌ Request falló: Status ${res.status}, Duration: ${res.timings.duration}ms`);

  sleep(5); // 5 segundos entre requests
}

export function setup() {
  console.log('🧪 Smoke Test - Validación básica del endpoint');
  console.log('   Este test debe pasar siempre antes de deployment');
  console.log('');
}

export function teardown(data) {
  console.log('');
  console.log('✅ Smoke test completado');
}
