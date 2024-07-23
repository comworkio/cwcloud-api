CREATE TABLE IF NOT EXISTS support_ticket_attachment (
    id SERIAL PRIMARY KEY,
    storage_key VARCHAR(255) NOT NULL,
    mime_type VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    support_ticket_id SERIAL NOT NULL,
    FOREIGN KEY (support_ticket_id) REFERENCES public.support_ticket (id) ON DELETE CASCADE
);
