CREATE TABLE IF NOT EXISTS public.access(
 id serial NOT NULL PRIMARY KEY,
 user_id INTEGER,
 object_id INTEGER ,
 access_str VARCHAR(100),
 object_type VARCHAR(100),
 created_at VARCHAR(100)
);