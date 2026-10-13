import type { NextConfig } from "next";

// Production: a static export (frontend/out) that the FastAPI backend serves itself,
// so the whole product is one service and API calls are same-origin (no CORS).
// Development: `next dev` proxies /api to the backend on :8000.
// (Next.js doesn't allow rewrites together with `output: "export"`, hence two modes.)
const isDev = process.env.NODE_ENV !== "production";
const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = isDev
  ? {
      async rewrites() {
        return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
      },
    }
  : {
      output: "export",
      trailingSlash: true,
      images: { unoptimized: true },
    };

export default nextConfig;
