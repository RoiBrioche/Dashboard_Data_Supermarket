"""
Example test file to demonstrate the testing framework
"""

import pytest


def test_example():
    """Example test function."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    text = "Hello, World!"
    assert text.startswith("Hello")
    assert text.endswith("!")
    assert "," in text


@pytest.mark.parametrize("input_val,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_square(input_val, expected):
    """Test square function with parameterized inputs."""
    result = input_val ** 2
    assert result == expected
