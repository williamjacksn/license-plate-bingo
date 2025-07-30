import json
import pathlib


THIS_FILE = pathlib.PurePosixPath(
    pathlib.Path(__file__).relative_to(pathlib.Path().resolve())
)


def gen(content: dict, target: str):
    pathlib.Path(target).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(target).write_text(
        json.dumps(content, indent=2, sort_keys=True), newline="\n"
    )


def gen_dependabot(target: str):
    def update(ecosystem: str) -> dict:
        return {
            "package-ecosystem": ecosystem,
            "allow": [{"dependency-type": "all"}],
            "directory": "/",
            "schedule": {"interval": "daily"},
        }

    ecosystems = ["docker", "github-actions", "uv"]
    content = {
        "version": 2,
        "updates": [update(e) for e in ecosystems],
    }

    gen(content, target)


def main():
    gen_dependabot(".github/dependabot.yaml")


if __name__ == "__main__":
    main()
