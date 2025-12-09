# Análisis del Script de Prueba de Estrés

## Problemas Identificados

### 1. ❌ Thresholds irrealistas para operación pesada
```javascript
http_req_duration: ['p(95)<800']  // Espera 800ms para exportar DB completa
```
**Problema**: Exportar una base de datos completa, crear SQLite, y codificar en base64 no puede ser <800ms.
**Realidad actual**: p95 = 5.64s (7x más lento que el threshold)

### 2. ❌ Sleep muy corto (0.5s)
```javascript
sleep(0.5);  // Solo 0.5s entre requests
```
**Problema**:
- Cada request toma 3-5s
- Con sleep de 0.5s, cada VU intenta hacer ~2 req/s
- Con 100 VUs = 200 req/s intentadas sobre operaciones de 5s
- Esto satura Lambda y PostgreSQL innecesariamente

### 3. ❌ Tipo de prueba incorrecta
Este patrón de prueba es para **APIs REST ligeras** (ej: GET /users), no para **operaciones batch pesadas** como exportación de DB.

### 4. ❌ No considera cold starts
Lambda cold starts añaden 1-3s. Con ramp-up rápido, muchos VUs nuevos = muchos cold starts.

## Recomendaciones

### Opción A: Prueba Realista de Carga Sostenida
Si quieres saber cuántas exportaciones concurrentes puede manejar tu sistema:

```javascript
export const options = {
  stages: [
    { duration: '30s', target: 5 },   // Calentamiento lento
    { duration: '3m', target: 10 },   // Carga sostenida (más realista)
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<10000'], // 10s es más realista
    http_req_failed: ['rate<0.05'],     // 5% tolerancia por cold starts
  },
};

export default function () {
  const res = http.get(url);

  check(res, {
    'status OK': (r) => r.status === 200,
    'latencia < 8s': (r) => r.timings.duration < 8000, // Más realista
  });

  sleep(5 + Math.random() * 5); // 5-10s entre requests (más humano)
}
```

### Opción B: Prueba de Capacidad Máxima
Si quieres encontrar el punto de quiebre:

```javascript
export const options = {
  stages: [
    { duration: '1m', target: 5 },
    { duration: '2m', target: 10 },
    { duration: '2m', target: 20 },
    { duration: '2m', target: 30 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<15000'], // 15s límite superior
    http_req_failed: ['rate<0.10'],      // 10% tolerancia
  },
};
```

### Opción C: Prueba de Smoke Test (Validación Básica)
Para CI/CD, verifica que funciona:

```javascript
export const options = {
  vus: 3,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<12000'],
    http_req_failed: ['rate<0.05'],
  },
};
```

## Métricas de Éxito Realistas

Para una operación de exportación de DB:

| Métrica | Valor Aceptable | Valor Bueno | Valor Excelente |
|---------|----------------|-------------|-----------------|
| p95 latencia | < 10s | < 7s | < 5s |
| p99 latencia | < 15s | < 10s | < 8s |
| Error rate | < 5% | < 2% | < 1% |
| Throughput sostenido | 5 req/s | 10 req/s | 20 req/s |

## Conclusión

Tu script actual está diseñado para APIs ligeras. Para operaciones pesadas como exportación:
1. Aumentar sleep a 5-10s
2. Reducir concurrencia a 5-20 VUs
3. Ajustar thresholds a realidad (p95 < 10s)
4. Considerar si necesitas provisioned concurrency en Lambda
