import torch

from transformers import AutoModelForSequenceClassification, AutoTokenizer

from adapters.ai.ModelAdapter import ModelAdapter
from schemas.Ai import PromptSchema
from utils.ai.default_values import CWAI_LOW_CPU_MEM, CWAI_TOKENIZER_USE_FAST
from utils.logger import log_msg

_sentiment_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
_sentiment_model = AutoModelForSequenceClassification.from_pretrained(_sentiment_model_name, low_cpu_mem_usage = CWAI_LOW_CPU_MEM)
_sentiment_tokenizer = AutoTokenizer.from_pretrained(_sentiment_model_name, use_fast = CWAI_TOKENIZER_USE_FAST)

emotion_mapping = {
    1: 'anger',
    2: 'dislike',
    3: 'neutral',
    4: 'like',
    5: 'love'
}

class NlptownsentimentAdapter(ModelAdapter):
    def load_model(self):
        log_msg("INFO", "[NlptownsentimentAdapter][load_model] loading model...")

    def generate_response(self, prompt: PromptSchema):
        log_msg("DEBUG", "[NlptownsentimentAdapter][generate_response] prompt is {}".format(prompt))
        inputs = _sentiment_tokenizer(prompt.message, return_tensors="pt")
        outputs = _sentiment_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = torch.argmax(probs).item() + 1
        predicted_emotion = emotion_mapping[predicted_class]
        return {"response": ["The predicted emotion is: {}, score: {}".format(predicted_emotion, predicted_class)], "score": predicted_class}
