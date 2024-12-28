from textblob import TextBlob

from adapters.ai.ModelAdapter import ModelAdapter
from schemas.Ai import PromptSchema
from utils.logger import log_msg

class TextblobsentimentAdapter(ModelAdapter):
    def load_model(self):
        log_msg("INFO", "[TextblobsentimentAdapter][load_model] loading model...")

    def generate_response(self, prompt: PromptSchema):
        log_msg("DEBUG", "[TextblobsentimentAdapter][generate_response] prompt is {}".format(prompt))
        blob = TextBlob(prompt.message)
        polarity = blob.sentiment.polarity
        
        if polarity > 0:
            sentiment = 'postive'
        elif polarity < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return { "response": ["The predicted sentiment is: {}, score: {}".format(sentiment, polarity)], "score": polarity }
