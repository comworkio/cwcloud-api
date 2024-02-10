CREATE TABLE IF NOT EXISTS public.voucher(
 id serial NOT NULL PRIMARY KEY,
 code VARCHAR(100),
 validity INTEGER,
 user_id INTEGER,
 created_at VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS public.registered_voucher(
 id serial NOT NULL PRIMARY KEY,
 user_id INTEGER,
 voucher_id INTEGER,
 created_at VARCHAR(100)
);