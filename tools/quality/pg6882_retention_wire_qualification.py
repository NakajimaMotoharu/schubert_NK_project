"""Original retention method counters and two TestID joins; never global coverage splicing."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import pg6878_retention_wire_selected as selected
from pg5940_private_lock_compile import ROOT, W, BASE, sha

QSHA = '8b33234201d16c5ae4c236fb0b7f0052953dbab88f723c712bb0439ec92bf3d7'
PRIOR = BASE / 'PG6854-web-deadline-original-v1/manifest.json'
PRIOR_SHA = '69dba2782be8034e9efac8505b5019d466da0100bd1a3bc105f57760b61466fd'
CLASS = 'dev/codex/schubert/nk/batch/file/MorningGateEvidence'
METHODS = {
 'retention': '(Ldev/codex/schubert/nk/batch/file/StartupPermitRecords$Epoch;Ljava/lang/String;Ljava/lang/String;Ldev/codex/schubert/nk/batch/file/MorningBackupRetention$Result;)[B',
 'retentionName': '(Ljava/lang/String;)Ljava/lang/String;'}


def methods(tree):
    found = {}
    for c in tree.findall('package/class'):
        if c.get('name') != CLASS:
            continue
        for m in c.findall('method'):
            name = m.get('name')
            if name not in METHODS:
                continue
            if name in found or m.get('desc') != METHODS[name]:
                raise ValueError('one exact member name and descriptor')
            counters = {x.get('type'): {k: int(x.get(k)) for k in ('covered', 'missed')} for x in m.findall('counter')}
            if not all(t in counters and counters[t]['covered'] > 0 and counters[t]['missed'] == 0 for t in ('LINE', 'METHOD', 'BRANCH')):
                raise ValueError('positive actual method counters; no synthetic CLASS or absent fill')
            found[name] = counters
    if set(found) != set(METHODS):
        raise ValueError('both actual formatter methods')
    return found


def main():
    qp = BASE / 'PG6880-retention-wire-original-v2/manifest.json'
    pp = W / 'pg6880-retention-wire-original-v2/manifest.safe.json'
    if QSHA is None or sha(qp) != QSHA or sha(PRIOR) != PRIOR_SHA:
        raise ValueError('freeze genuine original qualifications first')
    q, p, old = [json.loads(x.read_bytes()) for x in (qp, pp, PRIOR)]
    oldp = W / 'pg6854-web-deadline-original-v1/manifest.safe.json'
    if sha(oldp) != old['privateManifestSha256']:
        raise ValueError('prior Main identity map, not old PASS import')
    prior = json.loads(oldp.read_bytes())
    if not (q['actualExit'] == 0 and q['source'] == p['source'] and (q['tests'], q['suites'], q['physicalMain']) == (29, 10, 1669)
      and q['privateManifestSha256'] == sha(pp) and q['originalSixSpotBugs'] == q['checkstyleFindings'] == 0
      and q['pmdRawFindings'] == 1409 and q['changedPhysical'] == []
      and p['allSourceHashes'] == prior['allSourceHashes'] and p['allPhysicalMainSha256'] == prior['allPhysicalMainSha256']):
        raise ValueError('same all851/1669 Main, genuine selected29 only')
    selected.guard(q['source'])
    if subprocess.check_output(['git', 'diff', q['source'], '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all original Main/Test/gates fixed')
    run = W / selected.SLOT
    original = json.loads((run / 'manifest.safe.json').read_bytes())
    xml = run / 'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml'
    if sha(xml) != original['coverage']['batch']['sha256'] or q['originalManifestSha256'] != sha(run / 'manifest.safe.json'):
        raise ValueError('original terminal and actual XML')
    method_counters = methods(ET.parse(xml).getroot())
    cases_path = pp.with_name('cases.safe.json')
    if sha(cases_path) != q['casesSha256']:
        raise ValueError('original case map')
    cases = json.loads(cases_path.read_bytes())
    mapping = {
     'retwire001DeletedGenerationWholeFrameAndDiskPostconditions': 'PT-OPS-RETWIRE-001',
     'retwire002InjectedName255Accepted256RejectedWithoutFilesystemNameCreation': 'PT-OPS-RETWIRE-002'}
    trace = []
    cls = 'dev.codex.schubert.nk.batch.file.RetentionWireBoundaryTest'
    for method, tid in mapping.items():
        matches = [c for c in cases if c['className'] == cls and c['method'] == method and c['source'] == q['source'] and c['result'] == 'PASS_ORIGINAL_XML']
        if len(matches) != 1:
            raise ValueError('one original case per independent TestID')
        trace.append(dict(testId=tid, method=method, sourcePath=selected.TEST, sourceSha256=sha(ROOT / selected.TEST), originalCase=matches[0]))
    value = dict(actualExit=0, source=q['source'], selectedQualificationSha256=sha(qp), originalCoverageXmlSha256=sha(xml),
      selectedTests=29, selectedSuites=10, newJUnitMethods=2, methodCounters=method_counters,
      classCounters=p['allActualCounters']['batch:' + CLASS + '.class'], independentTestIdTrace=trace,
      all851MainByteExact=True, all1669PhysicalMainByteExact=True, mainChanges=0, oldTestChanges=0,
      newSourceGlobalCounters=None, oldFullImportedIntoNewGlobal=False, testsExecutedByReader=0,
      vmActions=0, realBusinessOperations=0, nativeQualified=False, formalAccepted=False,
      acceptedLeafDelta=0, effortPercent=None, ptAlternativeCompleted=0, toolSha256=sha(Path(__file__)))
    out = BASE / 'PG6882-retention-wire-qualification-v1'
    os.umask(0o077)
    out.mkdir()
    path = out / 'manifest.json'
    with path.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(path), methods100=True, newJUnitMethods=2)))


if __name__ == '__main__':
    main()
