// Stap 2: GitHub stuurt de bezoeker terug. Wissel de code in voor een token
// en geef dat door aan het beheerscherm (Decap CMS) dat in het hoofdvenster draait.
const SITE = 'https://vanwezelbos.nl';

function page(status, payload) {
  const message = `authorization:github:${status}:${JSON.stringify(payload)}`;
  return `<!doctype html><html><body><p>Even geduld…</p><script>
(function () {
  var message = ${JSON.stringify(message)};
  var allowed = [${JSON.stringify(SITE)}, 'http://localhost:4173', 'http://localhost:8080'];
  function receive(e) {
    if (allowed.indexOf(e.origin) === -1) return;
    window.opener.postMessage(message, e.origin);
    window.removeEventListener('message', receive, false);
    setTimeout(function () { window.close(); }, 300);
  }
  window.addEventListener('message', receive, false);
  window.opener.postMessage('authorizing:github', '*');
})();
</script></body></html>`;
}

module.exports = async (req, res) => {
  const { code, state } = req.query || {};
  const cookie = (req.headers.cookie || '').split(';').map((c) => c.trim())
    .find((c) => c.startsWith('oauth_state='));
  const expected = cookie ? cookie.slice('oauth_state='.length) : null;
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Set-Cookie', 'oauth_state=; HttpOnly; Secure; SameSite=Lax; Path=/api; Max-Age=0');

  if (!code || !state || !expected || state !== expected) {
    res.status(400).send(page('error', { message: 'Inloggen mislukt (ongeldige sessie). Probeer opnieuw.' }));
    return;
  }
  try {
    const r = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        client_id: process.env.GITHUB_CLIENT_ID,
        client_secret: process.env.GITHUB_CLIENT_SECRET,
        code,
      }),
    });
    const data = await r.json();
    if (!data.access_token) throw new Error(data.error_description || data.error || 'Geen token ontvangen');
    res.status(200).send(page('success', { token: data.access_token, provider: 'github' }));
  } catch (err) {
    res.status(500).send(page('error', { message: String(err.message || err) }));
  }
};
