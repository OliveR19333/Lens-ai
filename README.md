# LENS AI — FPV Camera Advisor

Point your camera at a scene, pick your rig, get exact D-Log M / GP-Log settings in seconds.

## Deploy to Railway (free, HTTPS, works on iPhone)

### Step 1 — Push to GitHub
1. Go to https://github.com/new and create a new repo called `lens-ai`
2. In terminal, inside this folder:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/lens-ai.git
git push -u origin main
```

### Step 2 — Deploy on Railway
1. Go to https://railway.app and sign up (free)
2. Click **New Project → Deploy from GitHub repo**
3. Select your `lens-ai` repo
4. Railway auto-detects Node.js and deploys — takes ~60 seconds
5. Click **Settings → Networking → Generate Domain**
6. You'll get a URL like `lens-ai-production.up.railway.app`

### Step 3 — Use it anywhere
- Open that URL in Safari on iPhone
- Allow camera when prompted
- Paste your Anthropic API key in the bar at the top
- Pick camera, pick intent, aim, analyze

Free tier gives you 500 hours/month — plenty for field use.

---

## Run Locally (Mac/Windows/Linux)

```bash
npm install
node server.js
```
Open http://localhost:3000

---

## Cameras Supported
- DJI Avata 2 — D-Log M
- DJI Mini 4 Pro — D-Log M
- GoPro Hero 13 — GP-Log

## API Key
Get one at https://console.anthropic.com → API Keys
Your key is saved in your browser locally — never stored on the server.
