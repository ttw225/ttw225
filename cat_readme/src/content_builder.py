import inspect
import logging
import pathlib
from string import Template
from typing import Dict, List
from urllib.parse import urlencode

from config import VALID_ACTION, Action

CONTENT_TEMPLATE = """
${cat_status}

${cat_img}

## Control Panel

Choose your favorite one

${control_panel}

${egg}
"""


class Content:
    def __init__(self, root: pathlib.Path, action: Action) -> None:
        self.root: pathlib.Path = root
        self.action: Action = action

    def build_content(self) -> str:
        data: Dict[str, str] = {
            "cat_status": self.generate_status(),
            "cat_img": self.generate_img_path(),
            "control_panel": self.generate_control_panel(),
            "egg": self.generate_egg(),
        }
        return Template(CONTENT_TEMPLATE).substitute(data)

    def generate_status(self) -> str:
        status: str = ""
        match (self.action.category):
            case ("sleep"):
                status = "Sleeping... Zzz"
            case ("play"):
                status = f"Playing with {self.action.name.replace('_', ' ')} !"
            case ("eat"):
                status = f"Eating a {self.action.name.replace('_', ' ')} 😋"
            case ("fun"):
                status = "entertaining everyone XD\n\n*(Secret) Someone found this easter egg!!*"
            case _:
                logging.warning(f"[Generate Status] category: {self.action.category}")
        return f"Cat is {status}"

    def generate_img_path(self) -> str:
        image_md: str = (
            f"<img src='./assets/image/{self.action.category}/{self.action.name}.gif' "
            f"alt=cat_{self.action.category}_{self.action.name} "
            "width='320' height='320' />"
        )
        return inspect.cleandoc(image_md)

    def generate_control_panel(self) -> str:
        def create_table_content(category: str) -> str:
            links: List[str] = [self.create_issue_link(category, name) for name in VALID_ACTION[category]]
            return " &nbsp; ".join(links)

        control_panel: str = f"""
        | play | sleep | eat |
        | :---: | :---: | :---: |
        | {create_table_content("play")} | {create_table_content("sleep")} | {create_table_content("eat")} |
        """
        return inspect.cleandoc(control_panel)

    def generate_egg(self) -> str:
        return f"<!-- {self.create_issue_link('fun', 'headgear')} -->"

    @staticmethod
    def create_issue_link(category: str, name: str) -> str:
        issue_link = (
            f"[{VALID_ACTION[category][name]}]("
            "https://github.com/ttw225/test/issues/new?"
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

    def generate_user_list(self):
        return ""
