drop table if exists agenda;
create table agenda (
  id integer primary key autoincrement,
  name text not null,
  last_name text not null,
  address text not null,
  email text not null,
  phone_number text not null,
  phone_type text not null
);