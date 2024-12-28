from transformers import GPT2LMHeadModel, GPT2Tokenizer

from adapters.ai.ModelAdapter import ModelAdapter
from schemas.Ai import PromptSchema
from utils.logger import log_msg
from utils.ai.transformers_utils import get_response

_gpt2_model_name = 'gpt2'
_gpt2_tokenizer = GPT2Tokenizer.from_pretrained(_gpt2_model_name)
_gpt2_model = GPT2LMHeadModel.from_pretrained(_gpt2_model_name)

class Gpt2Adapter(ModelAdapter):
    def load_model(self):
        log_msg("INFO", "[Gpt2Adapter][load_model] loading model...")

    def generate_response(self, prompt: PromptSchema):
        log_msg("DEBUG", "[Gpt2Adapter][generate_response] prompt is {}".format(prompt))
        return get_response(prompt, _gpt2_tokenizer, _gpt2_model)
