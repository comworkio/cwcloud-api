ALTER TABLE public.api_keys
ADD CONSTRAINT uq_access_secret_key UNIQUE (access_key, secret_key);

ALTER TABLE public.api_keys
ALTER COLUMN user_id SET NOT NULL;

ALTER TABLE public.api_keys
ADD CONSTRAINT fk_api_keys_user FOREIGN KEY (user_id) REFERENCES "user" (id);