# Forest Chat

A small 3D web space: a forest clearing with a campfire where up to 10 people walk around and chat.

## Run it

Needs [Node.js](https://nodejs.org) 18 or newer. No `npm install`.

```
node server.js
```

Open the link it prints (http://localhost:3000). Open it in a second window to see two characters. Others on the same Wi‑Fi can join with the "On your network" link.

## Controls

- **Arrow keys**: walk
- **Enter**: open chat, type, Enter again to send. Speech bubbles disappear after 5 seconds.
- **Click a person** (or their name tag): the camera moves close to them. Arrow keys or Esc return to the normal view.

## Notes

- Three files: `server.js` (plain Node web server, live updates over Server-Sent Events), `index.html` (the whole 3D page, three.js from a CDN), and this README.
- No login, payment or personal data. Nicknames live only in memory while the server runs.
- Max 10 people at once; the 11th sees a "campfire is full" message.
