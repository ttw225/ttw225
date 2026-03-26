import json
import pathlib

import pytest

from build_readme import BuildReadme, parse_argv
from config import Action


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_br(action: Action, tmp_path: pathlib.Path) -> BuildReadme:
    """Create a BuildReadme instance with all paths pointing into tmp_path."""
    br = BuildReadme(user_action=action)
    br.readme_path = tmp_path / "README.md"
    br.status_path = tmp_path / "status.json"
    return br


# ---------------------------------------------------------------------------
# replace_chunk (static method, no I/O)
# ---------------------------------------------------------------------------


class TestReplaceChunk:
    def test_basic_replacement(self):
        content = "<!-- output starts -->\nold content\n<!-- output ends -->"
        result = BuildReadme.replace_chunk(content, "output", "new content")
        assert "<!-- output starts -->" in result
        assert "new content" in result
        assert "<!-- output ends -->" in result
        assert "old content" not in result

    def test_replaces_multiline_old_content(self):
        content = "<!-- section starts -->\nline1\nline2\nline3\n<!-- section ends -->"
        result = BuildReadme.replace_chunk(content, "section", "replaced")
        assert "replaced" in result
        assert "line1" not in result
        assert "line2" not in result

    def test_preserves_surrounding_text(self):
        content = "header\n<!-- output starts -->\nold\n<!-- output ends -->\nfooter"
        result = BuildReadme.replace_chunk(content, "output", "new")
        assert "header" in result
        assert "footer" in result

    def test_no_match_returns_unchanged(self):
        content = "no markers here"
        result = BuildReadme.replace_chunk(content, "output", "new")
        assert result == content

    def test_idempotent(self):
        """Replacing the same marker twice with the same chunk is a no-op."""
        content = "<!-- output starts -->\nold\n<!-- output ends -->"
        first = BuildReadme.replace_chunk(content, "output", "new content")
        second = BuildReadme.replace_chunk(first, "output", "new content")
        assert first == second

    def test_different_markers_are_independent(self):
        content = (
            "<!-- alpha starts -->\nalpha old\n<!-- alpha ends -->\n"
            "<!-- beta starts -->\nbeta old\n<!-- beta ends -->"
        )
        result = BuildReadme.replace_chunk(content, "alpha", "alpha new")
        assert "alpha new" in result
        assert "beta old" in result

    def test_chunk_inserted_between_markers(self):
        content = "<!-- out starts -->\n<!-- out ends -->"
        result = BuildReadme.replace_chunk(content, "out", "injected")
        assert result == "<!-- out starts -->\ninjected\n<!-- out ends -->"

    def test_multiple_same_markers_replace_only_first_block(self):
        content = (
            "A\n"
            "<!-- output starts -->\nold-1\n<!-- output ends -->\n"
            "B\n"
            "<!-- output starts -->\nold-2\n<!-- output ends -->\n"
            "C"
        )
        result = BuildReadme.replace_chunk(content, "output", "new")
        expected = (
            "A\n"
            "<!-- output starts -->\nnew\n<!-- output ends -->\n"
            "B\n"
            "<!-- output starts -->\nold-2\n<!-- output ends -->\n"
            "C"
        )
        assert result == expected


# ---------------------------------------------------------------------------
# check_update
# ---------------------------------------------------------------------------


