# Forest Chat

A small 3D web space: a forest clearing with a campfire where up to 10 people walk around and chat.

## Run it

Needs [Node.js](https://nodejs.org) 18 or newer. No `npm install`.

```
node server.js
```

Open the link it prints (http://localhost:3000). Open it in a second window to see two characters. Others on the same Wi‑Fi can join with the "On your network" link.

## Put it online (Vercel + Supabase)

Vercel only serves static pages, so live syncing goes through Supabase Realtime (free tier) instead of `server.js`.

1. Create a free project at [supabase.com](https://supabase.com). No tables are needed.
2. In Project Settings → API, copy the **Project URL** and the **anon / publishable key**.
3. Paste them into `SUPABASE_URL` and `SUPABASE_KEY` near the networking section of `index.html`. The anon key is meant to be public. Never use the `service_role` / secret key.
4. On [vercel.com/new](https://vercel.com/new), import this repo. Framework preset: **Other**, no build command. Deploy.

With those two values empty, the page talks to `server.js` instead, so local play still works.

## Controls

- **Arrow keys**: walk
- **Enter**: open chat, type, Enter again to send. Speech bubbles disappear after 5 seconds.
- **Click a person** (or their name tag): the camera moves close to them. Arrow keys or Esc return to the normal view.

## Notes

- Three files: `server.js` (plain Node web server, live updates over Server-Sent Events), `index.html` (the whole 3D page, three.js from a CDN, optional Supabase Realtime), and this README.
- No login, payment or personal data. Nicknames live only in memory while the server runs.
- Max 10 people at once; the 11th sees a "campfire is full" message.
