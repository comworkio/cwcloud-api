INSERT INTO public.environment (name, path,description,created_at ,roles,main_role,is_private)
VALUES ('code', 'code','this is a description for code','2022-06-02T21:00:36.609Z', 'sudo;common;ssh;cloud-instance-ssh-keys;fail2ban;kinsing;firewall;docker;code;gw-letsencrypt;gitlab-runner','code',false);
INSERT INTO public.environment (name, path,description,created_at ,roles,main_role,is_private)
VALUES ('wordpress', 'wpaas','this is a description for wordpress', '2022-06-02T21:00:36.609Z','sudo;common;ssh;cloud-instance-ssh-keys;fail2ban;kinsing;firewall;docker;wordpress;gw-letsencrypt;gitlab-runner','wordpress',false);

UPDATE public.environment
SET roles = 'sudo;common;ssh;cloud-instance-ssh-keys;fail2ban;kinsing;firewall;docker;code;gw-letsencrypt;nginx;gitlab-runner'
WHERE path='code';

UPDATE public.environment
SET roles = 'sudo;common;ssh;cloud-instance-ssh-keys;fail2ban;kinsing;firewall;docker;wordpress;gw-letsencrypt;nginx;gitlab-runner'
WHERE path='wpaas';