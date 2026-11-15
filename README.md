# vanwezelbos.nl

Statische site (geen WordPress, geen build-stap op Vercel). Alles in `public/` wordt geserveerd.

## Nieuw bericht plaatsen
1. Zet foto's (liefst max. 1800px breed, JPG) in `public/img/`.
2. Voeg een item toe aan `content/posts.json`.
3. Maak `content/posts/<slug>.html` met de tekst (`<p>`, `<h3>`, `<strong>`).
4. Draai `python3 scripts/build.py` en commit + push. Vercel deployt automatisch.

## Deployen
Importeer de GitHub-repo in Vercel (framework: *Other*, geen build command, output directory `public`; staat al in `vercel.json`).
Zet daarna het domein `vanwezelbos.nl` aan het Vercel-project en wijs de DNS ernaartoe.
