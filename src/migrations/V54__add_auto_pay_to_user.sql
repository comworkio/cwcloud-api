ALTER TABLE public.user ADD COLUMN auto_pay Boolean;
UPDATE public.user
SET auto_pay = false;