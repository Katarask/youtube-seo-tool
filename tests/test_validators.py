"""Tests for input validation."""

import pytest

from src.utils.validators import (
    ValidationError,
    validate_keyword,
    validate_keywords,
    validate_api_key,
    validate_gap_score_threshold,
    validate_max_results,
)


class TestValidateKeyword:
    """Tests for keyword validation."""

    def test_valid_keyword(self):
        """Test valid keyword passes."""
        result = validate_keyword("python tutorial")
        assert result == "python tutorial"

    def test_strips_whitespace(self):
        """Test whitespace is stripped."""
        result = validate_keyword("  python tutorial  ")
        assert result == "python tutorial"

    def test_empty_keyword_raises(self):
        """Test empty keyword raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_keyword("")

    def test_none_keyword_raises(self):
        """Test None keyword raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_keyword(None)

    def test_too_long_keyword_raises(self):
        """Test keyword over 100 chars raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_keyword("a" * 101)

    def test_invalid_characters_raises(self):
        """Test invalid characters raise ValidationError."""
        invalid_keywords = [
            "test<script>",
            "test>alert",
            'test"quote',
            "test{brace}",
            "test[bracket]",
            "test\\backslash",
        ]
        for keyword in invalid_keywords:
            with pytest.raises(ValidationError):
                validate_keyword(keyword)


class TestValidateKeywords:
    """Tests for multiple keyword validation."""

    def test_valid_keywords(self):
        """Test valid keyword list passes."""
        result = validate_keywords(["python", "javascript", "rust"])
        assert result == ["python", "javascript", "rust"]

    def test_deduplicates_keywords(self):
        """Test duplicate keywords are removed."""
        result = validate_keywords(["Python", "python", "PYTHON"])
        assert len(result) == 1

    def test_empty_list_raises(self):
        """Test empty list raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_keywords([])

    def test_invalid_keyword_in_list_raises(self):
        """Test invalid keyword in list raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_keywords(["valid", "", "also valid"])


class TestValidateApiKey:
    """Tests for API key validation."""

    def test_valid_api_key(self):
        """Test valid API key passes."""
        result = validate_api_key("AIzaSyA1234567890abcdef")
        assert result == "AIzaSyA1234567890abcdef"

    def test_strips_whitespace(self):
        """Test whitespace is stripped."""
        result = validate_api_key("  AIzaSyA1234567890abcdef  ")
        assert result == "AIzaSyA1234567890abcdef"

    def test_empty_api_key_raises(self):
        """Test empty API key raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_api_key("")

    def test_none_api_key_raises(self):
        """Test None API key raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_api_key(None)

    def test_too_short_api_key_raises(self):
        """Test API key under 10 chars raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_api_key("short")


class TestValidateGapScoreThreshold:
    """Tests for gap score threshold validation."""

    def test_valid_threshold(self):
        """Test valid threshold passes."""
        assert validate_gap_score_threshold(5.0) == 5.0
        assert validate_gap_score_threshold(0.0) == 0.0
        assert validate_gap_score_threshold(10.0) == 10.0

    def test_negative_threshold_raises(self):
        """Test negative threshold raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_gap_score_threshold(-1.0)

    def test_over_10_threshold_raises(self):
        """Test threshold over 10 raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_gap_score_threshold(11.0)


class TestValidateMaxResults:
    """Tests for max results validation."""

    def test_valid_max_results(self):
        """Test valid max results passes."""
        assert validate_max_results(10) == 10
        assert validate_max_results(1) == 1
        assert validate_max_results(100) == 100

    def test_zero_raises(self):
        """Test zero raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_max_results(0)

    def test_negative_raises(self):
        """Test negative raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_max_results(-1)

    def test_over_limit_raises(self):
        """Test over limit raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_max_results(101, limit=100)
