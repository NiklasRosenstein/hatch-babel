import json
from pathlib import Path
from typing import Any, TypedDict

from babel import __version__ as babel_version
from babel.messages.frontend import CommandLineInterface
from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl
from typing_extensions import NotRequired, Required


class Config(TypedDict):
    locale_dir: Required[str]
    """ The relative path to the directory that contains `*.po` files to compile with `pybabel`. """

    include_po: NotRequired[bool]
    """ Whether to include `*.po` files next to the compiled `*.mo` files. Defaults to `True`. """


class PybabelBuldHook(BuildHookInterface[BuilderConfig]):
    PLUGIN_NAME = "babel"

    config: Config  # type: ignore[assignment]

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        self.clean_files: list[Path] = []

        root = Path(self.build_config.root)
        locale_dir = root / self.config["locale_dir"]

        # NOTE: This is not documented but works. See https://github.com/pypa/hatch/issues/1787
        exclude = self.build_config.build_config.setdefault("exclude", [])
        force_include = build_data["force_include"]

        # Write an "info file" into the locale_dir. We use this as a marker when the wheel is built from the
        # source distribution so we don't need to do another compile step (which would fail with include_po=false).
        info_file = locale_dir / ".pybabel.info"

        if not info_file.exists():
            info_file.write_text(json.dumps({"version": babel_version}))
            force_include[str(info_file)] = str(info_file.relative_to(root))
            CommandLineInterface().run(["pybabel", "-q", "compile", "-d", locale_dir])  # type: ignore[no-untyped-call]
            self.clean_files.append(info_file)

        # Add compiled *.mo files and exclude *.po files, if requested.
        for mo_file in locale_dir.rglob("*.mo"):
            force_include[str(mo_file)] = str(mo_file.relative_to(root))

            if not self.config.get("include_po", False):
                po_file = mo_file.with_suffix(".po")
                exclude.append(str(po_file.relative_to(root)))

    def finalize(self, version: str, build_data: Any, artifact_path: str) -> None:
        for file in self.clean_files:
            print("Cleanup", file)
            file.unlink()


@hookimpl
def hatch_register_build_hook() -> type[BuildHookInterface[BuilderConfig]]:
    return PybabelBuldHook
