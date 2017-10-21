#!/bin/bash

echo "Executando ${PYTHON_FILE}.py..."

exec python -u /server/${PYTHON_FILE}.py
