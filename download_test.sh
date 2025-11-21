#!/bin/bash
# Script para probar la descarga del archivo SQLite

TENANT_ID=64127
API_URL="https://1h1bwgaoz1.execute-api.us-west-2.amazonaws.com/dev/export/${TENANT_ID}"
OUTPUT_FILE="tenant_${TENANT_ID}.sqlite"

echo "Descargando SQLite para tenant ${TENANT_ID}..."
curl -v "${API_URL}" --output "${OUTPUT_FILE}"

echo ""
echo "Verificando archivo descargado..."
if [ -f "${OUTPUT_FILE}" ]; then
    FILE_TYPE=$(file "${OUTPUT_FILE}")
    FILE_SIZE=$(ls -lh "${OUTPUT_FILE}" | awk '{print $5}')

    echo "Archivo: ${OUTPUT_FILE}"
    echo "Tamaño: ${FILE_SIZE}"
    echo "Tipo: ${FILE_TYPE}"

    if echo "${FILE_TYPE}" | grep -q "SQLite"; then
        echo "✅ Archivo SQLite válido!"
    else
        echo "❌ El archivo NO es un SQLite válido"
        echo "Contenido de los primeros bytes:"
        head -c 100 "${OUTPUT_FILE}" | xxd
    fi
else
    echo "❌ No se pudo descargar el archivo"
fi
