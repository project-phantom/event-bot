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
  event_name varchar(255) not null,
  venue_id varchar(255),
  organizer_id integer,
  description varchar(255),
  visible_status int not null,
  total_attendee integer
  -- qr_image text
);

      -- self.organizerID = organizerID
      --   self.name = name
      --   self.description = description
      --   self.visibility = visibility
      --   self.booking = booking
      --   self.attendee = attendee

CREATE TABLE if not exists attendances(
  user_id integer not null,
  event_id integer not null,
  user_status integer
);

create table if not exists booking_venues(
  venue_id integer primary key AUTOINCREMENT,
  venue_name varchar(100) not null,
  date_time datetime,
  book_status integer,
  event_id integer
);

