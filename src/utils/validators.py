"""Input validation utilities for YouTube SEO Tool.

Provides validation functions to catch errors early and prevent
invalid data from reaching APIs.
"""

import re
from typing import Optional


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


# Keyword constraints
MIN_KEYWORD_LENGTH = 1
MAX_KEYWORD_LENGTH = 100
INVALID_KEYWORD_PATTERN = re.compile(r'[<>"\{\}\[\]\\]')


def validate_keyword(keyword: str) -> str:
    """
    Validate and sanitize a keyword.

    Args:
        keyword: The keyword to validate

    Returns:
        Sanitized keyword (stripped of whitespace)

    Raises:
        ValidationError: If keyword is invalid
    """
    if not keyword:
        raise ValidationError("Keyword cannot be empty")

    # Strip whitespace
    keyword = keyword.strip()

    if len(keyword) < MIN_KEYWORD_LENGTH:
        raise ValidationError(
            f"Keyword must be at least {MIN_KEYWORD_LENGTH} character(s)"
        )

    if len(keyword) > MAX_KEYWORD_LENGTH:
        raise ValidationError(
            f"Keyword must be at most {MAX_KEYWORD_LENGTH} characters"
        )

    # Check for invalid characters
    if INVALID_KEYWORD_PATTERN.search(keyword):
        raise ValidationError(
            "Keyword contains invalid characters: < > \" { } [ ] \\"
        )

    return keyword


def validate_keywords(keywords: list[str]) -> list[str]:
    """
    Validate a list of keywords.

    Args:
        keywords: List of keywords to validate

    Returns:
        List of validated, deduplicated keywords

    Raises:
        ValidationError: If any keyword is invalid
    """
    if not keywords:
        raise ValidationError("At least one keyword is required")

    validated = []
    seen = set()

    for kw in keywords:
        clean = validate_keyword(kw)
        lower = clean.lower()
        if lower not in seen:
            seen.add(lower)
            validated.append(clean)

    return validated


def validate_api_key(api_key: Optional[str], name: str = "API key") -> str:
    """
    Validate an API key.

    Args:
        api_key: The API key to validate
        name: Name of the API key for error messages

    Returns:
        The API key (stripped)

    Raises:
        ValidationError: If API key is invalid
    """
    if not api_key:
        raise ValidationError(f"{name} is required")

    api_key = api_key.strip()

    if len(api_key) < 10:
        raise ValidationError(f"{name} appears to be invalid (too short)")

    return api_key


def validate_gap_score_threshold(score: float) -> float:
    """
    Validate a gap score threshold.

    Args:
        score: The score threshold

    Returns:
        The validated score

    Raises:
        ValidationError: If score is out of range
    """
    if not 0.0 <= score <= 10.0:
        raise ValidationError("Gap score must be between 0 and 10")

    return score


def validate_max_results(max_results: int, limit: int = 100) -> int:
    """
    Validate max results parameter.

    Args:
        max_results: The max results value
        limit: Upper bound for max results

    Returns:
        The validated max results

    Raises:
        ValidationError: If value is invalid
    """
    if max_results < 1:
        raise ValidationError("Max results must be at least 1")

    if max_results > limit:
        raise ValidationError(f"Max results cannot exceed {limit}")

    return max_results
