import nltk

from nltk.sentiment import SentimentIntensityAnalyzer

from adapters.ai.ModelAdapter import ModelAdapter
from schemas.Ai import PromptSchema
from utils.logger import log_msg

nltk.download('vader_lexicon')
_sia = SentimentIntensityAnalyzer()

class NltksentimentAdapter(ModelAdapter):
    def load_model(self):
        log_msg("INFO", "[NltksentimentAdapter][load_model] loading model...")

    def generate_response(self, prompt: PromptSchema):
        log_msg("DEBUG", "[NltksentimentAdapter][generate_response] prompt is {}".format(prompt))
        scores = _sia.polarity_scores(prompt.message)
        
        if scores['compound'] >= 0.05:
            sentiment = 'postive'
        elif scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return { "response": ["The predicted sentiment is: {}, score: {}".format(sentiment, scores['compound'])], "score": scores['compound'] }
