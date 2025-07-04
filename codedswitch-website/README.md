# CodedSwitch Website

A modern, beautiful website for CodedSwitch with payment integration and secure download functionality.

## Features

- 🎨 Modern, responsive design
- 💳 Stripe payment integration
- 🔒 Secure download system
- 📱 Mobile-friendly interface
- ⚡ Fast React frontend
- 🚀 Node.js/Express backend

## Project Structure

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
└── README.md
```

## Quick Start

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Stripe account (for payments)

### 1. Setup Backend

```bash
cd backend

# Install dependencies
npm install

# Copy environment file
cp env.example .env

# Edit .env with your Stripe keys
# Get your keys from: https://dashboard.stripe.com/apikeys
```

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
npm start
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The website will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## Configuration

### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard
3. Update the `.env` file in the backend folder:

```env
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
PORT=5000
```

### Customization

#### Update Download Link

In `backend/server.js`, update the download link:

```javascript
// Line ~75
downloadLink: 'https://your-actual-download-link.com/codedswitch.zip'
```

#### Update Pricing

In `backend/server.js`, modify the pricing plans:

```javascript
// Lines ~80-105
plans: [
  {
    id: 'basic',
    name: 'Basic',
    price: 9.99,
    features: [
      'Full CodedSwitch Access',
      'Basic Support',
      '30-day Money Back Guarantee'
    ]
  }
]
```

#### Update Contact Information

In `frontend/src/App.jsx`, update the contact details:

```javascript
// Lines ~200-210
<span>support@codedswitch.com</span>
```

## Deployment

### Frontend (Vercel/Netlify)

1. Push your code to GitHub
2. Connect your repository to Vercel or Netlify
3. Set build command: `npm run build`
4. Set output directory: `dist`

### Backend (Railway/Heroku)

1. Push your code to GitHub
2. Connect your repository to Railway or Heroku
3. Set environment variables:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `PORT`

### Environment Variables

Make sure to set these in your production environment:

```env
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
PORT=5000
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/pricing` - Get pricing plans
- `POST /api/create-payment-intent` - Create Stripe payment intent
- `POST /api/payment-success` - Handle successful payment
- `GET /api/download` - Secure download endpoint

## Security Features

- CORS enabled for frontend-backend communication
- Payment verification with Stripe
- Secure download links (payment-gated)
- Environment variable protection

## Support

For support or questions:
- Email: support@codedswitch.com
- Create an issue on GitHub

## License

This project is proprietary software. All rights reserved. 