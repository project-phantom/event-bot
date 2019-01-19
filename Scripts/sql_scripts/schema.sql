drop table if exists users;
drop table if exists events;
drop table if exists attendance;

CREATE TABLE if not exists users (
  user_id integer primary key AUTOINCREMENT,
  name varchar (255) not null, 
  token varchar(100)
);

CREATE TABLE if not exists events(
  event_id integer primary key AUTOINCREMENT,
  event_name varchar(255) not null,
  venue_id integer,
  venue_name varchar(100),
  date_time datetime,
  description varchar(255),
  visible_status int not null,
  total_attendee integer
  -- qr_image text
  -- organizer_id integer
);

CREATE TABLE if not exists bookings(
  event_id integer not null,
  venue_name varchar(100),
  date_time datetime,
  venue_status integer,
  time_slot_status integer,
  book_status integer 
);


-- CREATE TABLE if not exists attendances(
--   user_id integer not null,
--   event_id integer not null,
--   user_status integer
-- );


