DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS selected_config;

-- store users
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  permission INTEGER NOT NULL
);

INSERT INTO user (username, password, permission) VALUES ('admin', 'admin', 0);

-- store config
CREATE TABLE config (
  config_name TEXT PRIMARY KEY,
  on_ec_level INTEGER NOT NULL,
  on_light_level INTEGER NOT NULL,
  off_light_level INTEGER NOT NULL,
  temp_setpoint INTEGER NOT NULL,
  temp_max INTEGER NOT NULL
);

INSERT INTO config (config_name, on_ec_level, on_light_level, off_light_level, temp_setpoint, temp_max) VALUES ('default', 50, 1000, 1100, 25, 32);
INSERT INTO config (config_name, on_ec_level, on_light_level, off_light_level, temp_setpoint, temp_max) VALUES ('microgreens', 50, 2000, 2100, 25, 32);

CREATE TABLE selected_config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  config_name TEXT,
  FOREIGN KEY (config_name) REFERENCES config(config_name)
);

INSERT INTO selected_config (config_name) VALUES ('default');