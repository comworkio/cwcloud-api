UPDATE public.bucket
SET endpoint=CONCAT('https://', name, '-', hash, '.s3.', region, '.scw.cloud')
WHERE provider='scaleway';

UPDATE public.bucket
SET endpoint=CONCAT('https://', name, '-', hash, '.s3.', REGEXP_REPLACE(LOWER(region), '[0-9]', '', 'g'), '.perf.cloud.ovh.net')
WHERE provider='ovh'

