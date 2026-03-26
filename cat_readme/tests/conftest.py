import pytest

from config import Action


@pytest.fixture
def sleep_action() -> Action:
    return Action("sleep", "Sleep_Well")


@pytest.fixture
def eat_action() -> Action:
    return Action("eat", "Can")


@pytest.fixture
def play_action() -> Action:
    return Action("play", "Catnip")


@pytest.fixture
def fun_action() -> Action:
    return Action("fun", "headgear")
