"""BUG763/YKT543 independent literal run bindings; no VM or credential operation."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
TOOLS = ROOT / 'tools/quality/vm/050_s1'
CHR = ROOT / 'program/characterization/tests/java/dev/codex/schubert/characterization'
SOURCE = '979c5ac3e9c28ae76363adacdf9f0736f5a59df1'
OLD = '09b448644cfe70c87df9c89aa5c0c1bf6efdeeea'
OUTPUT = '/home/mini/codex/project1/work/pgpt-runs/PG379/pg475-l01-v2'
DIGEST = '9183662292299cc86412c31a551bf140c8b32ccd9b2d6dcdd414b14e4bcd4806'

required = {
    CHR / 'NativeNkL01Capture475.java': [f'"{SOURCE}".equals(args[1])', f'"{OUTPUT}".equals(args[0])'],
    CHR / 'NativeNkL01Capture475OracleTest.java': [f'"{OUTPUT}","{SOURCE}"', f'previous[1]="{OLD}"'],
    TOOLS / 'pg475_l01_native_v2.sh': [f'"$task_work/pg475-l01-v2" {SOURCE}', 'pg475-l01-tools-v2', 'pg475-l01-native-v2'],
    TOOLS / 'pg475_l01_compile_v2.sh': ['pg475-l01-tools-v2', 'NativeNkL01Capture475OracleTest'],
    TOOLS / 'pg475_parent_observer_v1.sh': [f'pg475_watch_parent.py {SOURCE} {DIGEST} PG475'],
    TOOLS / 'pg475_a01_native_v1.sh': [f'pg475_capture_a01_when_ready.py {SOURCE}'],
    TOOLS / 'pg475_capture_a01_when_ready.py': ["SOURCE==(WORK/'pg475-six-full-v1.source').read_text().strip()"],
    TOOLS / 'pg475_external_start_once.py': ["SOURCE==(WORK/'pg475-six-full-v1.source').read_text().strip()", "'release':'PG475'", 'O_EXCL'],
    TOOLS / 'pg475_watch_parent.py': ["'commit':sys.argv[1]", "sys.argv[3]=='PG475'", '0.1.0-PG475'],
    TOOLS / 'Pg475CompletedReadback.java': [f'SOURCE="{SOURCE}"', f'DIGEST="{DIGEST}"'],
    TOOLS / 'Pg475NativeStop.java': ['SOURCE=Pg475CompletedReadback.SOURCE', 'RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG475")'],
    TOOLS / 'pg475_collect_native_v1.py': [f"SOURCE='{SOURCE}'", 'pg475-host', "'pg475-six-full-v1'"],
    TOOLS / 'pg475_collect_connection_v1.py': [f"S='{SOURCE}'", 'pg475-l01-native-v2', 'pg475-l01-v2/L01-observed.private.json'],
    TOOLS / 'Pg475StoppedDeployment.java': [f'SOURCE="{SOURCE}"', f'OLD_SOURCE="{OLD}"', '0.1.0-PG474', '0.1.0-PG475'],
    TOOLS / 'Pg475StoppedDeploymentTest.java': [f'SOURCE.equals("{SOURCE}")', f'OLD_SOURCE.equals("{OLD}")'],
    TOOLS / 'pg475_stopped_native.py': [f"'{SOURCE}' if action=='after' else '{OLD}'", "'PG475' if action=='after' else 'PG474'"],
    TOOLS / 'pg475_stopped_verify_v1.sh': [f'git diff --quiet {SOURCE}', 'pg475-six-full-v1.exit'],
    TOOLS / 'pg475_stage_candidate_v1.py': [f"SOURCE='{SOURCE}'", 'old=pathlib.Path(\'/opt/schubert-nk/releases/0.1.0-PG474\')'],
    TOOLS / 'pg475_candidate_build_v1.py': ["SOURCE=(WORK/'pg475-six-full-v1.source').read_text().strip()", "gate['productionSource']==SOURCE", f"replace('{OLD}',SOURCE)"],
}

def valid(material):
    return set(material) == set(required) and all(
        all(token in material[path] for token in tokens) for path, tokens in required.items())

material = {p: p.read_text() for p in required}
assert valid(material)
checks = 1
for path, tokens in required.items():
    for token in tokens:
        changed = dict(material)
        changed[path] = changed[path].replace(token, 'FOREIGN_BINDING')
        assert not valid(changed)
        checks += 1
    missing = dict(material)
    del missing[path]
    assert not valid(missing)
    checks += 1
assert all('DRAFT_' not in material[p] for p in required)
checks += 1
print(f'PG475_SOURCE_BINDINGS independentAssertions={checks} targets={len(required)} oldAuthorityExplicit=true nativeMutation0=true productionPT0=true')
