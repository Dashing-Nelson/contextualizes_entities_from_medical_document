import pytest

from app.util.text_context import extract_entities
from tests.integration_test.data.results import result_for_entity


@pytest.mark.integration
def test_extract_entities_filters_unwanted_labels():
    """
    Integration test that verifies the extract_entities function
    only returns entities matching the 'keep' labels
    """

    text = (
        "College of\nPhysicians and Surgeons of Columbia University, New York, NY, United States\n"
        "Some patients remain unwell for months after “recovering” from acute COVID-\n19. They develop persistent "
        "fatigue, cognitive problems, headaches, disrupted\nsleep, myalgias and arthralgias, post-exertional "
        "malaise, orthostatic intolerance\nand other symptoms that greatly interfere with their ability to "
        "function and that\ncan leave som. open access June 5, 2023"
    )

    results = extract_entities(text)

    # We expect to see:
    #  - 'fatigue' -> Sign_symptom
    #  - 'chronic fatigue syndrome' -> Disease_disorder (depending on model specifics)
    #
    # We do NOT want:
    #  - 'June 5, 2023' -> Date
    #  - 'open access' -> Detailed_description (or some other irrelevant label)

    # 1) Make sure the function returns something
    assert results == result_for_entity
