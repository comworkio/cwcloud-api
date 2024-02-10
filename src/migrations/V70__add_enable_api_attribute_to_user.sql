ALTER TABLE public.user ADD COLUMN enabled_features JSONB DEFAULT '{}';

UPDATE public.user
SET enabled_features = jsonb_set(
    COALESCE(enabled_features, '{}')::jsonb,
    '{billable}',
    to_jsonb(COALESCE(billable, false)),
    true
)
    || jsonb_set(
        COALESCE(enabled_features, '{}')::jsonb,
        '{cwaiapi}',
        to_jsonb(COALESCE(cwaiapi, false)),
        true
    )
    || jsonb_set(
        COALESCE(enabled_features, '{}')::jsonb,
        '{emailapi}',
        to_jsonb(COALESCE(emailapi, false)),
        true
    )
    || jsonb_set(
        COALESCE(enabled_features, '{}')::jsonb,
        '{faasapi}',
        to_jsonb(COALESCE(faasapi, false)),
        true
    );

ALTER TABLE public.user DROP COLUMN billable;
ALTER TABLE public.user DROP COLUMN cwaiapi;
ALTER TABLE public.user DROP COLUMN emailapi;
ALTER TABLE public.user DROP COLUMN faasapi;