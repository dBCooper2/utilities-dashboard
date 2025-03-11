# Deploying the Utilities Dashboard Backend to Railway

This guide provides step-by-step instructions for deploying the Utilities Dashboard backend to [Railway](https://railway.app/).

## Prerequisites

1. [Railway account](https://railway.app/) (free tier available)
2. [Railway CLI](https://docs.railway.app/develop/cli) (optional but recommended)
3. Git installed on your local machine
4. GitHub repository containing your project

## Deployment Steps

### 1. Prepare Your Project for Deployment

Ensure your project has:
- ✅ A valid `requirements.txt` file
- ✅ A `Dockerfile` (already included in the project)
- ✅ Environment variables configured in `.env` file

### 2. Push Your Code to GitHub

If your code is not already on GitHub:

```bash
git init
git add .
git commit -m "Initial commit for Railway deployment"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 3. Set Up Railway Project

#### Option A: Via Railway Web Dashboard

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click on "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your GitHub repository
5. Railway will detect your Dockerfile automatically

#### Option B: Via Railway CLI

1. Install Railway CLI if not already installed:
   ```bash
   npm i -g @railway/cli
   ```
   
2. Login to Railway:
   ```bash
   railway login
   ```
   
3. Link your project:
   ```bash
   railway link
   ```
   
4. Deploy your project:
   ```bash
   railway up
   ```

### 4. Configure Environment Variables

Set the following environment variables in the Railway dashboard:

```
DB_HOST=<railway-provided-postgres-host>
DB_PORT=<railway-provided-postgres-port>
DB_NAME=<railway-provided-postgres-name>
DB_USER=<railway-provided-postgres-user>
DB_PASSWORD=<railway-provided-postgres-password>
EIA_API_KEY=<your-eia-api-key>
TIMESCALE_ENABLED=True
CHUNK_TIME_INTERVAL=1 day
FETCH_DAYS_BACK=30
FORECAST_DAYS=7
LOG_LEVEL=INFO
PORT=8000
```

### 5. Add PostgreSQL Database

1. In your Railway project dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will create a PostgreSQL instance and provide connection details
3. Update your environment variables with the Railway-provided PostgreSQL connection details

### 6. Deploy Your Application

If you're using the Railway dashboard, the application will deploy automatically when you push changes to your GitHub repository.

If you're using the CLI:
```bash
railway up
```

### 7. Access Your Application

1. In the Railway dashboard, go to your project
2. Click on your service (the Dockerfile deployment)
3. Click on "Settings" → "Domains"
4. You'll see your application's URL (e.g., https://utilities-dashboard-production.up.railway.app)

## Monitoring and Troubleshooting

- View logs in the Railway dashboard by clicking on your service and selecting the "Logs" tab
- Use the CLI to view logs:
  ```bash
  railway logs
  ```

## Updating Your Deployment

When you make changes to your code:

1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```

2. Railway will automatically redeploy your application if you've connected via GitHub

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Documentation](https://docs.railway.app/develop/cli)
- [Railway PostgreSQL Documentation](https://docs.railway.app/databases/postgresql) 