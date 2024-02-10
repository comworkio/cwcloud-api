CREATE TABLE IF NOT EXISTS public.environment(
 id serial NOT NULL PRIMARY KEY,
 name VARCHAR(100),
 description VARCHAR(1000),
 path VARCHAR(100) ,
 roles VARCHAR(300) ,
 main_role VARCHAR(100) ,
 is_private Boolean,
 created_at VARCHAR(100)
 
);