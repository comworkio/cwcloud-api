UPDATE public.user
SET enabled_features = jsonb_set(
    COALESCE(enabled_features, '{}')::jsonb,
    '{disable_emails}',
    to_jsonb(COALESCE(disable_emails, false)),
    true
);

ALTER TABLE public.user DROP COLUMN disable_emails;

