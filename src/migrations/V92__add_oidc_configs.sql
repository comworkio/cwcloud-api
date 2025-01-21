BEGIN;

ALTER TABLE public.user
ADD COLUMN oidc_configs JSONB DEFAULT '[]'::jsonb;

CREATE INDEX idx_oidc_configs ON public.user USING GIN (oidc_configs);

COMMIT;
