CREATE INDEX c_by_user_id ON consumption(user_id);
CREATE INDEX c_by_instance_id ON consumption(instance_id);
DELETE FROM instance WHERE status NOT IN ('active', 'starting');
DELETE FROM consumption WHERE instance_id NOT IN (SELECT id FROM instance);
