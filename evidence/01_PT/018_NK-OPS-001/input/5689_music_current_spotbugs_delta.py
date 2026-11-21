"""Run the typed SpotBugs check for the current fixed Music/Web compile scope."""

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

parent = Path(__file__).with_name('5686_scr011_012_template_current_six.py')
spec = importlib.util.spec_from_file_location('music_spotbugs_helpers', parent)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
RUN = 'PG41506-f03-music-exact-spotbugs-v1'


def main():
    group = h.read(next(h.PLAN.glob('1906_*')))
    source = group['values']['source']
    q = group['quota']
    age = datetime.now(timezone.utc) - datetime.fromisoformat(q['observedAtUTC'])
    assert q['ordinaryUsageAllowed'] and 0 <= age.total_seconds() <= 120
    assert all(w is None or w['remainingPercent'] > 10 for w in (q['primary'], q['secondary']))
    assert source == h.git('rev-parse','HEAD').decode().strip()
    build = h.evidence('41504')
    v = h.read(build)
    assert v['source'] == source and v['compileScopeVerified'] and v['actualExit'] == 0
    target = Path(v['cwd']) / 'target/classes'
    files = {p.relative_to(target).as_posix(): h.pin(p)['sha256'] for p in target.rglob('*.class')}
    assert files == v['physical'] and len(files) == 36
    assert all(name.startswith('dev/codex/schubert/nk/web/') for name in files)
    blocked = ('TemporaryInfrastructureException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'WebStartupException')
    assert not any(any(x in name for x in blocked) for name in files)
    auxiliary = list(v['dependencies'])
    assert len(auxiliary) == len(set(auxiliary))
    auxiliaries = {}
    for name in auxiliary:
        p = Path(name)
        assert h.pin(p)['sha256'] == v['dependencies'][name]
        with ZipFile(p) as z:
            members = {x for x in z.namelist() if x.endswith('.class')}
        if p.is_relative_to(h.TOOLS):
            assert not any(x.startswith('dev/codex/schubert/nk/') for x in members)
        else:
            assert members == set(v['allowedProtocolClassNames'])
        assert not any(any(x in t for x in blocked) for t in members)
        auxiliaries[name] = dict(sha256=v['dependencies'][name], classCount=len(members))
    assert sum(not Path(name).is_relative_to(h.TOOLS) for name in auxiliary) == 1
    original = h.read(h.evidence('41310'))['stages']['spotbugs']['command']
    assert original[5:9] == ['-effort:max','-low','-xml:withMessages','-exitcode']
    assert all(Path(x).is_relative_to(h.TOOLS) for x in original[3].split(os.pathsep))
    private = h.ROOT.parent / 'pgpt-runs/PG379' / RUN
    private.mkdir(mode=0o700)
    report = private / 'spotbugs.xml'
    cmd = [*original[:9], '-auxclasspath', os.pathsep.join(auxiliary), '-output', str(report), str(target)]
    proof = dict(source=source, core=v['core'], compileProof=h.pin(build), run=RUN, exactTargets=files,
                 exactAuxiliaries=auxiliaries, actualCommand=cmd, beganAtUTC=h.now())
    h.write(private/'begin.json', proof)
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    for channel, data in (('stdout',r.stdout),('stderr',r.stderr)):
        (private / channel).write_bytes(data)
    assert report.exists(),'no SpotBugs XML'
    xml = ET.parse(report).getroot()
    defects = []
    for node in xml.findall('BugInstance'):
        span = node.find('SourceLine')
        defects.append(dict(type=node.get('type'), priority=node.get('priority'),
                            source=span.get('sourcepath') if span is not None else None,
                            line=span.get('start') if span is not None else None))
    error = xml.find('Errors')
    stats = xml.find('FindBugsSummary')
    missing = len(error.findall('MissingClass')) if error is not None else None
    errors = len(error.findall('Error')) if error is not None else None
    out = h.OPS / RUN
    out.mkdir()
    h.write(out/'manifest.json',dict(**proof, actualExit=r.returncode, bugs=len(defects),
        findingMetadata=defects, processingErrors=errors, missingClass=missing,
        analyzedClasses=int(stats.get('total_classes')) if stats is not None else None,
        originalXml=h.pin(report), stderr=h.pin(private/'stderr'), stdout=h.pin(private/'stdout'),
        noRuntimeOrHeldOperations=True, formalAcceptanceId=None, whole451=False, terminalAtUTC=h.now()))
    print('Exit', r.returncode, 'findings', len(defects), 'missing', missing, 'errors', errors)


if __name__ == '__main__':
    main()
