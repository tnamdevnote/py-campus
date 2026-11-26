// PyCampus Classroom: local relay server.
// Run `node server.js` and open the printed link to use the classroom without Supabase.
// It mimics the two Supabase Realtime features the page uses:
//   presence  - who is here (name, role, seat, hand)
//   broadcast - messages to everyone else (move, chat, code, board, hello)
// The page holds all classroom rules; this server only relays. No npm install needed.
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const PORT = Number(process.env.PORT) || 3000;
const MAX_CONNECTIONS = 30; // the page itself caps the classroom at 10 people
const PAGE = fs
  .readFileSync(path.join(__dirname, 'index.html'), 'utf8')
  .replace('<head>', '<head><script>window.LOCAL_RELAY = true;</script>');

const clients = new Map(); // id -> SSE response
const presence = {}; // id -> [meta]

const sse = (res, event, data) => res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
const sendPresence = () => { for (const res of clients.values()) sse(res, 'presence', presence); };

function readJson(req, limit, cb) {
  let body = '';
  req.on('data', (c) => { body += c; if (body.length > limit) req.destroy(); });
  req.on('end', () => { try { cb(JSON.parse(body)); } catch { cb(null); } });
}
const validId = (id) => typeof id === 'string' && /^[a-z0-9]{4,16}$/.test(id);

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');

  if (req.method === 'GET' && url.pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache' });
    return res.end(PAGE);
  }

  if (req.method === 'GET' && url.pathname === '/events') {
    const id = url.searchParams.get('id');
    if (!validId(id) || clients.size >= MAX_CONNECTIONS) { res.writeHead(400); return res.end(); }
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
    clients.set(id, res);
    sse(res, 'presence', presence);
    const ping = setInterval(() => res.write(': ping\n\n'), 15000);
    req.on('close', () => {
      clearInterval(ping);
      if (clients.get(id) === res) clients.delete(id);
      if (presence[id]) { delete presence[id]; sendPresence(); }
    });
    return;
  }

  if (req.method === 'POST' && ['/track', '/untrack', '/send'].includes(url.pathname)) {
    return readJson(req, 24000, (msg) => {
      if (!msg || !validId(msg.id) || !clients.has(msg.id)) { res.writeHead(400); return res.end(); }
      if (url.pathname === '/track') {
        if (JSON.stringify(msg.meta || {}).length > 4000) { res.writeHead(413); return res.end(); }
        presence[msg.id] = [msg.meta];
        sendPresence();
      } else if (url.pathname === '/untrack') {
        delete presence[msg.id];
        sendPresence();
      } else {
        const out = { from: msg.id, event: String(msg.event || ''), payload: msg.payload };
        for (const [cid, r] of clients) if (cid !== msg.id) sse(r, 'bc', out);
      }
      res.writeHead(204); res.end();
    });
  }

  res.writeHead(404); res.end('Not found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\nPyCampus Classroom (local mode) is running.\n  On this computer:  http://localhost:${PORT}`);
  for (const list of Object.values(os.networkInterfaces())) {
    for (const a of list || []) {
      if (a.family === 'IPv4' && !a.internal) console.log(`  On your network:   http://${a.address}:${PORT}`);
    }
  }
  console.log('');
});
