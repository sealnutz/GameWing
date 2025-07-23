// beacon/server.js   (ES-module style)

import { WebSocketServer } from "ws";
import pg from "pg";
import dotenv from "dotenv";
dotenv.config();

/* ────────── Postgres pool ────────── */
const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,   // defined in .env
});

/* ────────── WebSocket beacon ────────── */
const PORT = process.env.PORT || 3000;
const wss  = new WebSocketServer({ port: PORT });

console.log(`Beacon listening on ws://localhost:${PORT}`);

wss.on("connection", (socket, req) => {
  /* optional auth */
  const token = req.headers["x-auth"];
  if (process.env.SHARED_TOKEN && token !== process.env.SHARED_TOKEN) {
    console.log("🚫  Bad token, closing connection");
    socket.close();
    return;
  }

  const ip = req.socket.remoteAddress;
  console.log(`🔗  Client connected from ${ip}`);

  socket.on("message", async raw => {
    try {
      const evt = JSON.parse(raw);          // {ts, app, state, user_id, device_id}
      console.log("🡆", evt);

      /* write to DB */
      await pool.query(
        `INSERT INTO device_events (ts, app, state, user_id, device_id)
         VALUES ($1,$2,$3,$4,$5)`,
        [evt.ts, evt.app, evt.state, evt.user_id, evt.device_id]
      );

      socket.send(JSON.stringify({ ok: true }));
    } catch (err) {
      console.error("❌  Bad JSON or DB error:", err);
    }
  });

  socket.on("close", () => console.log(`❌  Connection closed: ${ip}`));
});
