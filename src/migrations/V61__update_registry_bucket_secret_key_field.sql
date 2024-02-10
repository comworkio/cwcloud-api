ALTER TABLE public.registry
ALTER COLUMN secret_key TYPE TEXT;
ALTER TABLE public.bucket
ALTER COLUMN secret_key TYPE TEXT;