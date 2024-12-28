from typing import Optional

from pydantic import BaseModel

class PromptSettingsSchema(BaseModel):
    max_length: Optional[int]
    num_return_sequences: Optional[int]
    no_repeat_ngram_size: Optional[int]
    early_stopping: Optional[bool] = True
    do_sample: Optional[bool] = True
    skip_special_tokens: Optional[bool] = True
    top_k: Optional[int]
    top_p: Optional[float]
    temperature: Optional[float]

class PromptSchema(BaseModel):
    model: str
    message: str
    settings: Optional[PromptSettingsSchema]
