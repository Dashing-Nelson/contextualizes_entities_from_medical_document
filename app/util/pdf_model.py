import os

from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

from app.util.log import logger


class PDFModel:
    def __init__(self, model_dir: str, task: str, aggregation_strategy, device):
        # Resolve absolute path for models/
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        model_path = os.path.join(base_dir, "models", model_dir)
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForTokenClassification.from_pretrained(model_path)
            self.pipe = pipeline(
                task,
                model=model,
                tokenizer=tokenizer,
                aggregation_strategy=aggregation_strategy,
                device=device,
            )
            logger.info(f"Successfully loaded the {model_path} model.")
        except Exception as e:
            logger.error(f"Error loading {model_path} model: {e}")
            raise e

    def extract_entities(self, text):
        return self.pipe(text)
