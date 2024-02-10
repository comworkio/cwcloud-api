CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 

CREATE TABLE faas_execution_trace (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    invocation_id uuid NOT NULL,
    content JSONB NOT NULL,
    invoker_id INT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoker_id) REFERENCES public.user(id)
);

CREATE INDEX idx_faas_execution_trace_invoker_id ON faas_execution_trace (invoker_id);