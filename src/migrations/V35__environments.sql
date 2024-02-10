--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.22
-- Dumped by pg_dump version 9.6.22

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DELETE FROM public.environment;

--
-- Data for Name: environment; Type: TABLE DATA; Schema: public; Owner: cloudapi
--

INSERT INTO public.environment VALUES (6, 'wordpress', 'Wordpress installation', 'wpaas', 'common;ssh;sudo;cloud-instance-ssh-keys;fail2ban;kinsing;firewall;docker;wordpress;gw-letsencrypt;nginx;gitlab-runner', 'wordpress', false, '2022-06-02T21:00:36.609Z', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

wp_env_name: {{ env_name }}
wp_lang: fr_FR
wp_mysql_passwd: changeit
wp_root_url: https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
wp_force_recreate: true
wp_port: 8080

smtp_host: changeit.changeit.com
smtp_port: 587
smtp_username: changeit
smtp_password: changeit

wp_smtp_from: changeit@changeit.com
wp_smtp_from_bui_name: changeit
wp_instance_name: {{ env_name }}
wp_admin_users:
  - name: admin
    passwd: $apr1$M4x65b92$KsQCdoC.BzdBcuTai2MuG0
wp_mysql_passwd: changeit 
wp_table_prefix: wp_ 
wp_smtp_from: changeit@changeit.com
wp_smtp_from_bui_name: changeit"

gw_websites: []
gw_auth_files: []
gw_upstreams: []
{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8080
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16
', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

## Init your wordpress instance

You can install your wordpress [here](https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}).

It''ll ask for a username and password and it''s the following:

* username: `admin`
* password: `changeit`

You can change your password in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
wp_admin_users:
  - name: admin
    passwd: $apr1$M4x65b92$KsQCdoC.BzdBcuTai2MuG0
```

For generating a new password to copy in the `passwd` field:

```shell
htpasswd -c .htpasswd.tmp admin
cat .htpasswd.tmp | cut -d ":" -f2 # copy the output as passwd
rm -rf .htpasswd.tmp
```

Go check our documentation [here](https://doc.cloud.comwork.io/docs/wpaas)');
INSERT INTO public.environment VALUES (12, 'elasticstack', 'Elasticstack cluster', 'elasticstack', 'common;sudo;ssh;cloud-instance-ssh-keys;kinsing;es-backup-command;fail2ban;firewall;docker;docker-elasticstack;imalive;elastic-rollup;gw-letsencrypt;nginx;gitlab-runner', 'docker-elasticstack', true, '2022-06-24T08:16:31.353763', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

vm_max_map_count: 262144
disable_docker_rp: true
elastic_cluster_size: 3
elastic_project_name: {{ env_hashed_name }}
kibana_public_ns: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
elastic_public_ns: api.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
backup_es_host: api.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
elastic_username: elastic
elastic_password: changeme
elastic_basic_auth: ZWxhc3RpYzpjaGFuZ2VtZQ==
kibana_username: kibana
kibana_password: changeme
enable_fix_rights: true
enable_docker_gateway: false
letsencrypt_disable_nginx: false
elastic_backup_directory: /home/es-backup
elastic_fs_user: cloud
elasticsearch_home_directory: /home/cloud/elasticstack

gw_auth_files:
  - name: elastic.keys
    users:
      - name: elastic
        passwd: $apr1$2ufk6wqe$metve5eCMLkqAyGQ9DwtE.

should_slack: "off"
elastic_host: api.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
slack_token: changeit

force_recreate: true
redeliver_kibana: true
redeliver_elastic_search: true
delete_all_old_containers: true

gw_upstreams:
  - name: elasticcluster
    # TODO replace the members entries by the following once your cluster is set
    # members: ["localhost:9201", "localhost:9202", "localhost:9203"]
    members: ["localhost:8099"]

gw_websites: []
{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: api.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: elasticcluster
    auth_file: elastic.keys
    elastic: true
  - domain: imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8099
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    # TODO replace the target by the following once your cluster is set
    # target: localhost:5601
    target: localhost:8099
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16
', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

## Init the elastic credentials

Inside one of the elastic containers, run the following command:

```shell
docker exec -it {{ env_hashed_name }}_data_es_db_01 bin/elasticsearch-setup-passwords interactive
```

Choose your password wisely and do not loose it!

Then change the `changeme` values in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
elastic_password: changeme
kibana_password: changeme
```

Then update this value:

```yaml
elastic_basic_auth: ZWxhc3RpYzpjaGFuZ2VtZQ==
```

In order to get a valid basic auth, you can use this command:

```shell
printf "elastic:{your new password}|base64"
```

Then update this value:

```yaml
gw_auth_files:
  - name: elastic.keys
    users:
      - name: elastic
        passwd: $apr1$2ufk6wqe$metve5eCMLkqAyGQ9DwtE.
```

In order to get a valid htpasswd, here''s the command:

```shell
htpasswd -c .htpasswd.tmp elastic
cat .htpasswd.tmp | cut -d ":" -f2 # copy the output as passwd
rm -rf .htpasswd.tmp
```

## Replace the targets of the reverse proxy

Go replace the commented TODO in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file: 

```yaml
gw_upstreams:
  - name: elasticcluster
    # TODO replace the members entries by the following once your cluster is set
    # members: ["localhost:9201", "localhost:9202", "localhost:9203"]
    members: ["localhost:8099"]
```

And:

```yaml
# TODO replace the target by the following once your cluster is set
# target: localhost:5601
target: localhost:8099
```

## Avoid downtime on deployment

We advise you to disable (`true` => `false`) those three settings in order to avoid downtime each time you trigger a pipeline:

```yaml
redeliver_kibana: false
redeliver_elastic_search: false
delete_all_old_containers: false
```

## Imalive metrics exporter

There''s an [imalive api](https://doc.cloud.comwork.io/docs/tutorials/imalive) deployed on your instance.

Here''s the domain you can send http requests: https://imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}

To see the metrics of your instance:

```shell
curl https://imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}/metrics | jq .
```');
INSERT INTO public.environment VALUES (18, 'mariadb', 'MariaDB (MySQL fork) database instance', 'mariadb', 'common;fail2ban;sudo;ssh;cloud-instance-ssh-keys;firewall;kinsing;docker;imalive;mariadb;gw-letsencrypt;nginx;gitlab-runner', 'imalive', false, '2022-09-12T20:33:17.691721', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

gw_upstreams: []

gw_auth_files: []

gw_websites: []

{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8099
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443
  - port: 3306

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

## After first installation of MariaDB / MySQL

It''s highly recommand to allow connection to the port `3306` only from the hosts or networks which need to connect to the db:

```yaml
firewall_allow:
  - port: 22
  - port: 80
  - port: 443
  - port: 3306
    ip: {put your ip here}
```

Then secure your database:

```shell
$ sudo mysql_secure_installation
Set root password? [Y/n] Y
Remove anonymous users? [Y/n] Y
Disallow root login remotely? [Y/n] Y
Reload privilege tables now? [Y/n] Y
```

Then create a database and a user that will be able to connect to this database from the outside:

```shell
$ sudo su -
$ mysql -uroot -p # use the password you just set
MariaDB [(none)]> CREATE USER ''your_user''@''%'' IDENTIFIED BY ''your_password'';
MariaDB [(none)]> CREATE DATABASE your_db;
MariaDB [(none)]> use your_db;
MariaDB [your_db]> GRANT ALL PRIVILEGES ON your_db TO ''your_user''@''%'';
MariaDB [your_db]> GRANT ALL PRIVILEGES ON your_db.* TO ''your_user''@''%'';
MariaDB [your_db]> FLUSH PRIVILEGES;
```

Then you can connect from the outside:

```shell
mysql -h {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} -uyour_user -p your_db
```

Then you can try some SQL commands:

```shell
mysql> CREATE TABLE my_table (id INTEGER);
Query OK, 0 rows affected (0.04 sec)
mysql> INSERT INTO my_table VALUES (1);
Query OK, 1 row affected (0.04 sec)
```

More informations in this [tutorial](https://doc.cloud.comwork.io/docs/tutorials/dbaas).');
INSERT INTO public.environment VALUES (13, 'portainer', 'Portainer instance : CaaS / containers management solution', 'portainer', 'common;sudo;ssh;cloud-instance-ssh-keys;docker;firewall;fail2ban;gw-letsencrypt;nginx;portainer;imalive;kinsing;gitlab-runner', 'portainer', false, '2022-07-07T18:43:55.707394', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

portainer_websocket_port: 8000
portainer_domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
portainer_upstream: portainerwebsocket

gw_upstreams:
  - name: portainerapi
    members: ["localhost:9008", "localhost:9009", "localhost:9010"]
  - name: portainerwebsocket
    members: ["localhost:8008", "localhost:8009", "localhost:8010"]

gw_auth_files: []
gw_websites: []
{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: portainerapi
    conf: tool_proxy

{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443
  - port: 8000

  gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16
', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

Go check our documentation [here](https://doc.cloud.comwork.io/docs/portainer)

You''ll find there how to create a portainer edge agent on other instances.
');
INSERT INTO public.environment VALUES (14, 'matomo', 'Matomo installation', 'matomo', 'common;sudo;ssh;cloud-instance-ssh-keys;docker;firewall;fail2ban;gw-letsencrypt;nginx;matomo;kinsing;gitlab-runner', 'matomo', false, '2022-07-10T09:54:12.294217', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

gw_upstreams: []
gw_auth_files: []
gw_websites: []

{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:3200
{% endif %}

matomo_trusted_host: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
matomo_mysql_password: changeit
matomo_salt: changeit

firewall_allow:
  - port: 22
  - port: 80
  - port: 443

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```
Go check our documentation [here](https://doc.cloud.comwork.io/docs/matomo)

You''ll find the password to connect your instance in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
access_password: XXXXXXXX
```
');
INSERT INTO public.environment VALUES (16, 'localtunnel', 'Instance of localtunnel-server as a service', 'lt', 'common;sudo;ssh;cloud-instance-ssh-keys;firewall;fail2ban;kinsing;docker;imalive;tunnelserver;gw-letsencrypt;nginx;gitlab-runner', 'tunnelserver', false, '2022-09-06T17:05:55.910263', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

tunnel_server_domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
tunnel_force_recreate: true

gw_upstreams: []
gw_auth_files: []
gw_websites: []

{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8099
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:3200
  - domain: localtunnel-1.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localtunnel-1.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}:3200
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443
  - port: 3200
    ip: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16
', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

## Use your localtunnel instance with the lt CLI

### Allow your private network to the tunnelserver''s firewall

First you have to allow your network public''s ip where you need to expose port via tunnel. 

Get your public ip first:

```shell
curl ifconfig.me
```

Then, add the value in the firewall section in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
firewall_allow:
  # ...
  - ip: YOUR_PUBLIC_IP # to replace by the value returned by the previous curl
    cidr: 24
```

### Expose your service with the lt CLI

You can install the cli this way:

```shell
npm install -g localtunnel
```

Then, use it this way:

```shell
lt --host https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} --port {the port you want to expose} --subdomain localtunnel-1
```

### Open multiple tunnels

Note: you can use multiple tunnels, you just have to add your tunnels subdomains in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
gw_proxies:
  # ...
  - domain: localtunnel-1.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localtunnel-1.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}:3200
  - domain: localtunnel-2.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localtunnel-2.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}:3200
  - domain: localtunnel-3.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localtunnel-3.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}:3200
```

Then you''ll be able to open new tunnels with your client:

```shell
lt --host https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} --port 8080 --subdomain localtunnel-1
lt --host https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} --port 8081 --subdomain localtunnel-2
lt --host https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} --port 8082 --subdomain localtunnel-3
```

And share those urls:

```shell
https://localtunnel-1.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} 
https://localtunnel-2.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} 
https://localtunnel-3.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```');
INSERT INTO public.environment VALUES (15, 'faasd', 'A lightweight & portable FaaS engine (lightweight distribution of OpenFaaS)', 'faasd', 'common;sudo;fail2ban;ssh;cloud-instance-ssh-keys;faasd;gw-letsencrypt;nginx;gitlab-runner', 'faasd', false, '2022-08-30T18:03:14.822343', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}


config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

faasd_user: cloud
faasd_password: {{ access_password }}

gw_upstreams: []

gw_auth_files: []

gw_websites: []


{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8080
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```


## Use OpenFaaS cli and GUI

You can install go to the OpenFaaS GUI [here](https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}).

It''ll ask for a username and password that you''ll find in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
faasd_user: cloud
faasd_password: {random password generated}
```

Install the faas cli if it''s not already done:

```shell
curl -sSL https://cli.openfaas.com | sudo sh
```

To connect with the faasd CLI:

```shell
export OPENFAAS_URL=https://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
faas-cli login --username cloud --password {the random password generated}
```

More details here: https://doc.cloud.comwork.io/docs/tutorials/faasd');
INSERT INTO public.environment VALUES (11, 'gateway', 'A simple nginx gateway (reverse proxy and load balancer)', 'vps', 'common;sudo;ssh;cloud-instance-ssh-keys;docker;fail2ban;firewall;imalive;gw-letsencrypt;nginx;kinsing;gitlab-runner', 'imalive', false, '2022-06-24T08:10:49.856459', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

gw_upstreams: []
bucket_name: letsencrypt-backup
backup_date_format: "+%F"
backup_folder: /etc/letsencrypt
zip_compress_backup_enable: true
backup_inside_container: /tls-data
backup_zip_file_folder: /home/s3-data-backup/tmp

gw_auth_files: []
gw_websites: []
{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8099
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8099
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16
', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

Go check our documentation [here](https://doc.cloud.comwork.io/docs/vps)

## Imalive metrics exporter

There''s an [imalive api](https://doc.cloud.comwork.io/docs/tutorials/imalive) deployed on your instance.

Here''s the domain you can send http requests: https://imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}

To see the metrics of your instance:

```shell
curl https://imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}/metrics | jq .
```
');
INSERT INTO public.environment VALUES (1, 'code', 'VSCode on your browser with all the tooling you need (git, docker, k3d, kubectl, etc)', 'code', 'common;sudo;ssh;cloud-instance-ssh-keys;fail2ban;kinsing;firewall;docker;code;gw-letsencrypt;nginx;gitlab-runner', 'code', false, '2022-06-02T21:00:36.609Z', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

coder_password: {{ access_password }}
coder_git_email: {{ user_email }}
oci_registries: []
ssh_servers_config: []

gpg_keys_b64: []

ssh_private_keys_b64: []

kube_configs_b64:
  - filename: changeit
    current_ctx: true
    value: changeit

code_git_workspaces:
  - name: {{ env_name }}
    git: {{ gitlab_project_remote }}

gw_upstreams:
  - name: cloud-server
    members: ["localhost:8080"]
gw_auth_files: []
gw_websites: []
{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: cloud-server
    conf: tool_proxy
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16

', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

Go check our documentation [here](https://doc.cloud.comwork.io/docs/code)
');
INSERT INTO public.environment VALUES (17, 'postgresql', 'PostgreSQL database instance', 'pgsql', 'common;ssh;cloud-instance-ssh-keys;fail2ban;sudo;firewall;kinsing;docker;imalive;postgresql;postgresql-roles;gw-letsencrypt;gw-nginx;gitlab-runner', 'imalive', false, '2022-09-09T21:26:41.719384', '---
node_home: /root
node_name: {{ env_hashed_name }}
deploy_user: cloud

sudo_users:
  - name: cloud
    passwd: no
  - name: gitlab-runner
    passwd: no

docker_users:
  - cloud
  - gitlab-runner

root_password: {{ root_password }}
gitlab_runner_token: changeit
gitlab_registration_token: {{ gitlab_runner_token }}
gitlab_runner_binary_path: /usr/bin
gitlab_url: {{ gitlab_host }}

config_path: /etc/letsencrypt/configs
certbot_packages: python3-certbot-nginx
letsencrypt_choice: ''y''

# change to false after first installation
pgsql_first_install: "true" 

pg_allowed_hosts:
  - ip: 0.0.0.0
    cidr: 0

gw_upstreams: []
gw_auth_files: []
gw_websites: []
{% if generate_dns == ''false'' %}
gw_proxies: []
{% else %}
gw_proxies:
  - domain: imalive.{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8099
  - domain: {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
    target: localhost:8099
{% endif %}

firewall_allow:
  - port: 22
  - port: 80
  - port: 443
  - port: 5432

gw_deny_ips:
  - ip: 91.140.0.0
    cidr: 16
', '# Instance {{ env_hashed_name }}

Environment: {{ environment }}

## Connect to the machine with ssh

Add this configuration in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file:

```yaml
ssh_users:
  - username: cloud
    keys: 
      - {your public key}
```

Then, `git commit` and `git push` and wait for the end of the pipeline. You''ll be able to connect with ssh:

```shell
ssh -i ~/.ssh/your_private_key cloud@{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}
```

## After first installation of PostgreSQL

Set to false this variable in the [`{{ env_name }}.yml`](./{{ env_name }}.yml) file (the quote are important):

```yaml
pgsql_first_install: "false"
```

In the same file, it''s highly recommand to allow connection to the port `5432` only from the hosts or networks which need to connect to the db:

```yaml
firewall_allow:
  - port: 22
  - port: 80
  - port: 443
  - port: 5432
    ip: {put your ip here}
```

Then you can connect with SSH after adding your key and create your first db like that:

```shell
$ sudo su -
$ su - postgres
$ psql
postgres=> CREATE ROLE your_username LOGIN PASSWORD ''your_password'' SUPERUSER; # if you want to be a superuser
postgres=> CREATE ROLE your_username LOGIN PASSWORD ''your_password'' NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION; # if you want to only be granted on one db
postgres=> CREATE DATABASE "your_db" WITH OWNER = your_username ENCODING = ''UTF8'';
```

Then you''ll be able to connect with this user like that:

```shell
$ psql -U your_username -W your_db
password:
your_db=> CREATE TABLE my_table(my_id INT);
your_db=> INSERT INTO my_table VALUES (1);
```

And if you need to connect from the outside:

```shell
psql -h {{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }} -U your_username -W your_db
```

And here''s a JDBC url you can use for your java applications:

```shell
jdbc:postgresql://{{ env_hashed_name }}.{{ environment }}.{{ root_dns_zone }}:5432/i4db
```

More informations in this [tutorial](https://doc.cloud.comwork.io/docs/tutorials/dbaas).
');


--
-- Name: environment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cloudapi
--

SELECT pg_catalog.setval('public.environment_id_seq', 18, true);


--
-- PostgreSQL database dump complete
--
