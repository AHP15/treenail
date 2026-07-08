// The site's single absolute URL (D-013, T-019).
//
// Launch is on the Vercel-provided subdomain. Per R-007 this throwaway URL
// must live in exactly ONE place so the later domain-adoption task (T-020) can
// repoint the origin — and with it every canonical and Open Graph URL, which
// all resolve against `metadataBase = new URL(SITE_URL)` — by editing this one
// line and adding the 301 redirect map.
//
// Do NOT hardcode this string into README, the npm package `homepage`, or any
// other durable external surface: those reference the project through the
// stable GitHub repo link instead, so the throwaway subdomain never propagates
// into places that outlive it (R-007). Internally, link with relative paths
// (`/docs`, `/contact`); only absolute-URL needs (canonical, OG) go through
// this constant.
export const SITE_URL = 'https://treenail.vercel.app';
