# Rivalscope web app

Next.js (App Router) + Tailwind v4 + shadcn/ui. See the [project README](../README.md) for the
whole picture.

```bash
npm ci
npm run dev        # http://localhost:3000, proxies /api to the backend on :8000
npm run lint && npm run typecheck
npm run build      # static export to ./out, served by the FastAPI backend in production
```

- `src/lib/api.ts` — the only code that calls the backend; errors carry a stable `code`.
- `src/lib/queries.ts` — data hooks (TanStack Query), including polling of live agent runs.
- `src/lib/types.ts` — mirrors `backend/api/schemas.py`; update both together.
- `src/components/providers.tsx` — one error policy: demo writes open "Request access",
  everything else becomes a toast.
- Pages read ids from the query string (`/product/?id=1`) because the app is a static export.
