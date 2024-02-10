CREATE TABLE IF NOT EXISTS public.support_ticket(
 id serial NOT NULL PRIMARY KEY,
 user_id INTEGER,
 selected_product VARCHAR(200) ,
 status VARCHAR(100),
 severity VARCHAR(100),
 message TEXT
);

CREATE TABLE IF NOT EXISTS public.support_change_status_log(
 id serial NOT NULL PRIMARY KEY,
 ticket_id INTEGER,
 status VARCHAR(100),
 change_date VARCHAR(100)
);