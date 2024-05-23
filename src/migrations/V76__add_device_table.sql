CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

ALTER TABLE public.user
ADD CONSTRAINT unique_email UNIQUE (email);

CREATE TABLE device (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    typeobject_id uuid NOT NULL,
    username VARCHAR(200) NOT NULL,
    active BOOLEAN NOT NULL,
    FOREIGN KEY (typeobject_id) REFERENCES public.object_type(id),
    FOREIGN KEY (username) REFERENCES public.user(email) ON DELETE CASCADE
);
