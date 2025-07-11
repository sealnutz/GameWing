CREATE TABLE IF NOT EXISTS device_events (
  id         SERIAL PRIMARY KEY,
  ts         BIGINT      NOT NULL,
  app        TEXT        NOT NULL,
  state      TEXT        NOT NULL,
  user_id    TEXT        NOT NULL,
  device_id  TEXT        NOT NULL
);
