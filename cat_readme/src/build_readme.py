import json
import logging
import pathlib
import re
import sys

from config import VALID_ACTION, Action
from content_builder import Content

ROOT = pathlib.Path(__file__).parent.resolve()


class BuildReadme:
    def __init__(self, *, user_action: Action) -> None:
        self.action: Action = user_action
        self.readme_path: pathlib.Path = ROOT / "../../README.md"
        self.status_path: pathlib.Path = ROOT / "../status.json"
        self.readme: str = ""

    def update(self) -> None:
        if not self.check_update():
            logging.warning("[Pass] No Update")
            return
        self.load_readme()
        new_cat_readme: str = self.do_action()
        self.readme = self.replace_chunk(self.readme, "output", new_cat_readme)
        self.write_readme()
        self.write_status()

    def check_update(self) -> bool:
        with open(self.status_path, "r", encoding="utf-8") as file:
            status = json.load(file)
        if status == self.action.__dict__:
            return False
        return True

    def do_action(self) -> str:
        content: Content = Content(ROOT, self.action)
        return content.build_content()

    def load_readme(self) -> None:
        with open(self.readme_path, "r", encoding="utf-8") as file:
            self.readme = file.read()

    def write_readme(self) -> None:
        with open(self.readme_path, "w", encoding="utf-8") as file:
            file.write(self.readme)

    def write_status(self) -> None:
        with open(self.status_path, "w", encoding="utf-8") as file:
            json.dump(self.action.__dict__, file)

    @staticmethod
    def replace_chunk(content: str, marker: str, chunk: str) -> str:
        readme_regex: re.Pattern = re.compile(
            r"<!\-\- {marker} starts \-\->.*<!\-\- {marker} ends \-\->".format(marker=marker),
            re.DOTALL,
        )
        chunk_with_flag: str = f"<!-- {marker} starts -->\n{chunk}\n<!-- {marker} ends -->"
        return readme_regex.sub(chunk_with_flag, content)


if __name__ == "__main__":
    action: Action
    try:
        _, category, name = sys.argv[1].split("|")
        if name not in VALID_ACTION.get(category, ()):
            raise ValueError("Action Invalid")
        action = Action(category, name)
    except Exception as e:
        logging.warning(f"[argv parse error] {e}")
        action = Action("sleep", "sleep_well")
    readme = BuildReadme(user_action=action)
    readme.update()
