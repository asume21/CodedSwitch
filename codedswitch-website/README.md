# CodedSwitch Web Platform

**Node.js/React Web Application** - This is NOT a Python application.

## 🚨 Important: This is a Node.js Application

This directory contains the **web platform** for CodedSwitch, built with:
- **Frontend**: React + Vite
- **Backend**: Node.js + Express
- **Payments**: Stripe integration

## 🚫 No Python Dependencies

This web deployment does NOT use:
- ❌ Python
- ❌ Pygame
- ❌ Python requirements.txt
- ❌ Python setup.py

## ✅ Node.js Dependencies Only

This deployment uses:
- ✅ Node.js
- ✅ npm
- ✅ React
- ✅ Express

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### 1. Setup Backend
```bash
cd backend
npm install
```

### 2. Setup Frontend
```bash
cd frontend
npm install
```

### 3. Run the Application
```bash
# Terminal 1 - Backend
cd backend
npm start

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🌐 Deployment

This application is designed to deploy on Render as a **Node.js application**.

### Render Configuration
- **Environment**: Node.js
- **Build Command**: `chmod +x deploy.sh && ./deploy.sh`
- **Start Command**: `cd backend && npm start`

## 📁 Project Structure

```
codedswitch-website/
├── frontend/          # React application
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/           # Node.js/Express API
│   ├── server.js
│   ├── env.example
│   └── package.json
├── package.json       # Root Node.js config
├── render.yaml        # Render deployment config
├── deploy.sh          # Deployment script
└── README.md
```

## 🔧 Configuration

### Stripe Setup
1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard
3. Update the `.env` file in the backend folder:

```env
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
PORT=5000
```

## 🚨 Troubleshooting

### If you see pygame errors:
- This is a Node.js application
- Pygame errors indicate Render is using the wrong buildpack
- Ensure `package.json` exists and specifies Node.js
- Check that `render.yaml` is configured correctly

### If build fails:
- Verify Node.js version (>=16.0.0)
- Check that all npm dependencies are installed
- Ensure environment variables are set correctly

## 📞 Support

For support or questions:
- Email: support@codedswitch.com
- Create an issue on GitHub

## License

This project is proprietary software. All rights reserved. 