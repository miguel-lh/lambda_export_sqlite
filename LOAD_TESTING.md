# Guía de Pruebas de Carga

## 🎯 Problema con tu script original

Tu script `stress-test.js` tiene estos problemas:

### ❌ Lo que estaba mal:
1. **Sleep muy corto (0.5s)**: Cada VU hacía requests cada medio segundo
   - Con 100 VUs = hasta 200 req/s
   - Para operación que toma 3-5s = sobrecarga innecesaria

2. **Thresholds irrealistas**: `p(95)<800ms` para exportar una DB completa
   - Realidad: ~5.6s (7x más lento)
   - Exportar DB + crear SQLite + base64 no puede ser <800ms

3. **Tipo de prueba incorrecta**:
   - Tu script es para APIs REST ligeras (GET /users)
   - Tu endpoint es una operación batch pesada

## 📋 Scripts Mejorados

He creado 3 scripts diferentes para distintos propósitos:

### 1. `stress-test-improved.js` ⭐ RECOMENDADO

**Cuándo usar**: Prueba de carga realista y sostenida

**Características**:
- Max 15 VUs concurrentes (realista)
- Sleep 3-7s entre requests (patrón humano)
- Thresholds realistas: p95<10s
- Métricas detalladas

**Ejecutar**:
```bash
k6 run stress-test-improved.js
```

**Resultado esperado**:
- ✅ Debería pasar todos los thresholds
- ✅ Success rate > 95%
- ✅ p95 < 10s

---

### 2. `stress-test-spike.js` 🔥 SPIKE TEST

**Cuándo usar**: Encontrar el punto de quiebre del sistema

**Características**:
- Aumenta gradualmente de 5 a 40 VUs
- Más permisivo con errores (tolera 15%)
- Objetivo: Ver dónde empieza a fallar

**Ejecutar**:
```bash
k6 run stress-test-spike.js
```

**Qué buscar**:
- ¿En qué fase empiezan los errores? (10 VUs? 20? 30?)
- ¿Cuál es la latencia máxima sostenible?
- ¿Se recupera el sistema después del pico?

---

### 3. `stress-test-smoke.js` 🧪 SMOKE TEST

**Cuándo usar**: Validación rápida en CI/CD

**Características**:
- Solo 3 VUs
- 1 minuto de duración
- Verifica funcionalidad básica

**Ejecutar**:
```bash
k6 run stress-test-smoke.js
```

**Para CI/CD**:
```bash
# En tu pipeline
k6 run stress-test-smoke.js --quiet
if [ $? -eq 0 ]; then
  echo "✅ Smoke test passed - safe to deploy"
else
  echo "❌ Smoke test failed - DO NOT DEPLOY"
  exit 1
fi
```

---

## 📊 Métricas de Éxito Realistas

Para una operación de **exportación completa de DB**:

| Escenario | VUs | Throughput | p95 Latencia | Error Rate |
|-----------|-----|-----------|--------------|------------|
| **Bajo** | 5 | 3-5 req/s | < 8s | < 2% |
| **Medio** | 10 | 5-8 req/s | < 10s | < 5% |
| **Alto** | 20 | 8-12 req/s | < 15s | < 10% |
| **Pico** | 30+ | ??? | ??? | ??? |

## 🎯 Comparación: Antes vs Después

### Tu script original:
```javascript
stages: [
  { duration: '30s', target: 10 },
  { duration: '1m', target: 50 },   // ❌ Demasiado agresivo
  { duration: '1m', target: 100 },  // ❌ Muy agresivo para export
],
sleep(0.5);  // ❌ Demasiado rápido
thresholds: {
  http_req_duration: ['p(95)<800'],  // ❌ Imposible para export DB
}
```

### Script mejorado:
```javascript
stages: [
  { duration: '30s', target: 3 },
  { duration: '1m', target: 5 },    // ✅ Realista
  { duration: '2m', target: 10 },   // ✅ Carga media sostenible
  { duration: '1m', target: 15 },   // ✅ Pico controlado
],
sleep(3 + Math.random() * 4);  // ✅ 3-7s (humano)
thresholds: {
  http_req_duration: ['p(95)<10000'], // ✅ Realista (10s)
}
```

## 🚀 Próximos Pasos

1. **Ejecuta el smoke test primero**:
   ```bash
   k6 run stress-test-smoke.js
   ```
   Si falla → Hay problema básico

2. **Luego el test mejorado**:
   ```bash
   k6 run stress-test-improved.js
   ```
   Debería pasar todos los thresholds

3. **Finalmente el spike test** (opcional):
   ```bash
   k6 run stress-test-spike.js
   ```
   Para saber dónde está el límite

## 🔍 Análisis de Resultados

### Si el test PASA:
```
✓ http_req_duration...: avg=5.2s  p(95)=8.3s  p(99)=9.8s
✓ http_req_failed.....: 0.02%
✓ export_success_rate.: 98.5%
```
→ **Sistema funciona correctamente para carga esperada**

### Si el test FALLA:
```
✗ http_req_duration...: avg=12.3s  p(95)=18.5s  p(99)=25.1s
✗ http_req_failed.....: 8.2%
✗ export_success_rate.: 89.3%
```
→ **Necesitas optimizaciones** (ver stress-test-analysis.md)

## 💡 Optimizaciones Sugeridas

Si los tests fallan, implementa en este orden:

1. **Connection pooling PostgreSQL** → Mayor impacto
2. **Aumentar Lambda memory a 3008MB** → Más CPU
3. **RDS Proxy** → Mejor manejo de conexiones
4. **Provisioned Concurrency** → Eliminar cold starts
5. **Compresión gzip** → Reducir payload

Ver `stress-test-analysis.md` para detalles.
