// Stap 1 van de GitHub-inlog voor het beheerscherm: stuur de bezoeker naar GitHub.
const crypto = require('crypto');

module.exports = (req, res) => {
  const clientId = process.env.GITHUB_CLIENT_ID;
  if (!clientId) {
    res.status(500).send('GITHUB_CLIENT_ID ontbreekt in de Vercel-instellingen.');
    return;
  }
  const state = crypto.randomBytes(16).toString('hex');
  res.setHeader('Set-Cookie',
    `oauth_state=${state}; HttpOnly; Secure; SameSite=Lax; Path=/api; Max-Age=600`);
  const url = new URL('https://github.com/login/oauth/authorize');
  url.searchParams.set('client_id', clientId);
  url.searchParams.set('scope', 'repo');
  url.searchParams.set('state', state);
  res.writeHead(302, { Location: url.toString() });
  res.end();
};
