from functools import lru_cache

from app.util.config import (
    KEEP_LABELS,
    huggingface_aggregation_strategy,
    huggingface_device,
    huggingface_model,
    huggingface_task,
)
from app.util.log import logger
from app.util.pdf_model import PDFModel

pdf_model = PDFModel(
    huggingface_model,
    huggingface_task,
    huggingface_aggregation_strategy,
    huggingface_device,
)


def get_context(text: str, start: int, end: int, window: int = 32) -> str:
    """
    Extracts a snippet of text around the entity.
    """
    # Calculate the starting index ensuring it doesn't go below 0.
    snippet_start = max(0, start - window)
    # Calculate the ending index ensuring it doesn't exceed the length of the text.
    snippet_end = min(len(text), end + window)
    return text[snippet_start:snippet_end]


@lru_cache(maxsize=128)
def extract_entities_cached(text: str):
    """
    Caches the entity extraction result for repeated text inputs.
    """
    return pdf_model.extract_entities(text)


def extract_entities(text: str):
    """
    Extracts entities using the Hugging Face pipeline and provides context.
    Returns a list of dictionaries with keys: entity, context, start, and end.
    """
    try:
        # Extract entities from the text using the cached extraction function.
        ner_results = extract_entities_cached(text)
        entities = []
        # Iterate through each entity result.
        for entity in ner_results:
            label = entity.get("entity_group", None)
            start = entity["start"]
            end = entity["end"]
            if label in KEEP_LABELS:
                # Retrieve a snippet of context around the entity.
                context_snippet = get_context(text, start, end)
                # Append the entity data to the list.
                entities.append(
                    {
                        "entity": entity["word"],
                        "context": context_snippet,
                        "start": start,
                        "end": end,
                    }
                )
        return entities
    except Exception as e:
        logger.exception("Error during entity extraction.")
        raise ValueError("Entity extraction failed.") from e
