drop table if exists users, rooms, suggestion;
create table users (
	id integer primary key autoincrement,
	username text not null,
	room_id integer,
	foreign key (room_id) references rooms(id)
	)
create table rooms (
	id integer primary key autoincrement,
	joinable boolean not null,
	num_members integer not null
)
create table suggestion(
	id integer primary key autoincrement,
	name text not null,
	room_id integer,
	foreign key (room_id) references rooms(id)
	);
