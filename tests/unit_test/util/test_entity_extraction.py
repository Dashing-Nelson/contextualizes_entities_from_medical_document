from unittest.mock import patch

import pytest

from app.util.text_context import extract_entities, get_context


def test_get_context():
    text = "This is a sample text with an entity in the middle."
    start, end = 27, 33  # "entity"

    context = get_context(text, start, end, window=10)

    assert context == "text with an entity in the"


def test_get_context_at_start():
    text = "Entity at the start."
    start, end = 0, 6  # "Entity"

    context = get_context(text, start, end, window=10)

    assert context == "Entity at the st"


def test_get_context_at_end():
    text = "Text ends with entity"
    start, end = 15, 21  # "entity"

    context = get_context(text, start, end, window=10)

    assert context == "ends with entity"  # Corrected assertion


def test_extract_entities_non_medical():
    text = "John Doe is a software engineer at Google."

    entities = extract_entities(text)

    assert entities == []


@patch("app.util.text_context.extract_entities_cached")
def test_extract_entities_medical(mock_extract_entities_cached):
    text = "John Doe has Covid-19 and is coughing."
    mock_extract_entities_cached.return_value = [
        {"word": "Covid-19", "start": 0, "end": 8, "entity_group": "Disease_disorder"},
        {"word": "Google", "start": 34, "end": 40, "entity_group": "other"},
    ]

    entities = extract_entities(text)

    assert entities == [
        {
            "context": "John Doe has Covid-19 and is coughing.",
            "end": 8,
            "entity": "Covid-19",
            "start": 0,
        }
    ]


def test_extract_entities_fails():
    with patch(
        "app.util.text_context.extract_entities_cached",
        side_effect=Exception("Mock Error"),
    ):
        with pytest.raises(ValueError, match="Entity extraction failed."):
            extract_entities("Some text here.")
