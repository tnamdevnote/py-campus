# PyCampus Classroom: overview

## What it is

PyCampus Classroom is a small 3D web classroom for practicing Python together. Students and one professor join from a link, walk into the room, take a seat, and work on Python problems. Every student has their own live code pane, and everyone can watch any pane as it's typed. The professor posts problems on the whiteboard, spotlights a student's code for the whole room, and gives feedback in chat. Think of it as live office hours in a shared room.

It's a class project for an object-oriented Python course. Two versions are planned:

- **Demo (now):** a single web page on Vercel, synced through Supabase Realtime. It's quick to ship and good for checking the idea.
- **Python version (later):** a FastAPI server that holds the room state in Python classes, on an always-on host such as Render or Fly.io. See [architecture.md](architecture.md) and [uml.md](uml.md).

## Agreed features

**Session and roles**
- One classroom session. There's no list of rooms and no multiple office hours.
- On entry you pick a name and a role, **Student** or **Professor**.
- Only one professor at a time. The Professor option is disabled while someone holds it, and it becomes available again when the professor leaves.
- The room never closes. With no professor, it keeps running and the spotlight clears.
- Up to 10 people. No login and no personal data.

**Everyone**
- Walk around the 3D classroom.
- Sit at a seat.
- Chat.
- Raise a hand ✋. It's just an icon over your head, with no other behavior.

**Students**
- Each student has their own code pane with Python highlighting.
- Everyone can watch every pane live on a tabbed board. Click the whiteboard to open it as a 2D overlay.
- A Run button runs your own code in the browser with Pyodide.

**Professor**
- Posts a problem on the whiteboard.
- Spotlights one student's pane onto the big board, live. Only the professor can do this.
- Gives feedback through chat.

**Later (not in scope now)**
- Saving work or keeping any state after people leave.
- A professor NPC, grading, or automatic answer checking.
