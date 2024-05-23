ALTER TABLE public.support_change_status_log ADD creation_date VARCHAR(100);

UPDATE public.support_change_status_log
SET creation_date = '1970-01-01T00:00:00'
WHERE creation_date IS NULL;
