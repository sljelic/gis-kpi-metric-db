"""Synchronize release versions and build distributions plus HTML/PDF assets."""

from pathlib import Path
import re
import shutil
import subprocess
import sys
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]


def set_version(value, root=ROOT):
    version = str(Version(value))
    path = root / "pyproject.toml"
    content = path.read_text()
    start = content.index("[project]")
    end = content.find("\n[", start + 1)
    if end < 0:
        end = len(content)
    section, count = re.subn(
        r'(?m)^version\s*=\s*"[^"]+"',
        f'version = "{version}"',
        content[start:end],
        count=1,
    )
    if count != 1:
        raise ValueError("Expected one static project version")
    path.write_text(content[:start] + section + content[end:])
    (root / "VERSION").write_text(version + "\n")
    return version


def main():
    version = set_version(sys.argv[1])
    for path in (ROOT / "dist", ROOT / "build", ROOT / "docs/_build"):
        if path.exists():
            shutil.rmtree(path)
    subprocess.run([sys.executable, "-m", "build"], cwd=ROOT, check=True)
    subprocess.run(["make", "html", "pdf"], cwd=ROOT, check=True)
    shutil.make_archive(
        str(ROOT / "dist" / f"docs-html-{version}"), "zip", ROOT / "docs/_build/html"
    )
    for pdf in (ROOT / "docs/_build/pdf").rglob("*.pdf"):
        shutil.copy2(pdf, ROOT / "dist" / pdf.name)


if __name__ == "__main__":
    main()
