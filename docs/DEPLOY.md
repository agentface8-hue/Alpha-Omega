# Deploy Alpha-Omega

## 1. Push to GitHub

```bash
git add .
git commit -m "Your message"
git push origin main
```

## 2. Deploy backend (Render.com)

1. Go to [render.com](https://render.com), sign in with GitHub.
2. **New** → **Web Service**.
3. Connect repo `ipurches/Alpha-Omega-System` (or your fork).
4. Settings:
   - **Root Directory:** leave blank (repo root).
   - **Runtime:** Python 3.
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. **Environment:** Add `GOOGLE_API_KEY` (and optionally others) if you want real AI agents; otherwise the app uses demo mode.
6. Deploy. Note the URL, e.g. `https://alpha-omega-api.onrender.com`.

## 3. Deploy frontend (Vercel)

1. Go to [vercel.com](https://vercel.com), sign in with GitHub.
2. **Add New** → **Project** → import `Alpha-Omega-System`.
3. Settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
   - **Build command:** `npm run build`
   - **Output Directory:** `dist`
4. **Environment Variables:** Add `VITE_API_URL` = your backend URL (e.g. `https://alpha-omega-api.onrender.com`) — no trailing slash.
5. Deploy. Your app will be at `https://your-project.vercel.app`.

## 4. Optional: Backend only (no frontend)

Run the API locally and point the frontend at it:

- Backend: deploy to Render as above.
- Local frontend: create `frontend/.env.local` with `VITE_API_URL=https://your-backend.onrender.com`, then `npm run dev`.

## Notes

- Render free tier spins down after inactivity; first request may be slow.
- Keep `.env` and secrets out of the repo; set them in Render/Vercel dashboards.
