from fastapi import status, APIRouter

router = APIRouter()

@router.get("", status_code = status.HTTP_200_OK)
def get_health():
    return {
        'status': 'ok',
        'alive': True
    }
