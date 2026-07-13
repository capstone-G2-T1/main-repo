# Dalilak Frontend

Next.js 15 frontend for exploring EV brands, vehicle models, bilingual Arabic/English pages, authentication screens, and an AI chat interface.

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3001`.

## Production build

```bash
npm run build
npm start
```

## Docker

```bash
docker build -t dalilak-frontend .
docker run --rm -p 3000:3000 dalilak-frontend
```

Copy `.env.example` to `.env.local` when connecting the frontend to a backend API.
