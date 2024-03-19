from fastapi.responses import JSONResponse

from entities.kubernetes.Cluster import Cluster
from utils.kubernetes.k8s_management import get_dumped_json

def get_clusters_limited(current_user, db):
    clusters = Cluster.getAllForUser(db) 
    response = get_dumped_json(clusters)
    return JSONResponse(content = response, status_code = 200)
