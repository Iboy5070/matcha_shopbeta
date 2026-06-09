/**
 * Cloudflare Worker — auto-wakes Render before serving (no manual reload).
 *
 * Deploy (free):
 *   1. https://dash.cloudflare.com → Workers → Create
 *   2. Paste this file, Save and Deploy
 *   3. Share your *.workers.dev URL (or add custom route)
 *
 * Env var in Worker settings:
 *   ORIGIN = https://matcha-shopbeta.onrender.com
 */

const LOADING_HTML = `<!DOCTYPE html>
<html lang="lo"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MATCHAZUKI — ກຳລັງເປີດ...</title>
<style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:system-ui,sans-serif;background:#f7f5f0}
.card{text-align:center;padding:2rem;max-width:360px}.spin{width:36px;height:36px;margin:1rem auto;border:3px solid #e8e8e8;border-top-color:#2d5a3d;border-radius:50%;animation:s .8s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}</style></head>
<body><div class="card"><h1 style="color:#2d5a3d">MATCHAZUKI</h1><div class="spin"></div><p>ກຳລັງເປີດຮ້ານ... ລໍອັດຕະໂນມັດ</p></div>
<script>setTimeout(function(){location.reload()},8000)</script></body></html>`;

async function wakeOrigin(origin, maxWaitMs) {
  const deadline = Date.now() + maxWaitMs;
  while (Date.now() < deadline) {
    try {
      const r = await fetch(origin + "/healthz/", { cf: { cacheTtl: 0, cacheEverything: false } });
      if (r.ok) return true;
    } catch (e) {}
    await new Promise((r) => setTimeout(r, 2500));
  }
  return false;
}

export default {
  async fetch(request, env) {
    const origin = (env.ORIGIN || "https://matcha-shopbeta.onrender.com").replace(/\/$/, "");
    const url = new URL(request.url);
    const target = origin + url.pathname + url.search;

    if (url.pathname === "/healthz" || url.pathname === "/healthz/") {
      return fetch(origin + url.pathname, request);
    }

    let response;
    try {
      response = await fetch(target, {
        method: request.method,
        headers: request.headers,
        body: request.method !== "GET" && request.method !== "HEAD" ? request.body : undefined,
        redirect: "manual",
      });
    } catch (e) {
      response = null;
    }

    if (!response || response.status >= 502) {
      const ok = await wakeOrigin(origin, 90000);
      if (ok) {
        try {
          return await fetch(target, {
            method: request.method,
            headers: request.headers,
            body: request.method !== "GET" && request.method !== "HEAD" ? request.body : undefined,
            redirect: "follow",
          });
        } catch (e) {}
      }
      return new Response(LOADING_HTML, {
        status: 503,
        headers: { "Content-Type": "text/html; charset=utf-8", "Retry-After": "8" },
      });
    }

    return response;
  },
};
