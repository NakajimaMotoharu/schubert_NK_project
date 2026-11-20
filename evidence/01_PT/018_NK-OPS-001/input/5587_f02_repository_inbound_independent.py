"""Reconcile the exact direction delta and current API repository source names."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
ROOT = Path("src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api")
DESIGN = Path("documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md")
CANONICAL = "63c4a673bc98464a5bb8e9dae85eba3ce9ef0d2a"
API = "dev.codex.schubert.nk.api."
TARGET = API + "messaging.inbound.InboundPort"
EXPECTED_ORIGINS = {
    API + "persistence.InboundFieldFixture",
    API + "monitoring.persistence.InboundCallFixture",
    API + "fence.DirectionFixtureRepository$Nested",
    API + "persistence.InboundArrayFixture",
}


def git(*parts):
    return subprocess.check_output(["git", *parts], timeout=20)


def pin(path, data=None):
    return {"path": str(path), "sha256": sha256(path.read_bytes() if data is None else data).hexdigest()}


def receipt(prefix):
    path, = OPS.glob(f"{prefix}-*/manifest.json")
    data = json.loads(path.read_bytes())
    raw = path.with_name("audit.stdout.txt")
    assert pin(raw) == data["steps"]["audit"]["stdout"]
    rows = [tuple(line.split("\t")[1:]) for line in raw.read_text().splitlines()
            if line.startswith("FINDING\t")]
    assert len(rows) == len(set(rows))
    return path, data, set(rows)


def main():
    red_path, red, former = receipt("PG41110")
    green_path, green, current = receipt("PG41112")
    assert former <= current and len(former) == 67
    assert current - former == {("REPOSITORY_DIRECTION", origin, TARGET) for origin in EXPECTED_ORIGINS}
    assert (red["matched"], green["matched"], green["caseCount"], green["priorControls"]) == (3, 7, 7, 103)
    assert green["physical"] == red["physical"] == 166
    core = green["productionCore"]
    paths = [Path(line) for line in git("ls-tree", "-r", "--name-only", core, "--", str(ROOT))
             .decode().splitlines()]
    source = git("show", f"{CANONICAL}:{DESIGN}")
    assert "repositoryから上位層を呼ばない".encode() in source
    inbound = ROOT / "messaging" / "inbound"
    names = sorted(path.stem for path in paths if path.parent == inbound and path.stem != "package-info")
    pattern = re.compile(r"\b(?:" + "|".join(names) + r")\b|\bapi\.messaging\.inbound\b")
    candidates = [path for path in paths if "persistence" in path.relative_to(ROOT).parts[:-1]
                  or path.stem.endswith("Repository")]
    assert len(candidates) == 16 and len(names) == 14
    source_pins = []
    for path in candidates:
        data = git("show", f"{core}:{path}")
        assert not pattern.search(data.decode()), path
        source_pins.append(pin(path, data))
    out = OPS / "PG41114-f02-repository-inbound-independent-v1"
    out.mkdir()
    path = out / "manifest.json"
    with path.open("x") as stream:
        json.dump(dict(actualExit=0, productionCore=core, toolSource=green["toolSource"],
                       canonicalDesign=CANONICAL, design=pin(DESIGN, source), red=pin(red_path),
                       green=pin(green_path), repositorySources=source_pins, inboundTypeNames=names,
                       matchedCases=7, previousControls=103, unimportedClasses=0, directSourceNameMatches=0,
                       productJars=0, productTests=0, formalDelta=0, wholeF02=False, whole451=False,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(pin(path))


if __name__ == "__main__":
    main()
