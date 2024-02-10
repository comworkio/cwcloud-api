CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 

CREATE TABLE faas_function (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    owner_id INT NOT NULL,
    is_public BOOLEAN NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES public.user(id)
);

CREATE TABLE faas_invocation (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    content JSONB NOT NULL,
    invoker_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoker_id) REFERENCES public.user(id)
);

CREATE TABLE faas_trigger (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    owner_id INT NOT NULL,
    content JSONB NOT NULL,
    kind VARCHAR(254) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES public.user(id)
);

CREATE INDEX faas_triggers_by_kind ON faas_trigger (kind);

ALTER TABLE public.user ADD COLUMN faasapi Boolean DEFAULT False;