class TestCheckUpdate:
    def test_returns_false_when_status_matches(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text(json.dumps({"category": "sleep", "name": "Sleep_Well"}), encoding="utf-8")
        assert br.check_update() is False

    def test_returns_true_when_category_differs(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text(json.dumps({"category": "eat", "name": "Sleep_Well"}), encoding="utf-8")
        assert br.check_update() is True

    def test_returns_true_when_name_differs(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text(json.dumps({"category": "sleep", "name": "Sun"}), encoding="utf-8")
        assert br.check_update() is True

    def test_returns_true_when_status_is_empty_dict(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text(json.dumps({}), encoding="utf-8")
        assert br.check_update() is True

    def test_returns_true_when_status_has_extra_fields(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text(
            json.dumps({"category": "sleep", "name": "Sleep_Well", "extra": "field"}),
            encoding="utf-8",
        )
        assert br.check_update() is True

    def test_raises_when_status_file_missing(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        with pytest.raises(FileNotFoundError):
            br.check_update()

    def test_raises_when_status_json_invalid(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text("{not-json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            br.check_update()


# ---------------------------------------------------------------------------
# do_action
# ---------------------------------------------------------------------------


class TestDoAction:
    def test_returns_string(self, sleep_action: Action, tmp_path: pathlib.Path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (tmp_path / "participants.txt").write_text("alice\n", encoding="utf-8")
        br = BuildReadme(user_action=sleep_action)
        br.readme_path = tmp_path / "README.md"
        br.status_path = tmp_path / "status.json"
        # Override ROOT-based Content construction by monkeypatching the module-level ROOT
        import build_readme as br_module
        original_root = br_module.ROOT
        br_module.ROOT = src_dir
        try:
            result = br.do_action()
        finally:
            br_module.ROOT = original_root
        assert isinstance(result, str)
        assert "Cat is" in result


# ---------------------------------------------------------------------------
# load_readme / write_readme / write_status
# ---------------------------------------------------------------------------


class TestLoadReadme:
    def test_loads_content(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.readme_path.write_text("hello readme", encoding="utf-8")
        br.load_readme()
        assert br.readme == "hello readme"

    def test_raises_when_readme_missing(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        with pytest.raises(FileNotFoundError):
            br.load_readme()


class TestWriteReadme:
    def test_writes_readme_attribute(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.readme_path.write_text("", encoding="utf-8")
        br.readme = "new content"
        br.write_readme()
        assert br.readme_path.read_text(encoding="utf-8") == "new content"


class TestWriteStatus:
    def test_writes_action_as_json(self, eat_action: Action, tmp_path: pathlib.Path):
        br = make_br(eat_action, tmp_path)
        br.status_path.write_text("{}", encoding="utf-8")
        br.write_status()
        data = json.loads(br.status_path.read_text(encoding="utf-8"))
        assert data == {"category": "eat", "name": "Can"}

    def test_overwrites_previous_status(self, sleep_action: Action, eat_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text(json.dumps({"category": "sleep", "name": "Sleep_Well"}), encoding="utf-8")
        br.action = eat_action
        br.write_status()
        data = json.loads(br.status_path.read_text(encoding="utf-8"))
        assert data == {"category": "eat", "name": "Can"}


# ---------------------------------------------------------------------------
# update (integration: combines check_update, do_action, write_*)
# ---------------------------------------------------------------------------


class TestUpdate:
    def test_no_write_when_status_unchanged(self, sleep_action: Action, tmp_path: pathlib.Path):
        br = make_br(sleep_action, tmp_path)
        br.status_path.write_text(json.dumps({"category": "sleep", "name": "Sleep_Well"}), encoding="utf-8")
        original = "original readme content"
        br.readme_path.write_text(original, encoding="utf-8")

        br.update()

        assert br.readme_path.read_text(encoding="utf-8") == original

    def test_writes_readme_and_status_when_changed(
        self, eat_action: Action, tmp_path: pathlib.Path, mocker
    ):
        br = make_br(eat_action, tmp_path)
        br.status_path.write_text(json.dumps({"category": "sleep", "name": "Sleep_Well"}), encoding="utf-8")
        br.readme_path.write_text(
            "before\n<!-- output starts -->\nold\n<!-- output ends -->\nafter",
            encoding="utf-8",
        )
        mocker.patch.object(br, "do_action", return_value="generated content")

        br.update()

        readme_text = br.readme_path.read_text(encoding="utf-8")
        assert "generated content" in readme_text
        assert "old" not in readme_text

        status = json.loads(br.status_path.read_text(encoding="utf-8"))
        assert status == {"category": "eat", "name": "Can"}

    def test_surrounding_readme_content_preserved(
        self, eat_action: Action, tmp_path: pathlib.Path, mocker
    ):
        br = make_br(eat_action, tmp_path)
        br.status_path.write_text(json.dumps({"category": "sleep", "name": "Sleep_Well"}), encoding="utf-8")
        br.readme_path.write_text(
            "HEADER\n<!-- output starts -->\nold\n<!-- output ends -->\nFOOTER",
            encoding="utf-8",
        )
        mocker.patch.object(br, "do_action", return_value="new chunk")

        br.update()

        readme_text = br.readme_path.read_text(encoding="utf-8")
        assert "HEADER" in readme_text
        assert "FOOTER" in readme_text


# ---------------------------------------------------------------------------
# parse_argv
# ---------------------------------------------------------------------------


class TestParseArgv:
    @pytest.mark.parametrize(
        ("argv", "expected_category", "expected_name"),
        [
            ("cat|eat|Can", "eat", "Can"),
            ("cat|play|Box", "play", "Box"),
            ("cat|sleep|Sleep_Well", "sleep", "Sleep_Well"),
            ("cat|fun|headgear", "fun", "headgear"),
            ("dog|eat|Can", "sleep", "Sleep_Well"),
            ("cat|eat| can ", "sleep", "Sleep_Well"),
            ("cat|Eat|Can", "sleep", "Sleep_Well"),
            ("cat|eat|nonexistent", "sleep", "Sleep_Well"),
            ("cat|badcat|Can", "sleep", "Sleep_Well"),
            ("not_pipe_separated", "sleep", "Sleep_Well"),
            ("cat|eat|Can|extra", "sleep", "Sleep_Well"),
            ("", "sleep", "Sleep_Well"),
        ],
    )
    def test_parse_argv_contract(self, argv: str, expected_category: str, expected_name: str):
        action = parse_argv(argv)
        assert action.category == expected_category
        assert action.name == expected_name
