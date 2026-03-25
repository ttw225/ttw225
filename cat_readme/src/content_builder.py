import inspect
import logging
import pathlib
from collections import Counter
from string import Template
from typing import Dict, List, Tuple
from urllib.parse import quote, urlencode

from config import VALID_ACTION, Action

CAT_IMAGE_SIZE_PX = 240

CONTENT_TEMPLATE = """
${cat_status}

${cat_img}

## Control Panel

### How to interact
1. Choose a category: Play, Sleep, or Eat.
2. Click an action button.
3. Submit the pre-filled issue.

${control_panel}

${egg}

## Latest Participants

${latest_participants}

## Top 20 LeaderBoard: 黑糖's Best Friends

${top_participants}

"""


class Content:
    def __init__(self, root: pathlib.Path, action: Action) -> None:
        self.root: pathlib.Path = root
        self.action: Action = action

    def build_content(self) -> str:
        latest_participants, top_participants = self.generate_user_list()
        data: Dict[str, str] = {
            "cat_status": self.generate_status(),
            "cat_img": self.generate_img_path(),
            "control_panel": self.generate_control_panel(),
            "egg": self.generate_egg(),
            "latest_participants": latest_participants,
            "top_participants": top_participants,
        }
        return Template(CONTENT_TEMPLATE).substitute(data)

    def generate_status(self) -> str:
        status: str = ""
        match (self.action.category):
            case "sleep":
                status = "Sleeping... Zzz"
            case "play":
                status = f"Playing with {self.action.name.replace('_', ' ')} !"
            case "eat":
                status = f"Eating a {self.action.name.replace('_', ' ')} 😋"
            case "fun":
                status = "entertaining everyone XD\n\n*(Secret) Someone found this easter egg!!*"
            case _:
                logging.warning(f"[Generate Status] category: {self.action.category}")
        return f"Cat is {status}"

    def generate_img_path(self) -> str:
        image_md: str = (
            f"<img src='./assets/image/{self.action.category}/{self.action.name}.gif' "
            f"alt=cat_{self.action.category}_{self.action.name} "
            f"width='{CAT_IMAGE_SIZE_PX}' height='{CAT_IMAGE_SIZE_PX}' />"
        )
        return inspect.cleandoc(image_md)

    def generate_control_panel(self) -> str:
        def readable_name(name: str) -> str:
            return name.replace("_", " ")

        def create_button_group(category: str) -> str:
            category_colors: Dict[str, str] = {
                "play": "8e44ad",
                "sleep": "2c3e50",
                "eat": "16a085",
            }
            buttons: List[str] = [
                self.create_issue_link(
                    category,
                    name,
                    text=self.create_badge(
                        label=f"{category.upper()}",
                        message=f"{VALID_ACTION[category][name]} {readable_name(name)}",
                        color=category_colors[category],
                    ),
                )
                for name in VALID_ACTION[category]
            ]
            return "<br/>".join(buttons)

        control_panel: str = f"""
        | 🧶 Play | 🌙 Sleep | 🍽️ Eat |
        | :--- | :--- | :--- |
        | {create_button_group("play")} | {create_button_group("sleep")} | {create_button_group("eat")} |
        """
        return inspect.cleandoc(control_panel)

    def generate_egg(self) -> str:
        return f"<!-- {self.create_issue_link('fun', 'headgear')} -->"

    @staticmethod
    def create_issue_link(category: str, name: str, text: str | None = None) -> str:
        link_text = text if text is not None else VALID_ACTION[category][name]
        issue_link = (
            f"[{link_text}]("
            "https://github.com/ttw225/ttw225/issues/new?"
            + urlencode(
                {
                    "title": f"cat|{category}|{name}",
                    "body": "Just push 'Submit new issue' and go back to README. You don't need to do anything else.",
                    "labels": category.capitalize(),
                }
            )
            + ")"
        )
        return issue_link

    @staticmethod
    def create_badge(label: str, message: str, color: str) -> str:
        encoded_label = quote(label)
        encoded_message = quote(message)
        return (
            f"![{label} {message}]("
            f"https://img.shields.io/badge/{encoded_label}-{encoded_message}-{color}?style=for-the-badge"
            ")"
        )

    def generate_user_list(self) -> Tuple[str, str]:
        with open(self.root / "../participants.txt", "r", encoding="utf-8") as file:
            participants: List[str] = file.read().splitlines()
        user_counter: Counter = Counter(participants)
        table_new_line_char: str = " |\n\t| "
        latest_20: str = f"""
        | user |
        | :---: |
        | {table_new_line_char.join([f"[{user_id}](https://github.com/{user_id})" for user_id in list(user_counter)[:20]])} |
        """
        top_20: str = f"""
        | times | user |
        | :---: | :---: |
        | {table_new_line_char.join([f"{counts} | [{user_id}](https://github.com/{user_id})" for user_id, counts in user_counter.most_common()[:20]])} |
        """
        return (inspect.cleandoc(latest_20), inspect.cleandoc(top_20))
