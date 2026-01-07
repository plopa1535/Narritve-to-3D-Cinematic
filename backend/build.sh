#!/bin/bash

# Render 빌드 스크립트
# 프론트엔드 빌드 후 백엔드에 통합

set -e

echo "=== Installing backend dependencies ==="
pip install -r requirements.txt

echo "=== Installing frontend dependencies ==="
cd ../frontend
npm install

echo "=== Building frontend ==="
npm run build

echo "=== Copying frontend build to backend ==="
cd ../backend
rm -rf static
cp -r ../frontend/dist static

echo "=== Build complete ==="
ls -la static/
