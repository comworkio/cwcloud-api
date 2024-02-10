CREATE TABLE IF NOT EXISTS public.registry(
 id serial NOT NULL PRIMARY KEY,
 hash VARCHAR(10) ,
 name VARCHAR(200) ,
 type VARCHAR(50) ,
 user_id INTEGER,
 region VARCHAR(100) ,
 provider VARCHAR(100) ,
 secret_key VARCHAR(150),
 access_key VARCHAR(150),
 status VARCHAR(50) ,
 created_at VARCHAR(100)
);