#!/bin/bash

echo "Executando ${PYTHON_FILE}.py..."

exec python -u /services/${PYTHON_FILE}.py
