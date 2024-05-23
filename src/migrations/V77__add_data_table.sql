CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE data (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    device_id uuid NOT NULL,
    normalized_content JSONB NOT NULL,
    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES public.device(id) ON DELETE CASCADE
);

CREATE TABLE numeric_data (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    data_id uuid NOT NULL,
    device_id uuid NOT NULL,
    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    key varchar(254) NOT NULL,
    value float NOT NULL,
    FOREIGN KEY (data_id) REFERENCES public.data(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES public.device(id) ON DELETE CASCADE
);

CREATE TABLE string_data (
    id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    data_id uuid NOT NULL,
    device_id uuid NOT NULL,
    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    key varchar(254) NOT NULL,
    value varchar(254) NOT NULL,
    FOREIGN KEY (data_id) REFERENCES public.data(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES public.device(id) ON DELETE CASCADE
);

