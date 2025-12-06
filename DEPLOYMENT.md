# Deployment Guide

This guide will help you deploy the EDA Agent application to production.

## Prerequisites

- GitHub account
- Groq API key (get one at [console.groq.com](https://console.groq.com/))
- Accounts on your chosen deployment platforms (Render, Vercel, etc.)

## Architecture

The application consists of two separate services:
1. **Backend** (FastAPI/Python) - Deployed separately
2. **Frontend** (React/Vite) - Deployed separately

They communicate via HTTP API calls.

## Deployment Options

### Option 1: Backend on Render + Frontend on Vercel (Recommended)

This is the easiest and most performant option for most use cases.

#### Deploy Backend to Render

1. **Create a New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `eda-agent-backend` (or your choice)
     - **Region**: Choose closest to your users
     - **Branch**: `production` (or `main`)
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Set Environment Variables**
   ```
   GROQ_API_KEY=your_actual_groq_api_key
   GROQ_MODEL=llama-3.3-70b-versatile
   DEBUG=false
   CORS_ORIGINS=https://your-frontend.vercel.app
   EXECUTION_TIMEOUT=30
   MAX_FILE_SIZE=52428800
   ```
   
   **Important**: Leave `CORS_ORIGINS` as a placeholder for now. You'll update it after deploying the frontend.

3. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL (e.g., `https://eda-agent-backend.onrender.com`)

#### Deploy Frontend to Vercel

1. **Create a New Project**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`

2. **Set Environment Variables**
   - In project settings → Environment Variables
   - Add:
     ```
     VITE_API_URL=https://eda-agent-backend.onrender.com
     ```
   - Replace with your actual Render backend URL

3. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note your frontend URL (e.g., `https://eda-agent.vercel.app`)

4. **Update Backend CORS**
   - Go back to Render
   - Update the `CORS_ORIGINS` environment variable:
     ```
     CORS_ORIGINS=https://eda-agent.vercel.app
     ```
   - Replace with your actual Vercel URL
   - Backend will automatically redeploy

### Option 2: Both on Render

#### Deploy Backend (Same as Option 1)

Follow the backend deployment steps from Option 1.

#### Deploy Frontend on Render

1. **Create a New Static Site**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Static Site"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `eda-agent-frontend`
     - **Branch**: `production`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Publish Directory**: `dist`

2. **Set Environment Variables**
   - Add environment variable:
     ```
     VITE_API_URL=https://eda-agent-backend.onrender.com
     ```

3. **Deploy and Update CORS**
   - Deploy the frontend
   - Note your frontend URL (e.g., `https://eda-agent.onrender.com`)
   - Update backend's `CORS_ORIGINS` with this URL

### Option 3: Using Docker on Railway/Fly.io

Both services can be deployed together using Docker Compose or separately.

#### Railway Deployment

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Create project: `railway init`
4. Add environment variables via Railway dashboard
5. Deploy: `railway up`

#### Fly.io Deployment

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Create apps for backend and frontend
4. Deploy with `fly deploy`

## Local Testing Before Deployment

### Test Backend Locally

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Make sure .env has your GROQ_API_KEY
python run.py

# Test at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Test Frontend with Local Backend

```bash
cd frontend

# Create .env.local file with:
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev

# Access at http://localhost:5173
```

### Test Frontend Build (Production Mode)

```bash
cd frontend

# Build the production version
npm run build

# Preview the production build
npm run preview

# Access at http://localhost:4173
```

### Test with Production-like URLs

To test the full deployment flow locally:

1. **Run backend on a specific port**:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Update frontend .env.local**:
   ```bash
   echo "VITE_API_URL=http://localhost:8000" > frontend/.env.local
   ```

3. **Run frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

4. **Test all features**:
   - Upload a CSV file
   - Ask questions about the data
   - Generate visualizations
   - Verify plots load correctly
   - Check browser console for errors

## Important Considerations

### File Storage

**Issue**: Render's free tier has ephemeral storage (files disappear on restart).

**Solutions**:
1. **Use Render Disk** (paid): $0.25/GB/month
   - In Render dashboard → Add Disk
   - Mount path: `/app/data`
   
2. **Use Cloud Storage** (recommended for scale):
   - AWS S3
   - Cloudinary
   - Google Cloud Storage
   
3. **Accept Ephemeral** (for demo/testing):
   - Files will be deleted on each deploy/restart
   - Good for testing and demonstrations

### Environment Variables Checklist

**Backend (Required)**:
- ✅ `GROQ_API_KEY` - Your Groq API key
- ✅ `CORS_ORIGINS` - Frontend URL(s), comma-separated

**Backend (Optional)**:
- `GROQ_MODEL` - Default: `llama-3.3-70b-versatile`
- `DEBUG` - Set to `false` in production
- `EXECUTION_TIMEOUT` - Default: 30 seconds
- `MAX_FILE_SIZE` - Default: 52428800 (50MB)

**Frontend (Required)**:
- ✅ `VITE_API_URL` - Your deployed backend URL

### Security Checklist

Before deploying:
- [ ] Set `DEBUG=false` in production
- [ ] Never commit your `.env` file with real API keys
- [ ] Use environment variables for all secrets
- [ ] Set appropriate CORS origins (not `*`)
- [ ] Review the code sandbox security settings
- [ ] Consider rate limiting for production
- [ ] Set up monitoring and error tracking

### Testing After Deployment

1. **Test file upload**: Upload a CSV file
2. **Test chat**: Ask a simple question like "Show me the first 5 rows"
3. **Test visualization**: Request a plot
4. **Test error handling**: Try uploading an invalid file
5. **Check CORS**: Verify no CORS errors in browser console
6. **Test on mobile**: Check responsive design
7. **Test session persistence**: Refresh page and verify session persists

### Troubleshooting

**CORS Errors**:
```
Access to XMLHttpRequest blocked by CORS policy
```
- Solution: Update backend `CORS_ORIGINS` with exact frontend URL (including https://)

**Backend Not Responding**:
- Check Render/Vercel logs
- Verify `GROQ_API_KEY` is set correctly
- Check start command is correct
- Verify PORT environment variable usage

**Frontend Can't Connect to Backend**:
- Verify `VITE_API_URL` is set correctly
- Check backend is actually running
- Test backend URL directly in browser
- Check browser console for errors

**Plots Not Loading**:
- Verify plot URLs are being generated correctly
- Check CORS settings include plot endpoints
- Verify backend storage directory exists

## Updating Your Deployment

### Update Backend

```bash
# Make changes locally
git add .
git commit -m "Update backend feature"
git push origin production

# Render/Railway will auto-deploy
```

### Update Frontend

```bash
# Make changes locally
git add .
git commit -m "Update frontend feature"
git push origin production

# Vercel/Render will auto-deploy
```

### Manual Redeploy

Most platforms support manual redeployment from their dashboard if auto-deploy is disabled.

## Cost Estimates (as of 2024)

### Free Tier Limits

**Render Free**:
- Backend: Free (sleeps after 15min inactivity, 750 hrs/month)
- Frontend: Free (100GB bandwidth/month)

**Vercel Free**:
- Frontend: Free (100GB bandwidth, unlimited requests)

**Groq API**:
- Free tier available with rate limits
- Check [groq.com/pricing](https://groq.com/pricing) for current limits

### Paid Tier (for production use)

- Render Starter: $7/month (always on)
- Vercel Pro: $20/month (advanced features)
- Render Disk: $0.25/GB/month (persistent storage)

## Monitoring and Logs

- **Render**: Dashboard → Service → Logs tab
- **Vercel**: Dashboard → Project → Deployments → View Function Logs
- **Railway**: Dashboard → Project → Deployments → Logs

Set up alerts for errors and downtime on your chosen platform.

## Next Steps

After successful deployment:

1. Test all features thoroughly
2. Set up custom domain (optional)
3. Configure SSL/HTTPS (usually automatic)
4. Set up monitoring and alerts
5. Consider adding analytics
6. Plan for scaling if needed

## Support

If you run into issues:
- Check platform documentation (Render, Vercel, etc.)
- Review application logs
- Verify all environment variables are set correctly
- Test locally first to isolate the issue

---

**Happy Deploying! 🚀**

