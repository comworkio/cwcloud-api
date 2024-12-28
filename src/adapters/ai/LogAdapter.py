from adapters.ai.ModelAdapter import ModelAdapter
from schemas.Ai import PromptSchema
from utils.logger import log_msg

class LogAdapter(ModelAdapter):
    def load_model(self):
        log_msg("INFO", "[LogAdapter][load_model] loading model...")

    def generate_response(self, prompt: PromptSchema):
        log_msg("DEBUG", "[LogAdapter][generate_response] prompt is {}".format(prompt))
        return { "response": ["Log response for prompt = {}".format(prompt)] }
