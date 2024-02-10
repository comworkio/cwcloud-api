CREATE TABLE IF NOT EXISTS public.mfa(
 id serial NOT NULL PRIMARY KEY,
 user_id INTEGER,
 otp_code VARCHAR(100) ,
 name VARCHAR(100),
 type VARCHAR(100)
);

UPDATE public.user SET enabled_2fa=false;
ALTER TABLE public.user DROP COLUMN opt_code;
