from fastapi import APIRouter

from exceptions.CwHTTPException import CwHTTPException

router = APIRouter()

@router.get("/400")
def generate_functional_ex():
    raise CwHTTPException(message = {"error": "functional error test", "i18n_code": "functional_error"}, status_code = 400)

@router.get("/500")
def generate_technical_ex():
    raise Exception("technical error test")
