# 🚀 Railway Deployment Guide

## Pre-Deployment Checklist

### ✅ Files Created
- [x] `Procfile` - Tells Railway how to run the app
- [x] `railway.json` - Railway configuration
- [x] `railway.env` - Environment variables template
- [x] Updated `app.py` - Now supports Railway's port configuration

### ✅ Code Changes Made
- [x] App now uses `PORT` environment variable (Railway sets this)
- [x] App binds to `0.0.0.0` (required for Railway)
- [x] Debug mode controlled by `FLASK_DEBUG` environment variable

## Railway Deployment Steps

### 1. Create GitHub Repository
- [ ] Go to [GitHub](https://github.com)
- [ ] Click "New repository"
- [ ] Name: `thai-tone-analyzer` (or your preferred name)
- [ ] Make it public (required for free Railway)
- [ ] Initialize with README
- [ ] Create repository

### 2. Push Code to GitHub
```bash
# In your project directory
git init
git add .
git commit -m "Initial commit: Thai tone analyzer app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/thai-tone-analyzer.git
git push -u origin main
```

### 3. Deploy to Railway
- [ ] Go to [Railway](https://railway.app)
- [ ] Sign up with GitHub account
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your `thai-tone-analyzer` repository
- [ ] Railway will automatically detect it's a Python app
- [ ] Click "Deploy"

### 4. Configure Environment Variables
- [ ] In Railway dashboard, go to your project
- [ ] Click on your service
- [ ] Go to "Variables" tab
- [ ] Add these variables:
  - `FLASK_ENV` = `production`
  - `FLASK_DEBUG` = `False`
  - `PORT` = (Railway sets this automatically)

### 5. Test Deployment
- [ ] Railway will provide a URL like `https://your-app-name.railway.app`
- [ ] Visit the URL to test your app
- [ ] Test Thai word analysis
- [ ] Test English translation
- [ ] Test audio functionality

## Post-Deployment

### Custom Domain (Optional)
- [ ] In Railway dashboard, go to "Settings"
- [ ] Click "Domains"
- [ ] Add your custom domain
- [ ] Configure DNS records as instructed

### Monitoring
- [ ] Check Railway logs for any errors
- [ ] Monitor usage in Railway dashboard
- [ ] Set up alerts if needed

## Troubleshooting

### Common Issues
1. **App won't start**: Check Railway logs for Python errors
2. **Port issues**: Ensure app uses `PORT` environment variable
3. **Import errors**: Check `requirements.txt` has all dependencies
4. **Static files**: Ensure templates folder is included

### Railway Logs
- Go to Railway dashboard → Your project → Deployments → View logs
- Look for Python errors or startup issues

## Cost
- **Free tier**: 500 hours/month + $5 credit
- **Usage**: Your app will sleep after inactivity
- **Scaling**: Automatically scales based on traffic

## Next Steps
- [ ] Share your deployed app URL
- [ ] Test with friends/users
- [ ] Monitor performance
- [ ] Consider custom domain
- [ ] Add analytics if needed
