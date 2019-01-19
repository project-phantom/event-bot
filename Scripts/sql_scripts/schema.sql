drop table if exists users;
drop table if exists events;
drop table if exists attendance;

CREATE TABLE if not exists users (
  user_id integer primary key AUTOINCREMENT,
  name varchar (255) not null, 
  token varchar(100)
);

CREATE TABLE if not exists events (
  event_id integer primary key AUTOINCREMENT,
  title varchar(255) not null,
  venue_id varchar(255),
  organiser varchar (255) not null,
  description varchar(255),
  status int not null,
  cur_attendance integer
  -- qr_image text
);

CREATE TABLE if not exists attendances(
  user_id integer not null,
  event_id integer not null,
  user_status integer
);

create table if not exists venues(
  venue_id integer primary key AUTOINCREMENT,
  venue_name varchar(100) not null,
  time_slot datetime,
  book_status integer 
);