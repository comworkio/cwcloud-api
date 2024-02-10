ALTER TABLE public.project ADD COLUMN git_username VARCHAR(300);
ALTER TABLE public.project ADD COLUMN access_token VARCHAR(300);
ALTER TABLE public.project ADD COLUMN gitlab_host VARCHAR(400);
ALTER TABLE public.project ADD COLUMN namespace_id VARCHAR(100);
