# Deployment Guide

This guide covers deploying the AI Email Agent to production using free-tier services.

## Overview

| Service | Purpose | Cost |
|---------|---------|------|
| Render | Backend hosting | Free ($0) |
| GitHub Pages | Frontend hosting | Free ($0) |
| Groq | AI/LLM API | Free (1M tokens/day) |

**Total Cost: $0**

---

## Prerequisites

Before deploying, ensure you have:

1. **GitHub account** - https://github.com
2. **Groq API key** - Get free at https://console.groq.com/
3. **Code pushed to GitHub**

---

## Step 1: Deploy Backend to Render

### 1.1 Sign Up / Log In

1. Go to https://dashboard.render.com/
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### 1.2 Create New Web Service

1. Click **+ New** button
2. Select **Web Service**
3. Find and select your repository: `AI-email_agent`
4. Click **Connect**

### 1.3 Configure Service

Fill in the following:

| Field | Value |
|-------|-------|
| **Name** | `ai-email-agent` (or your preferred name) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api_server:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### 1.4 Add Environment Variables

Click **Advanced** button, then add:

| Key | Value |
|-----|-------|
| `AI_PROVIDER` | `groq` |
| `MODEL_NAME` | `llama3-8b-8192` |
| `GROQ_API_KEY` | `your_actual_groq_api_key` |
| `FRONTEND_URL` | `https://yourusername.github.io` |

Replace `your_actual_groq_api_key` with your key from https://console.groq.com/

### 1.5 Create Service

Click **Create Web Service**

Render will:
1. Clone your repository
2. Install dependencies
3. Build and deploy
4. Provide a URL like `https://ai-email-agent-xxx.onrender.com`

**Note:** First deployment takes 2-3 minutes.

### 1.6 Verify Backend

1. Wait for "Your service is live" message
2. Click the provided URL
3. You should see:
   ```json
   {"message": "AI Email Agent API", "version": "1.0.0"}
   ```

4. Test API docs at `https://your-url.onrender.com/docs`

---

## Step 2: Setup GitHub Pages

### 2.1 Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Pages** in left sidebar
4. Under **Build and deployment**:
   - Source: Select **GitHub Actions**
5. Click **Save**

### 2.2 Add Backend URL Secret

1. In Settings, click **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add secret:
   - **Name**: `API_URL`
   - **Value**: Your Render backend URL (e.g., `https://ai-email-agent-xxx.onrender.com`)
4. Click **Add secret**

---

## Step 3: Deploy Frontend

### 3.1 Trigger Deployment

1. Go to **Actions** tab in your repository
2. Click **Deploy Frontend to GitHub Pages**
3. Click **Run workflow** → **Run workflow**

### 3.2 Wait for Deployment

Deployment takes 2-3 minutes. You'll see:
- Build job running
- Deploy job running
- Green checkmark when complete

### 3.3 Access Your Site

Once deployed, your site is available at:
```
https://yourusername.github.io/AI-email_agent/
```

Replace `yourusername` with your actual GitHub username.

---

## Step 4: Verify Everything Works

### 4.1 Check Frontend

1. Open `https://yourusername.github.io/AI-email_agent/`
2. You should see the email agent interface
3. Check that it shows "AI Connected" (not "Demo Mode")

### 4.2 Test Features

1. **Email List**: Should show demo emails
2. **Click Email**: Should show details and AI analysis
3. **Generate Reply**: Should create AI-powered reply
4. **Search**: Should filter emails

### 4.3 Check Backend Logs

If something doesn't work:

1. Go to Render dashboard
2. Click your service
3. Click **Logs** tab
4. Check for errors

---

## Updating Your Deployment

### Update Backend

1. Make code changes
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. Render auto-deploys on push

### Update Frontend

1. Make code changes
2. Commit and push to GitHub
3. GitHub Actions auto-deploys
4. Or manually trigger workflow in Actions tab

---

## Troubleshooting

### Backend Issues

**Service won't start:**
- Check logs in Render dashboard
- Verify environment variables are set
- Check `requirements.txt` has all dependencies

**CORS errors:**
- Verify `FRONTEND_URL` matches your GitHub Pages URL
- Check CORS settings in `api_server.py`

**AI not working:**
- Verify `GROQ_API_KEY` is correct
- Check Groq console for rate limits
- Check backend logs for API errors

### Frontend Issues

**Blank page:**
- Check browser console for errors
- Verify `API_URL` secret is set correctly
- Check that backend is running

**"Demo Mode" shown:**
- Frontend can't connect to backend
- Check `API_URL` secret
- Verify CORS settings
- Check network tab in DevTools

**Styles not loading:**
- Check `vite.config.js` base URL
- Should match your repository name

---

## Custom Domain (Optional)

### Backend Custom Domain

1. In Render dashboard, go to your service
2. Click **Settings** → **Custom Domain**
3. Follow instructions to add your domain

### Frontend Custom Domain

1. Go to repository Settings → Pages
2. Under **Custom domain**, enter your domain
3. Add DNS records as instructed
4. Enable HTTPS

---

## Monitoring

### Render Monitoring

- **Logs**: Real-time application logs
- **Metrics**: CPU, memory usage
- **Events**: Deployment history

### GitHub Actions Monitoring

- **Actions tab**: View workflow runs
- **Status**: Green = success, Red = failed

### Uptime Monitoring (Optional)

Set up free monitoring:
- UptimeRobot: https://uptimerobot.com/
- Pingdom: https://www.pingdom.com/

---

## Scaling (When Needed)

### Current Free Tier Limits

| Service | Limit |
|---------|-------|
| Render | 750 hours/month, sleeps after 15 min idle |
| GitHub Pages | 1GB storage, 100GB bandwidth/month |
| Groq | 1,000,000 tokens/day |

### Upgrade Options

**Render:**
- Starter: $7/month (always on)
- Standard: $25/month (more resources)

**Groq:**
- Pay-as-you-go after free tier
- Very affordable rates

**GitHub Pages:**
- Free tier usually sufficient
- Enterprise available

---

## Security Checklist

Before going to production:

- [ ] API keys in environment variables (not code)
- [ ] CORS configured for your domain only
- [ ] No sensitive data in logs
- [ ] HTTPS enabled (Render/GitHub Pages provide this)
- [ ] Dependencies up to date

---

## Quick Reference

### URLs

| Service | URL |
|---------|-----|
| Backend | `https://ai-email-agent-xxx.onrender.com` |
| Frontend | `https://yourusername.github.io/AI-email_agent/` |
| API Docs | `https://ai-email-agent-xxx.onrender.com/docs` |
| Groq Console | `https://console.groq.com/` |
| Render Dashboard | `https://dashboard.render.com/` |

### Commands

```bash
# Deploy backend (auto on push)
git push origin main

# Deploy frontend manually
git push origin main
# Then trigger workflow in GitHub Actions

# View logs
# Render: Dashboard → Service → Logs
# GitHub: Actions tab → Workflow run
```

---

## Support

If you encounter issues:

1. Check this troubleshooting section
2. Review logs in Render/GitHub
3. Open an issue on GitHub
4. Check documentation in `/docs` folder
