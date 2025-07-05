#!/bin/bash

# Build script for CodedSwitch Web Deployment
# This ensures only Node.js dependencies are installed

echo "🚀 Starting CodedSwitch Web Build..."

# Navigate to backend and install dependencies
echo "📦 Installing backend dependencies..."
cd backend
npm install --production

# Navigate to frontend and install dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

# Build the frontend
echo "🔨 Building frontend..."
npm run build

echo "✅ Build completed successfully!" 