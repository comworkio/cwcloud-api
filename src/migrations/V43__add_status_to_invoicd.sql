ALTER TABLE public.invoice ADD COLUMN status VARCHAR(100);

UPDATE public.invoice
SET status='paid'
WHERE payed=true;

UPDATE public.invoice
SET status='unpaid'
WHERE payed=false;

ALTER TABLE public.invoice DROP COLUMN payed;

