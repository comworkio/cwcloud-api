UPDATE public.user
SET enabled_features = jsonb_set(
    COALESCE(enabled_features, '{}')::jsonb,
    '{without_vat}',
    to_jsonb(COALESCE(without_tva_fr, false)),
    true
) || jsonb_set(
    COALESCE(enabled_features, '{}')::jsonb,
    '{auto_pay}',
     to_jsonb(COALESCE(auto_pay, false)),
    true
);

ALTER TABLE public.user DROP COLUMN without_tva_fr;
ALTER TABLE public.user DROP COLUMN auto_pay;
