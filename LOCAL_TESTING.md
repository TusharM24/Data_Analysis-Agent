# Local Testing Guide

This guide shows you how to test your application locally before deploying to production.

## Quick Start (Development Mode)

### 1. Start Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Make sure .env file exists with your GROQ_API_KEY
# If not, copy from env.sample:
# cp env.sample .env
# Then edit .env and add your GROQ_API_KEY

# Start the backend server
python run.py
```

Backend will run at: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Start Frontend (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

Frontend will run at: `http://localhost:5173`

### 3. Test the Application

1. Open browser to `http://localhost:5173`
2. Upload a CSV file
3. Ask questions like:
   - "Show me the first 5 rows"
   - "What are the column names?"
   - "Create a histogram of column_name"
4. Verify plots are displayed correctly

## Testing Production Build Locally

This simulates how your app will behave in production.

### Option 1: Test Frontend Build Only

```bash
cd frontend

# Create a local environment file (optional)
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Build the production version
npm run build

# Preview the production build
npm run preview
```

Access at: `http://localhost:4173`

The preview will use the production build but connect to your local backend.

### Option 2: Test with Docker (Full Production Simulation)

```bash
# From project root directory
cd "EDA Agent"

# Set your Groq API key
export GROQ_API_KEY=your_groq_api_key_here

# Build and start both services
docker-compose up --build
```

Access at: `http://localhost:3000`

This is the closest to production environment.

To stop:
```bash
docker-compose down
```

## Testing with Environment Variables

### Test Frontend with Different Backend URLs

Create different .env files for different scenarios:

**Testing with local backend:**
```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000
```

**Testing with deployed backend:**
```bash
# frontend/.env.local
VITE_API_URL=https://your-backend.onrender.com
```

Then run:
```bash
cd frontend
npm run dev
```

### Test Backend with Different CORS Settings

Edit `backend/.env`:

**For local frontend:**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**For deployed frontend:**
```bash
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

Then restart backend:
```bash
cd backend
python run.py
```

## Verify Everything Works

### ✅ Backend Checklist

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","groq_configured":true}`

2. **API Documentation**
   - Visit: `http://localhost:8000/docs`
   - Should see interactive API documentation

3. **CORS Headers**
   - Open browser DevTools → Network tab
   - Make a request from frontend
   - Check response headers include `Access-Control-Allow-Origin`

### ✅ Frontend Checklist

1. **File Upload**
   - Click "Upload Dataset"
   - Select a CSV file
   - Verify success message
   - Check dataset summary appears

2. **Chat Functionality**
   - Type a message: "Show me the first 5 rows"
   - Verify response appears
   - Check code is displayed
   - Verify no errors in browser console

3. **Visualizations**
   - Ask: "Create a histogram of column_name"
   - Verify plot appears in gallery
   - Check plot loads correctly
   - Verify plot can be viewed full-screen

4. **Session Management**
   - Refresh the page
   - Verify chat history persists
   - Check dataset info still shows

### ✅ Integration Checklist

1. **No Console Errors**
   - Open browser DevTools → Console
   - Should see no red errors
   - Some warnings are OK

2. **No Network Errors**
   - Open browser DevTools → Network tab
   - All requests should return 200/201
   - No CORS errors
   - Check request/response payloads

3. **File Paths**
   - Plots should load from `/api/plots/...`
   - Upload should work without file path errors

## Common Issues and Solutions

### Issue: "Connection refused" or "Network Error"

**Symptom**: Frontend can't connect to backend

**Solutions**:
1. Make sure backend is running (`python run.py`)
2. Check backend URL in `.env.local` matches where backend is running
3. Verify firewall isn't blocking port 8000

### Issue: "CORS policy" error

**Symptom**: Browser console shows CORS error

**Solutions**:
1. Check backend `.env` has correct `CORS_ORIGINS`
2. Make sure origins include `http://` or `https://`
3. Restart backend after changing CORS settings
4. Verify no trailing slashes in URLs

### Issue: "GROQ_API_KEY not set"

**Symptom**: Backend shows warning on startup

**Solutions**:
1. Create `backend/.env` file
2. Add: `GROQ_API_KEY=your_actual_key`
3. Restart backend

### Issue: Plots not loading

**Symptom**: Plot images show broken image icon

**Solutions**:
1. Check `backend/data/plots/` directory exists
2. Verify backend can write to that directory
3. Check plot URLs in browser DevTools → Network
4. Make sure `VITE_API_URL` is set correctly

### Issue: "Module not found" errors

**Symptom**: Import errors in backend or frontend

**Solutions**:

**Backend**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port already in use

**Symptom**: "Address already in use" error

**Solutions**:

**Kill process on port 8000 (backend)**:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Kill process on port 5173 (frontend)**:
```bash
# macOS/Linux
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

## Testing Different Scenarios

### Test with Large Files

```bash
# Create a large test CSV file (optional)
# Test upload with 10MB, 20MB files
# Verify MAX_FILE_SIZE setting works
```

### Test Error Handling

1. **Upload invalid file**: Try uploading a .txt file
2. **Ask unclear question**: "Show me something"
3. **Request invalid column**: "Plot column that doesn't exist"
4. **Network interruption**: Stop backend mid-request

### Test Session Persistence

1. Upload a file and chat
2. Close browser tab
3. Open new tab to same URL
4. Verify session persists

### Test Multiple Sessions

1. Open app in two different browser tabs
2. Upload different files in each
3. Verify sessions don't interfere with each other

## Performance Testing

### Check Response Times

- File upload: Should complete in < 5 seconds
- Simple query: Should respond in < 3 seconds
- Plot generation: Should complete in < 5 seconds

### Monitor Resource Usage

**Backend**:
```bash
# Check memory usage
ps aux | grep python

# Check CPU usage
top | grep python
```

**Frontend**:
- Open DevTools → Performance tab
- Record while using the app
- Check for memory leaks or slow operations

## Before Pushing to Production

Final checklist before deploying:

- [ ] All tests pass locally
- [ ] No console errors
- [ ] No CORS errors
- [ ] File upload works
- [ ] Chat works
- [ ] Plots load correctly
- [ ] Session persists after refresh
- [ ] Production build works (`npm run build && npm run preview`)
- [ ] Docker build works (if using Docker)
- [ ] Environment variables are documented
- [ ] `.env` files are NOT committed to git
- [ ] README is updated if needed

## Getting Help

If you're stuck:
1. Check the error message in browser console
2. Check backend logs in terminal
3. Verify environment variables are set correctly
4. Try the Docker setup to isolate issues
5. Review the DEPLOYMENT.md guide

---

**Ready to deploy?** See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment instructions.

