ALTER TABLE public.invoice RENAME TO consumption;

CREATE TABLE IF NOT EXISTS public.invoice(
 id serial NOT NULL PRIMARY KEY,
 ref VARCHAR(100),
 from_date Date ,
 date_created Date ,
 to_date Date ,
 user_id INTEGER

);