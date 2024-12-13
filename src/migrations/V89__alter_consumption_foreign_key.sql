DELETE FROM consumption WHERE instance_id NOT IN (SELECT id FROM instance);

ALTER TABLE public.consumption
ADD CONSTRAINT fk_consumption_instance FOREIGN KEY (instance_id) REFERENCES instance (id);
