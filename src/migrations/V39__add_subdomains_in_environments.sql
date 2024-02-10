ALTER TABLE public.environment ADD COLUMN subdomains VARCHAR(300);

UPDATE public.environment set subdomains = 'imalive' WHERE path = 'code' OR path = 'pgsql' OR path = 'mariadb' OR path = 'vps';
UPDATE public.environment set subdomains = '*' WHERE path = 'lt';
UPDATE public.environment set subdomains = 'api;imalive' WHERE path = 'elasticstack'