import pytest

from rag.scope_classifier import classify_scope


@pytest.mark.parametrize(
    "question",
    [
        "What is the current price of this car?",
        "What are fuel prices today?",
        "Will it rain tomorrow?",
        "Who will win the football game?",
        "Write Python code for me",
        "Book a service appointment",
        "Find the nearest service center",
        "Use my live location",
        "What is today's news?",
        "What do online ratings say?",
        "Tell me a cooking recipe",
    ],
)
def test_out_of_scope_categories(question):
    assert classify_scope(question) == "out_of_scope"


@pytest.mark.parametrize(
    "question",
    [
        "What does the TPMS warning light mean?",
        "How do I charge the battery?",
        "ما ضغط الإطارات؟",
    ],
)
def test_in_scope_manual_questions(question):
    assert classify_scope(question) == "in_scope"
