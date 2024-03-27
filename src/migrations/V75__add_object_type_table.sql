CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE object_type (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id INT NOT NULL,
    content JSONB NOT NULL,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES public.user(id)
);
