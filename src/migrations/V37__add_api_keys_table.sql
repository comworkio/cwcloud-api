CREATE TABLE IF NOT EXISTS public.api_keys(
 id serial NOT NULL PRIMARY KEY,
 access_key VARCHAR(100) ,
 secret_key VARCHAR(100) ,
 user_id INTEGER
);
