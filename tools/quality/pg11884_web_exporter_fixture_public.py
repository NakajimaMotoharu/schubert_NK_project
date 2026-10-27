"""Public changed-path scan; held names are excluded before any file content access."""
import hashlib
import json
import subprocess
from pg9898_g07_enum_public_delta import ROOT, RULES, HELD

OUT = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG11884-web-exporter-fixture-public-v1'
BEFORE = '0f8591bdd'
PREFIXES = ('tools/quality/architecture/WebExporterFixtureJunitLauncher.java','tools/quality/architecture/WebExporterFixtureArtifactCoverageMeasure.java','tools/quality/architecture/MqMediaCollectorFixtureJunitLauncher.java','tools/quality/architecture/MqMediaCollectorFixtureArtifactCoverageMeasure.java','tools/quality/pg118','tools/quality/architecture/JobOutboxValueFixtureJunitLauncher.java','tools/quality/architecture/JobOutboxValueFixtureArtifactCoverageMeasure.java','tools/quality/architecture/JdbcMetricCollectorFixtureJunitLauncher.java','tools/quality/architecture/JdbcMetricCollectorFixtureArtifactCoverageMeasure.java','tools/quality/architecture/MqSuppliedRecorderFixtureJunitLauncher.java','tools/quality/architecture/MqSuppliedRecorderFixtureArtifactCoverageMeasure.java','tools/quality/pg117','tools/quality/architecture/JvmSystemFixtureJunitLauncher.java','tools/quality/architecture/JvmSystemFixtureArtifactCoverageMeasure.java','tools/quality/architecture/StandardCompositionFixtureJunitLauncher.java','tools/quality/architecture/StandardCompositionFixtureArtifactCoverageMeasure.java','tools/quality/architecture/DbPoolBindingFixtureJunitLauncher.java','tools/quality/architecture/DbPoolBindingFixtureArtifactCoverageMeasure.java','documents/','evidence/01_PT/','src/','tools/quality/pg115','tools/quality/pg116','tools/quality/architecture/MetricHttpGuardJunitLauncher.java','tools/quality/architecture/MetricHttpFixtureJunitLauncher.java','tools/quality/architecture/MetricHttpFixtureArtifactCoverageMeasure.java','tools/quality/architecture/GcLiteralFixtureJunitLauncher.java','tools/quality/architecture/GcFakeGuardJunitLauncher.java','tools/quality/architecture/GcFakeGuardArtifactCoverageMeasure.java')


def selected(names):
    return set(names)-HELD


def main():
    assert not OUT.exists()
    safe = 'tools/quality/pg10606_fixed_error_public_delta.py'
    assert selected(HELD) == set() and selected([safe,*HELD]) == {safe}
    assert selected([safe,safe,*HELD]) == {safe} and selected([]) == set()
    raw = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,'--'],cwd=ROOT)
    raw += subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT)
    assert raw.endswith(b'\0')
    names = selected(raw.decode().split('\0')[:-1])
    assert not names&HELD
    rows, findings = [], []
    for name in sorted(names):
        assert name.startswith(PREFIXES)
        path = ROOT/name
        assert '/private' not in name and not path.is_symlink() and path.is_file()
        content = path.read_bytes()
        assert b'\0' not in content
        content.decode('utf-8')
        rows.append(dict(path=name,sha256=hashlib.sha256(content).hexdigest()))
        for rule,pattern in RULES.items():
            findings.extend(dict(path=name,rule=rule,line=content[:m.start()].count(b'\n')+1) for m in pattern.finditer(content))
    assert rows
    value = dict(actualExit=1 if findings else 0,before=BEFORE,files=rows,findings=findings,
        scope='EXPLICIT_PUBLIC_TEXT_DELTA_THREE_FORMAT_PATTERNS_NOT_WHOLE_G07',
        heldFilesNotReadByThisInvocation=sorted(HELD),selectionMetadataVectors=4,
        globalHeldFileUnreadAssurance='NOT_PROVEN_AFTER_BROAD_SEARCH',actualSecretCount=None,
        wholeWorktreeCleanClaim=False,productTestsExecuted=0,externalActions=0,formalUpdated=False)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=value['actualExit'],files=len(rows),findings=len(findings),
        manifestSha256=hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest())))
    raise SystemExit(value['actualExit'])


if __name__ == '__main__':
    main()
