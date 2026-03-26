import pathlib
import re
from urllib.parse import quote, parse_qs, urlsplit

import pytest

from config import Action
from content_builder import CAT_IMAGE_SIZE_PX, Content

IMG_TAG_PATTERN = re.compile(
    r"<img src='\./assets/image/"
    r"(?P<category>[^/]+)/(?P<name>[^']+)\.gif' "
    r"alt=cat_(?P=category)_(?P<alt_name>[^\s]+) "
    r"width='(?P<size>\d+)' height='(?P<size2>\d+)' />"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_content(action: Action, tmp_path: pathlib.Path) -> Content:
    """Create a Content instance with root set so participants.txt is resolvable.

    Content opens `root / "../participants.txt"`, so participants.txt lives at
    tmp_path and root = tmp_path / "src" (which must exist for OS path resolution).
    """
    src_dir = tmp_path / "src"
    src_dir.mkdir(exist_ok=True)
    (tmp_path / "participants.txt").write_text("alice\nbob\nalice\n", encoding="utf-8")
    return Content(src_dir, action)


# ---------------------------------------------------------------------------
# generate_status
# ---------------------------------------------------------------------------


class TestGenerateStatus:
    @pytest.mark.parametrize(
        ("action", "expected_fragment"),
        [
            (Action("sleep", "Sleep_Well"), "Sleeping... Zzz"),
            (Action("play", "Catnip"), "Playing with Catnip !"),
            (Action("eat", "Can"), "Eating a Can"),
            (Action("fun", "headgear"), "easter egg"),
        ],
    )
    def test_known_categories_include_expected_fragment(
        self, action: Action, expected_fragment: str, tmp_path: pathlib.Path
    ):
        c = make_content(action, tmp_path)
        result = c.generate_status()
        assert result.startswith("Cat is")
        assert expected_fragment in result

    def test_play_underscores_are_replaced(self, tmp_path: pathlib.Path):
        c = make_content(Action("play", "Cat_Teaser_Wand"), tmp_path)
        result = c.generate_status()
        assert "Cat Teaser Wand" in result
        assert "_" not in result

    def test_unknown_category_returns_partial_string(self, tmp_path: pathlib.Path):
        c = make_content(Action("unknown", "thing"), tmp_path)
        result = c.generate_status()
        assert result == "Cat is "

    def test_all_results_start_with_cat_is(self, tmp_path: pathlib.Path):
        for category, names in [("sleep", ["Sleep_Well"]), ("play", ["Box"]), ("eat", ["Can"]), ("fun", ["headgear"])]:
            c = make_content(Action(category, names[0]), tmp_path)
            assert c.generate_status().startswith("Cat is")


# ---------------------------------------------------------------------------
# generate_img_path
# ---------------------------------------------------------------------------


class TestGenerateImgPath:
    @pytest.mark.parametrize(
        ("action", "expected_category", "expected_name"),
        [
            (Action("sleep", "Sleep_Well"), "sleep", "Sleep_Well"),
            (Action("eat", "Can"), "eat", "Can"),
        ],
    )
    def test_img_tag_attributes(
        self,
        action: Action,
        expected_category: str,
        expected_name: str,
        tmp_path: pathlib.Path,
    ):
        c = make_content(action, tmp_path)
        result = c.generate_img_path()
        match = IMG_TAG_PATTERN.search(result)
        assert match is not None, f"Unexpected img tag format: {result}"

        assert match.group("category") == expected_category
        assert match.group("name") == expected_name
        assert match.group("alt_name") == expected_name
        assert match.group("size") == str(CAT_IMAGE_SIZE_PX)
        assert match.group("size2") == str(CAT_IMAGE_SIZE_PX)

    def test_single_line_no_newlines(self, play_action: Action, tmp_path: pathlib.Path):
        c = make_content(play_action, tmp_path)
        result = c.generate_img_path()
        assert "\n" not in result


# ---------------------------------------------------------------------------
# create_issue_link (static)
# ---------------------------------------------------------------------------


class TestCreateIssueLink:
    def test_uses_emoji_as_default_text(self):
        result = Content.create_issue_link("eat", "Can")
        assert "🥫" in result

    def test_custom_text_overrides_emoji(self):
        result = Content.create_issue_link("eat", "Can", text="Feed me")
        assert "[Feed me]" in result
        assert "🥫" not in result

    def test_title_contains_category_and_name(self):
        result = Content.create_issue_link("play", "Box")
        issue_url = result.split("](", 1)[1].rstrip(")")
        query = parse_qs(urlsplit(issue_url).query)
        assert query["title"] == ["cat|play|Box"]

    def test_labels_are_capitalized(self):
        result = Content.create_issue_link("sleep", "Sun")
        issue_url = result.split("](", 1)[1].rstrip(")")
        query = parse_qs(urlsplit(issue_url).query)
        assert query["labels"] == ["Sleep"]

    def test_points_to_github_issues(self):
        result = Content.create_issue_link("eat", "Kibble")
        assert "github.com/ttw225/ttw225/issues/new" in result

    def test_is_markdown_link(self):
        result = Content.create_issue_link("fun", "headgear")
        assert result.startswith("[")
        assert "](" in result
        assert result.endswith(")")


# ---------------------------------------------------------------------------
# create_badge (static)
# ---------------------------------------------------------------------------


class TestCreateBadge:
    def test_badge_markdown_and_url_are_structured(self):
        label = "PLAY"
        message = "🍀 Catnip"
        color = "8e44ad"
        result = Content.create_badge(label, message, color)

        left, url_and_paren = result.split("](", 1)
        alt_text = left[len("![") :]
        url = url_and_paren.rstrip(")")

        assert alt_text == f"{label} {message}"

        parsed = urlsplit(url)
        assert parsed.netloc == "img.shields.io"
        assert parsed.query
        query = parse_qs(parsed.query)
        assert query["style"] == ["for-the-badge"]

        encoded_label = quote(label)
        encoded_message = quote(message)
        assert parsed.path == f"/badge/{encoded_label}-{encoded_message}-{color}"


# ---------------------------------------------------------------------------
# generate_control_panel
# ---------------------------------------------------------------------------


class TestGenerateControlPanel:
    def test_is_markdown_table(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = make_content(sleep_action, tmp_path)
        result = c.generate_control_panel()
        assert "|" in result
        assert ":---" in result

    @pytest.mark.parametrize("header", ["Play", "Sleep", "Eat"])
    def test_contains_category_headers(self, sleep_action: Action, tmp_path: pathlib.Path, header: str):
        c = make_content(sleep_action, tmp_path)
        assert header in c.generate_control_panel()

    def test_contains_issue_links(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = make_content(sleep_action, tmp_path)
        result = c.generate_control_panel()
        assert "github.com/ttw225/ttw225/issues/new" in result

    def test_contains_badge_images(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = make_content(sleep_action, tmp_path)
        result = c.generate_control_panel()
        assert "img.shields.io/badge/" in result

    def test_no_leading_whitespace_on_first_line(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = make_content(sleep_action, tmp_path)
        result = c.generate_control_panel()
        assert not result.startswith(" ")
        assert not result.startswith("\t")


# ---------------------------------------------------------------------------
# generate_egg
# ---------------------------------------------------------------------------


class TestGenerateEgg:
    def test_is_html_comment(self, fun_action: Action, tmp_path: pathlib.Path):
        c = make_content(fun_action, tmp_path)
        result = c.generate_egg()
        assert result.startswith("<!--")
        assert result.endswith("-->")

    def test_contains_issue_link(self, fun_action: Action, tmp_path: pathlib.Path):
        c = make_content(fun_action, tmp_path)
        result = c.generate_egg()
        assert "github.com" in result

    def test_references_headgear(self, fun_action: Action, tmp_path: pathlib.Path):
        c = make_content(fun_action, tmp_path)
        result = c.generate_egg()
        assert "headgear" in result


# ---------------------------------------------------------------------------
# generate_user_list
# ---------------------------------------------------------------------------


class TestGenerateUserList:
    def _make_with_participants(self, content: str, tmp_path: pathlib.Path, action: Action) -> Content:
        src_dir = tmp_path / "src"
        src_dir.mkdir(exist_ok=True)
        (tmp_path / "participants.txt").write_text(content, encoding="utf-8")
        return Content(src_dir, action)

    def test_latest_table_header(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("alice\n", tmp_path, sleep_action)
        latest, _ = c.generate_user_list()
        assert "| user |" in latest
        assert "| :---: |" in latest

    def test_top_table_header(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("alice\n", tmp_path, sleep_action)
        _, top = c.generate_user_list()
        assert "| times | user |" in top
        assert "| :---: | :---: |" in top

    def test_latest_contains_user_links(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("alice\nbob\n", tmp_path, sleep_action)
        latest, _ = c.generate_user_list()
        assert "[alice](https://github.com/alice)" in latest
        assert "[bob](https://github.com/bob)" in latest

    def test_top_contains_counts(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("alice\nalice\nalice\nbob\nbob\n", tmp_path, sleep_action)
        _, top = c.generate_user_list()
        assert "3" in top
        assert "2" in top

    def test_latest_order_is_insertion_order(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("charlie\nalice\nbob\n", tmp_path, sleep_action)
        latest, _ = c.generate_user_list()
        charlie_pos = latest.index("charlie")
        alice_pos = latest.index("alice")
        bob_pos = latest.index("bob")
        assert charlie_pos < alice_pos < bob_pos

    def test_top_is_sorted_by_count_descending(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("bob\nbob\nbob\nalice\nalice\n", tmp_path, sleep_action)
        _, top = c.generate_user_list()
        bob_pos = top.index("bob")
        alice_pos = top.index("alice")
        assert bob_pos < alice_pos

    def test_latest_capped_at_20(self, sleep_action: Action, tmp_path: pathlib.Path):
        users = "\n".join(f"user{i}" for i in range(30))
        c = self._make_with_participants(users, tmp_path, sleep_action)
        latest, _ = c.generate_user_list()
        assert latest.count("github.com") == 20

    def test_top_capped_at_20(self, sleep_action: Action, tmp_path: pathlib.Path):
        users = "\n".join(f"user{i}" for i in range(30))
        c = self._make_with_participants(users, tmp_path, sleep_action)
        _, top = c.generate_user_list()
        assert top.count("github.com") == 20

    def test_empty_participants_file(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("", tmp_path, sleep_action)
        latest, top = c.generate_user_list()
        assert "| user |" in latest
        assert "| times | user |" in top

    def test_duplicate_user_appears_once_in_latest(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("alice\nalice\nalice\n", tmp_path, sleep_action)
        latest, _ = c.generate_user_list()
        assert latest.count("[alice]") == 1

    def test_tie_keeps_first_seen_order(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("bob\nalice\nalice\nbob\n", tmp_path, sleep_action)
        _, top = c.generate_user_list()
        assert top.index("bob") < top.index("alice")

    def test_blank_lines_are_ignored(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants("alice\n\nbob\n", tmp_path, sleep_action)
        latest, top = c.generate_user_list()
        assert "[](https://github.com/)" not in latest
        assert "[](https://github.com/)" not in top
        assert "[alice](https://github.com/alice)" in latest
        assert "[bob](https://github.com/bob)" in latest

    def test_user_ids_are_trimmed(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = self._make_with_participants(" alice \n", tmp_path, sleep_action)
        latest, _ = c.generate_user_list()
        assert "[alice](https://github.com/alice)" in latest


# ---------------------------------------------------------------------------
# build_content (integration)
# ---------------------------------------------------------------------------


class TestBuildContent:
    def test_contains_core_sections(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = make_content(sleep_action, tmp_path)
        result = c.build_content()
        assert "Cat is" in result
        assert "<img " in result
        assert "## Control Panel" in result
        assert "## Latest Participants" in result
        assert "LeaderBoard" in result
        assert "<!--" in result

    def test_template_has_no_unreplaced_placeholders(self, eat_action: Action, tmp_path: pathlib.Path):
        c = make_content(eat_action, tmp_path)
        result = c.build_content()
        assert "${" not in result

    def test_participants_appear_in_output(self, sleep_action: Action, tmp_path: pathlib.Path):
        c = make_content(sleep_action, tmp_path)
        result = c.build_content()
        assert "alice" in result
        assert "bob" in result
