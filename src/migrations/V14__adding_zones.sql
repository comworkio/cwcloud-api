ALTER TABLE public.instance ADD COLUMN zone VARCHAR(100);
ALTER TABLE public.instance ADD COLUMN provider VARCHAR(100);
ALTER TABLE public.bucket ADD COLUMN provider VARCHAR(100);
ALTER TABLE public.project ADD COLUMN zone VARCHAR(100);
