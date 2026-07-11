// Central brand + contact info (spec §14.4). Override the contact email at build
// time with VITE_CONTACT_EMAIL.
export const BRAND = {
  name: 'TNC GAS Mapping',
  org: "Teaster's Natural Creations",
  tagline: 'Ground & Aerial Services',
  contactEmail: import.meta.env.VITE_CONTACT_EMAIL || 'TNClandscape.Ryan@gmail.com'
}
