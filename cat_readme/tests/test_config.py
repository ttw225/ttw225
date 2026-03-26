import dataclasses

import pytest

from config import VALID_ACTION, Action


class TestValidAction:
    def test_is_dict(self):
        assert isinstance(VALID_ACTION, dict)

    def test_expected_categories(self):
        assert set(VALID_ACTION.keys()) == {"eat", "play", "sleep", "fun"}

    def test_each_category_is_dict(self):
        for category, actions in VALID_ACTION.items():
            assert isinstance(actions, dict), f"{category} actions should be a dict"

    def test_each_name_and_emoji_are_strings(self):
        for category, actions in VALID_ACTION.items():
            for name, emoji in actions.items():
                assert isinstance(name, str), f"name in {category} should be str"
                assert isinstance(emoji, str), f"emoji in {category} should be str"

    @pytest.mark.parametrize(
        ("category", "expected_names"),
        [
            ("eat", ["Can", "Kibble"]),
            ("play", ["Catnip", "Cat_Teaser_Wand", "Box"]),
            ("sleep", ["Sleep_Well", "Angle", "Sun", "Blanket"]),
            ("fun", ["headgear"]),
        ],
    )
    def test_category_action_names(self, category: str, expected_names: list[str]):
        for name in expected_names:
            assert name in VALID_ACTION[category]

    def test_no_empty_names_or_emojis(self):
        for actions in VALID_ACTION.values():
            for name, emoji in actions.items():
                assert name, "action name should not be empty"
                assert emoji, "action emoji should not be empty"


class TestAction:
    def test_keyword_creation(self):
        action = Action(category="eat", name="Can")
        assert action.category == "eat"
        assert action.name == "Can"

    def test_positional_creation(self):
        action = Action("play", "Box")
        assert action.category == "play"
        assert action.name == "Box"

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(Action)

    def test_fields(self):
        fields = {f.name for f in dataclasses.fields(Action)}
        assert fields == {"category", "name"}

    def test_equality(self):
        a1 = Action("sleep", "Sun")
        a2 = Action("sleep", "Sun")
        assert a1 == a2

    def test_inequality(self):
        a1 = Action("sleep", "Sun")
        a2 = Action("sleep", "Blanket")
        assert a1 != a2

    def test_asdict(self):
        action = Action("eat", "Kibble")
        assert dataclasses.asdict(action) == {"category": "eat", "name": "Kibble"}

    def test_no_default_values(self):
        # Both fields are required; missing args should raise TypeError
        import pytest

        with pytest.raises(TypeError):
            Action()  # type: ignore[call-arg]

        with pytest.raises(TypeError):
            Action("eat")  # type: ignore[call-arg]
