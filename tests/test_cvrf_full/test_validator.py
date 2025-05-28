from json import load
from pathlib import Path

from cvrf2csaf.validate import Validator


MINIMAL_DOCUMENT = {
    "document": {
        "csaf_version": "2.0",
        "category": "category",
        "title": "title",
        "publisher": {
            "category": "vendor",
            "name": "name",
            "namespace": "https://example.com",
        },
        "tracking": {
            "current_release_date": "2025-01-01T00:00:00.000+00:00",
            "initial_release_date": "2025-01-01T00:00:00.000+00:00",
            "id": "0",
            "revision_history": [
                {
                    "date": "2025-01-01T00:00:00.000+00:00",
                    "number": "0",
                    "summary": "text",
                }
            ],
            "status": "final",
            "version": "0",
        },
    }
}


def test_validator_empty():
    # a minimal, basically empty document that validates
    validator = Validator()
    result = validator.validate(MINIMAL_DOCUMENT)
    assert result[0] is True
    assert result[1] == []


def test_validator_cvrf_full():
    # invalid document
    document = load((Path(__file__).parent / "../../tests/test_cvrf_full/test_cvrf_full.json").open())
    validator = Validator()
    result = validator.validate(document)
    assert result[0] is False
    assert len(result[1]) > 0
