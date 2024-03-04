ALTER TABLE public.project ADD COLUMN IF NOT EXISTS type VARCHAR(25) NOT NULL DEFAULT 'vm' CHECK (type IN ('k8s', 'vm')) ;
ALTER TABLE public.environment ADD COLUMN IF NOT EXISTS type VARCHAR(25) NOT NULL DEFAULT 'vm' CHECK (type IN ('k8s', 'vm')) ;
ALTER TABLE public.environment ADD COLUMN IF NOT EXISTS external_roles TEXT;

CREATE TABLE IF NOT EXISTS k8s_kubeconfig_files (
    id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL,
    content BYTEA NOT NULL,
    created_at varchar(100) NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES public.user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS k8s_cluster (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    kubeconfig_file_id INT NOT NULL,
    version VARCHAR(100) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    created_at varchar(100) NOT NULL,
    FOREIGN KEY (kubeconfig_file_id) REFERENCES public.k8s_kubeconfig_files(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS k8s_deployment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hash VARCHAR(10) NOT NULL,
    description TEXT,
    cluster_id INT NOT NULL,
    project_id INT NOT NULL,
    env_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at varchar(100) NOT NULL,
    FOREIGN KEY (cluster_id) REFERENCES public.k8s_cluster(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES public.project(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES public.user(id) ON DELETE CASCADE,
    FOREIGN KEY (env_id) REFERENCES public.environment(id)
);