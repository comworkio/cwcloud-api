ALTER TABLE public.support_ticket_attachment
ADD COLUMN user_id INT,
ADD CONSTRAINT fk_user_support_attachment FOREIGN KEY (user_id) REFERENCES public.user (id);