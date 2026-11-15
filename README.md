# vanwezelbos.nl

Statische site op Vercel. Berichten schrijf je in het beheerscherm: **vanwezelbos.nl/admin**.

## Berichten (voor wie schrijft)
1. Ga naar `vanwezelbos.nl/admin` en klik op *Inloggen met GitHub*.
2. Klik op *Bericht* → vul categorie, datum, titel, afbeelding en tekst in.
3. Controleer rechts de preview (Desktop / Tablet / Telefoon) en klik op *Publiceren*.
4. Na ongeveer een minuut staat het bericht live.

## Techniek
- `content/posts/*.md` — de berichten (Markdown met kopregel). Het beheerscherm leest en schrijft deze bestanden.
- `scripts/build.py` — maakt er HTML van in `public/`; Vercel draait dit bij elke wijziging.
- `public/admin/` — Decap CMS (`config.yml` = velden, `preview.js` = apparaat-preview).
- `api/auth.js` + `api/callback.js` — GitHub-inlog voor het beheerscherm.
  Vereist in Vercel (Settings → Environment Variables): `GITHUB_CLIENT_ID` en `GITHUB_CLIENT_SECRET`
  van een GitHub OAuth App met callback `https://vanwezelbos.nl/api/callback` (Vercel stuurt door naar www).
- Foto's: `public/img/`. Bij de build worden grote foto's automatisch verkleind (Pillow, indien beschikbaar).
