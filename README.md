# PyCampus Classroom

A small 3D web classroom for practicing Python together. Students and one professor join from a link, take a seat, write Python in live code panes that everyone can watch, and run it in the browser. The professor posts problems on the whiteboard and spotlights a student's code for the whole room.

**Live demo:** https://py-campus.vercel.app

- [Project overview and agreed features](docs/overview.md)
- [System architecture (planned Python/FastAPI version)](docs/architecture.md)
- [UML class diagrams](docs/uml.md)

## How to use it

1. Open the link, type a nickname, and pick **Student** or **Professor**. Only one professor at a time; the button is disabled while someone holds it.
2. **Arrow keys** walk. **Click a chair** to sit; arrows stand you up.
3. **Enter** to chat. **H** raises or lowers your hand.
4. **B** (or click the whiteboard) opens the board:
   - **Students** write code in their own tab and press **Run**. Everyone can watch every student's tab live.
   - **The professor** writes a problem in the Problem tab and posts it, and can **Spotlight** any student's tab onto the big board.
5. When the professor leaves, the spotlight clears and anyone can take the professor role. The class keeps going.

Up to 10 people. No login and nothing is saved.

## How it's built (demo version)

- `index.html` is the whole app: three.js for the 3D room, CodeMirror for the editor, and Pyodide (Python compiled to WebAssembly) in a Web Worker to run code. Runs stop after 10 seconds.
- Hosted on Vercel as a static page. Live sync goes through **Supabase Realtime**: presence for who's here (name, role, seat, hand), broadcast for movement, chat, code and the whiteboard. The Supabase URL and anon/publishable key in `index.html` are public by design.
- `server.js` is an optional local relay: `node server.js` (Node 18+, no install), then open http://localhost:3000. It stands in for Supabase so you can run the classroom offline on one network. Browsers allow about 6 open connections per site, so use separate browsers or devices for more than 5 people in local mode.

The planned Python version replaces Supabase with a FastAPI WebSocket server that holds the room state in Python classes; see the docs above.
