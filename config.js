/* Desire Agency site config — single file for affiliate URLs.
 *
 * To activate the n8n partner link later, set N8N_AFFILIATE_URL
 * to the official URL from PartnerStack / n8n (one line) and
 * redeploy this file. Leave it empty until that link exists.
 *
 * Do not invent links. Official product URLs are fallbacks only
 * and are not affiliate links.
 */
window.SITE_CONFIG = {
  /* Empty on purpose: the n8n partner application was declined
     on 19 November 2026. Buttons go to the official site. */
  N8N_AFFILIATE_URL: "",

  /* Optional later; still empty. */
  MAKE_AFFILIATE_URL: "",

  /* Official fallbacks — not affiliate links. */
  N8N_OFFICIAL_URL: "https://n8n.io/",
  MAKE_OFFICIAL_URL: "https://www.make.com/",

  /* Site is published; allow indexing. */
  NOINDEX: false
};
