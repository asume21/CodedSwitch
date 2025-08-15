# CodedSwitch Deployment Guide

## Quick Deploy to Render

### 1. GitHub Setup
```bash
git init
git add .
git commit -m "Initial commit - CodedSwitch AI Music Platform"
git branch -M main
git remote add origin https://github.com/yourusername/codedswitch.git
git push -u origin main
```

### 2. Render Deployment

1. Connect your GitHub repository to Render
2. Use the `render.yaml` configuration (auto-detected)
3. Set the following environment variables in Render:

**Required Variables:**
- `GOOGLE_SERVICE_ACCOUNT_KEY` - Your Google Service Account JSON (for 16GB dataset access)
- `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude AI
- `OPENAI_API_KEY` - Your OpenAI API key (optional fallback)

**Optional Variables (for full features):**
- `STRIPE_SECRET_KEY` - Stripe secret key for payments
- `STRIPE_PRICE_ID_BASIC` - Stripe price ID for basic plan
- `STRIPE_PRICE_ID_PRO` - Stripe price ID for pro plan
- `VITE_STRIPE_PUBLIC_KEY` - Stripe publishable key

### 3. Database
- Render will automatically create a PostgreSQL database
- Database tables will be created automatically on first run

## Features Available

### Core AI Music Generation
✅ Beat maker with professional rhythms
✅ Melody composer with chord progressions
✅ Lyric generator with AI assistance
✅ Professional mixing studio with EQ/effects
✅ Real song composition (not random notes)

### Advanced Features
✅ 16,000+ professional audio references for AI training
✅ Google Drive integration for massive dataset processing
✅ Advanced musical arrangement system
✅ Professional mixer with individual track controls
✅ User authentication and subscription system

### Production Ready
✅ Health check endpoint
✅ Error handling and graceful degradation
✅ Scalable architecture with background processing
✅ Real-time audio processing with Web Audio API

## System Requirements
- Node.js 20+
- PostgreSQL database
- Google Drive API access (for dataset)
- AI API keys (Anthropic/OpenAI)

## Performance
- Handles 16,000+ audio files
- Batch processing for large datasets
- Background processing for heavy operations
- Optimized for production deployment

Built with React, Express, PostgreSQL, and Web Audio API.