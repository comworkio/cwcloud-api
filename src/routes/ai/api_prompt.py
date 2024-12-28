from typing import Annotated
from fastapi import Depends, status, APIRouter, Response

from middleware.auth_guard import get_current_active_user
from middleware.cwaiapi_guard import cwaiapi_required
from schemas.User import UserSchema
from schemas.Ai import PromptSchema
from controllers.ai.prompt import generate_prompt

from utils.common import is_false
from utils.observability.otel import get_otel_tracer
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "ai-prompt"
_counter = create_counter("ai_prompt_api", "CW AI Prompt API counter")

@router.post("/prompt", status_code = status.HTTP_201_CREATED)
def create_prompt(current_user: Annotated[UserSchema, Depends(get_current_active_user)], cwai: Annotated[str, Depends(cwaiapi_required)], prompt: PromptSchema, response: Response):
    with get_otel_tracer().start_as_current_span("{}-{}".format(_span_prefix, Method.POST)):
        increment_counter(_counter, Method.POST)

        result = generate_prompt(prompt)
        if is_false(result['status']):
            response.status_code = int(result['status'])
        return result
