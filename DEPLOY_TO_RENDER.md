# Quick Deploy to Render - Step by Step

## 🚀 Deploy in 10 Minutes!

### Step 1: Push New Files to GitHub

```bash
git add .
git commit -m "Add deployment configuration for Render"
git push
```

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect account"** if not already connected
3. Find and select: **`BhanuAmarapu/main-project`**
4. Click **"Connect"**

### Step 4: Configure Your Service

Fill in these settings:

| Field | Value |
|-------|-------|
| **Name** | `hybrid-ml-dedup` (or your choice) |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Environment** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | **Free** |

### Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these one by one:

```
SECRET_KEY = your-secret-key-change-this-to-something-random
DEBUG = False
USE_S3 = True
AWS_ACCESS_KEY = your-aws-access-key
AWS_SECRET_KEY = your-aws-secret-key
AWS_REGION = us-east-1
S3_BUCKET_NAME = your-bucket-name
```

**Important**: Replace the AWS values with your actual credentials!

### Step 6: Deploy!

1. Click **"Create Web Service"**
2. Wait 3-5 minutes while Render builds and deploys
3. Watch the logs for any errors

### Step 7: Access Your App!

Once deployed, Render will give you a URL like:
```
https://hybrid-ml-dedup.onrender.com
```

Click it to see your live app! 🎉

---

## 🔧 Troubleshooting

### Build Fails?
- Check the build logs in Render dashboard
- Make sure all files are pushed to GitHub
- Verify `requirements.txt` has all dependencies

### App Won't Start?
- Check environment variables are set correctly
- Look at the deployment logs
- Make sure `gunicorn` is in requirements.txt

### Database Errors?
- The app will create SQLite database automatically
- For production, consider upgrading to PostgreSQL

### File Upload Issues?
- Make sure AWS S3 credentials are correct
- Set `USE_S3=True` in environment variables
- Verify S3 bucket exists and has correct permissions

---

## 📊 After Deployment

### Your App URL
Render provides: `https://your-app-name.onrender.com`

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- 750 hours/month free (enough for 24/7 if only one app)

### Keep App Awake (Optional)
Use a service like UptimeRobot to ping your app every 5 minutes:
1. Sign up at https://uptimerobot.com
2. Add your Render URL
3. Set check interval to 5 minutes

---

## 🎯 Alternative: Deploy to PythonAnywhere (Easier)

If Render seems complex, try PythonAnywhere:

1. Go to https://www.pythonanywhere.com
2. Sign up for free account
3. Upload your ZIP file
4. Extract it
5. Configure web app in dashboard
6. Point WSGI to your `app.py`

**Pros**: Simpler, no credit card
**Cons**: Slower, no HTTPS on free tier

---

## ✅ Checklist

Before deploying, make sure:
- [ ] All files pushed to GitHub
- [ ] AWS credentials are valid
- [ ] S3 bucket exists
- [ ] Environment variables ready
- [ ] Render account created

After deploying:
- [ ] App URL works
- [ ] Can login with admin/admin123
- [ ] File upload works
- [ ] Dashboard shows data

---

## 🆘 Need Help?

Check:
- Render logs in dashboard
- GitHub repository is public
- All environment variables are set
- AWS S3 bucket has correct permissions

Good luck! 🚀
