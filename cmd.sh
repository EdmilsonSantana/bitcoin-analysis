#!/bin/bash

echo "Executando ${PYTHON_FILE}.py..."

exec python -u /app/${PYTHON_FILE}.py
