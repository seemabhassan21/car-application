#!/bin/bash
set -e

echo "Starting FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload