ALTER TABLE instance ADD COLUMN root_dns_zone VARCHAR(254);
UPDATE instance SET root_dns_zone = 'comwork.cloud';
