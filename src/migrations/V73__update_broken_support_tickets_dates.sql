UPDATE public.support_change_status_log
SET change_date = '1970-01-01T00:00:00'
WHERE change_date IS NULL;

UPDATE public.support_ticket
SET created_at = '1970-01-01T00:00:00'
WHERE created_at IS NULL;

UPDATE public.support_ticket
SET last_update = '1970-01-01T00:00:00'
WHERE last_update IS NULL;
