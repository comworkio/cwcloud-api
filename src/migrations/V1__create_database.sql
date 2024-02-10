CREATE TABLE IF NOT EXISTS public.instance(
 id serial NOT NULL PRIMARY KEY,
 hash VARCHAR(10) ,
 name VARCHAR(200) ,
 type VARCHAR(50) ,
 user_id INTEGER,
 environment_id INTEGER,
 project_id INTEGER,
 region VARCHAR(100) ,
 status VARCHAR(50) ,
 ip_address VARCHAR(100),
 created_at VARCHAR(100),
 modification_date timestamp
);


CREATE TABLE IF NOT EXISTS public.invoice(
 id serial NOT NULL PRIMARY KEY,
 instance_name VARCHAR(100) ,
 usage Float ,
 value Float ,
 date_created Date ,
 user_email VARCHAR(100)

);

CREATE TABLE IF NOT EXISTS public.user(
 id serial NOT NULL PRIMARY KEY,
 email VARCHAR(100),
 password VARCHAR(200) ,
 is_admin Boolean,
 confirmed Boolean,
 created_at VARCHAR(100)

);
