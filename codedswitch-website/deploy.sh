#!/bin/bash

# CodedSwitch Web Deployment Script
# This script ensures only Node.js dependencies are installed

set -e  # Exit on any error

echo "🚀 Starting CodedSwitch Web Deployment..."

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Remove any Python-related files that might confuse Render
echo "🧹 Cleaning up Python files..."
find . -name "*.py" -type f -delete 2>/dev/null || true
find . -name "requirements*.txt" -type f -delete 2>/dev/null || true
find . -name "setup.py" -type f -delete 2>/dev/null || true
find . -name "pyproject.toml" -type f -delete 2>/dev/null || true

# Build backend
echo "📦 Building backend..."
cd backend
npm install --production
echo "✅ Backend dependencies installed"

# Build frontend
echo "📦 Building frontend..."
cd ../frontend
npm install
npm run build
echo "✅ Frontend built successfully"

echo "🎉 CodedSwitch deployment build completed!" 