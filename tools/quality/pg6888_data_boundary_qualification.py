"""Two pure-data original TestID and exact member counters; no Root state or authority proof."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import pg6884_data_boundary_selected as selected
from pg5940_private_lock_compile import ROOT, W, BASE, sha

QSHA = '2814d78fe5ee54672c9a40a6aeaac151a125a75d3a68a4e48ab94390decaac78'
METHODS = {
 ('dev/codex/schubert/nk/batch/platform/RootStartupContext', 'serviceRootDeadline'):
   '(Ldev/codex/schubert/nk/batch/platform/RootStartupContext$Snapshot;J)J',
 ('dev/codex/schubert/nk/batch/file/RootCurrentPermitPreflight$Observed', 'toString'): '()Ljava/lang/String;'}


def main():
    qp = BASE / 'PG6886-data-boundary-original-v1/manifest.json'
    pp = W / 'pg6886-data-boundary-original-v1/manifest.safe.json'
    if sha(qp) != QSHA:
        raise ValueError('genuine frozen original42 qualification')
    q, p = [json.loads(x.read_bytes()) for x in (qp, pp)]
    selected.guard(q['source'])
    if not (q['actualExit'] == 0 and q['source'] == p['source'] and q['privateManifestSha256'] == sha(pp)
      and (q['tests'], q['suites'], q['physicalMain']) == (42, 11, 1669) and not q['changedPhysical']
      and q['originalSixSpotBugs'] == q['checkstyleFindings'] == 0 and q['pmdRawFindings'] == 1409):
        raise ValueError('same-source original42 and zero Main difference')
    if subprocess.check_output(['git', 'diff', q['source'], '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('original Main/Test/gates fixed')
    run = W / selected.SLOT
    xml = run / 'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml'
    original = json.loads((run / 'manifest.safe.json').read_bytes())
    if sha(xml) != original['coverage']['batch']['sha256'] or sha(run / 'manifest.safe.json') != q['originalManifestSha256']:
        raise ValueError('actual original coverage XML and terminal')
    rows = []
    for c in ET.parse(xml).findall('package/class'):
        for m in c.findall('method'):
            key = (c.get('name'), m.get('name'))
            if key not in METHODS:
                continue
            counters = {x.get('type'): {k: int(x.get(k)) for k in ('covered', 'missed')} for x in m.findall('counter')}
            if m.get('desc') != METHODS[key] or any(x['missed'] for x in counters.values()) or not all(counters[t]['covered'] > 0 for t in ('LINE', 'METHOD')):
                raise ValueError('exact actual member and positive line/method, all present counters zero miss')
            rows.append(dict(physicalClass='batch:' + c.get('name') + '.class', method=m.get('name'), descriptor=m.get('desc'), counters=counters))
    if len(rows) != 2:
        raise ValueError('both actual members')
    cp = pp.with_name('cases.safe.json')
    if sha(cp) != q['casesSha256']:
        raise ValueError('original Test identity map')
    cases = json.loads(cp.read_bytes())
    trace = []
    for path in sorted(selected.TESTS):
        cls = path.split('/src/test/java/')[1][:-5].replace('/', '.')
        found = [r for r in cases if r['className'] == cls and r['source'] == q['source'] and r['result'] == 'PASS_ORIGINAL_XML']
        if len(found) != 1:
            raise ValueError('one original case per new Test')
        tid = 'PT-OPS-DATA-511001' if cls.endswith('CurrentObservationValueTest') else 'PT-OPS-DATA-511002'
        trace.append(dict(testId=tid, sourcePath=path, sourceSha256=sha(ROOT / path), originalCase=found[0]))
    value = dict(actualExit=0, source=q['source'], selectedQualificationSha256=QSHA, coverageXmlSha256=sha(xml),
      tests=42, suites=11, newJUnitMethods=2, memberCounters=rows, independentTestIdTrace=trace,
      testsExecutedByReader=0, nativeQualified=False, rootAuthenticated=False, permitIssued=False,
      newGlobalCounters=None, formalAccepted=False, acceptedLeafDelta=0, effortPercent=None,
      ptAlternativeCompleted=0, vmActions=0, toolSha256=sha(Path(__file__)))
    out = BASE / 'PG6888-data-boundary-qualification-v1'
    os.umask(0o077)
    out.mkdir()
    path = out / 'manifest.json'
    with path.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(path), newJUnitMethods=2, actualMemberCounters=rows)))


if __name__ == '__main__':
    main()
