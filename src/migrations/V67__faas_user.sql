INSERT INTO public.user (email, "password", is_admin, confirmed, created_at) VALUES ('faas@comwork.io', '$2a$11$78TFYLecDcq8Mw08k1C8A.vpFdt4T0GC3cz2V.PX0z8W3t9TzCm3m', true, true, '2023-09-19T12:00:36.609Z');

INSERT INTO api_keys (user_id, access_key, secret_key, created_at) VALUES ((SELECT id FROM public.user WHERE email = 'faas@comwork.io' LIMIT 1), 'CWCTEZGVSNCKKRRHKPQG', '366a119d-b23d-4b76-93e8-a0e24b12abaf', '2023-09-19T12:00:36.609Z');
