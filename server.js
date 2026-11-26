// Forest Chat: a tiny multiplayer 3D chat space.
// Run with `node server.js`, then open the printed link. No npm install needed.
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');

const PORT = Number(process.env.PORT) || 3000;
const MAX_PLAYERS = 10;
const PAGE = fs.readFileSync(path.join(__dirname, 'index.html'));

const players = new Map(); // id -> { id, name, color, x, z, ry, res }

function send(res, event, data) {
  res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}
function broadcast(event, data, exceptId) {
  for (const p of players.values()) if (p.id !== exceptId) send(p.res, event, data);
}
function publicInfo(p) {
  return { id: p.id, name: p.name, color: p.color, x: p.x, z: p.z, ry: p.ry };
}
function readJson(req, cb) {
  let body = '';
  req.on('data', (c) => { body += c; if (body.length > 2000) req.destroy(); });
  req.on('end', () => { try { cb(JSON.parse(body)); } catch { cb(null); } });
}
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, Number(v) || 0));

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');

  if (req.method === 'GET' && url.pathname === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache' });
    return res.end(PAGE);
  }

  // Server-Sent Events stream: one per connected person.
  if (req.method === 'GET' && url.pathname === '/events') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    });
    if (players.size >= MAX_PLAYERS) {
      send(res, 'full', { max: MAX_PLAYERS });
      return res.end();
    }
    const name = String(url.searchParams.get('name') || 'Guest').trim().slice(0, 16) || 'Guest';
    const id = crypto.randomBytes(4).toString('hex');
    const angle = Math.random() * Math.PI * 2;
    const p = {
      id, name, res,
      color: `hsl(${Math.floor(Math.random() * 360)}, 65%, 55%)`,
      x: Math.cos(angle) * 4, z: Math.sin(angle) * 4, ry: 0,
    };
    players.set(id, p);
    send(res, 'welcome', { you: publicInfo(p), players: [...players.values()].map(publicInfo) });
    broadcast('join', publicInfo(p), id);
    console.log(`+ ${name} joined (${players.size}/${MAX_PLAYERS})`);

    const ping = setInterval(() => res.write(': ping\n\n'), 15000);
    req.on('close', () => {
      clearInterval(ping);
      players.delete(id);
      broadcast('leave', { id });
      console.log(`- ${name} left (${players.size}/${MAX_PLAYERS})`);
    });
    return;
  }

  if (req.method === 'POST' && (url.pathname === '/move' || url.pathname === '/chat')) {
    return readJson(req, (msg) => {
      const p = msg && players.get(msg.id);
      if (!p) { res.writeHead(404); return res.end(); }
      if (url.pathname === '/move') {
        p.x = clamp(msg.x, -30, 30); p.z = clamp(msg.z, -30, 30); p.ry = clamp(msg.ry, -10, 10);
        broadcast('move', { id: p.id, x: p.x, z: p.z, ry: p.ry }, p.id);
      } else {
        const text = String(msg.text || '').trim().slice(0, 120);
        if (text) broadcast('chat', { id: p.id, text });
      }
      res.writeHead(204); res.end();
    });
  }

  res.writeHead(404); res.end('Not found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\nForest Chat is running.\n  On this computer:  http://localhost:${PORT}`);
  for (const list of Object.values(os.networkInterfaces())) {
    for (const a of list || []) {
      if (a.family === 'IPv4' && !a.internal) console.log(`  On your network:   http://${a.address}:${PORT}`);
    }
  }
  console.log('');
});
