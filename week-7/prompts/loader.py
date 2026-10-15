import yaml
from pathlib import Path
from dataclasses import dataclass

PROMPTS_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Prompt:
    name: str
    text: str
    version: str
    model: str
    params: dict


def load(name: str, version: str = None) -> Prompt:
    """
    Load a prompt by name. The active version is
    configured in the metadata.yaml file and the
    corresponding prompt text is loaded from the
    versions directory.

    Args:
        name (str): The name of the prompt to load.
    Returns:
        Prompt: The loaded prompt object.
    """

    directory = PROMPTS_DIR / name
    metadata = yaml.safe_load((directory / "metadata.yaml").read_text())
    if version is None:
        version = metadata["active_version"]
    return Prompt(
        name=name,
        text=(directory / f"{version}.txt").read_text(),
        version=version,
        model=metadata["model"],
        params=metadata["params"],
    )
