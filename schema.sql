
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS suggestions;
DROP TABLE IF EXISTS user_rankings;

CREATE TABLE 'users' (
	'user_id'	INTEGER PRIMARY KEY,
	'room_id'	INTEGER,
	'name'	TEXT NOT NULL,
	'suggestion_status'	INTEGER NOT NULL,
	'ranking_status'	INTEGER NOT NULL
);

CREATE TABLE 'rooms' (
	'room_id'	INTEGER PRIMARY KEY,
	'room_name'	TEXT NOT NULL,
	'status'	INTEGER NOT NULL
);

CREATE TABLE `suggestions` (
	`room_id`	INTEGER,
	`suggestion`	TEXT NOT NULL,
	`suggestion_name`	TEXT NOT NULL,
	`cord`	TEXT,
	`rating`	TEXT,
	`address`	TEXT,
	`rank`	INTEGER NOT NULL
);

CREATE TABLE 'user_rankings' (
	'user_id'	INTEGER NOT NULL,
	'suggestion'	TEXT NOT NULL,
	'rank'	INTEGER NOT NULL
);
