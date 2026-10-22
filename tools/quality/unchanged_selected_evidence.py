"""Read qualified unchanged-Main selections; no PT/build/network/runtime execution or global merge."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6818_current_counter_delta import explicit_four100


def target_counter(tree, physical, branchless_reason=None):
    name = physical.split(':', 1)[1].removesuffix('.class')
    found = [c for c in tree.findall('package/class') if c.get('name') == name]
    if len(found) != 1:
        raise ValueError('one actual XML target, no absent-counter synthesis')
    counters = {x.get('type'): {k: int(x.get(k)) for k in ('covered', 'missed')} for x in found[0].findall('counter')}
    if branchless_reason is None:
        if not explicit_four100(counters):
            raise ValueError('every four counters present, positive and zero missed')
    else:
        if not isinstance(branchless_reason, str) or not branchless_reason.strip():
            raise ValueError('explicit source-specific branchless reason')
        if 'BRANCH' in counters or not all(k in counters and counters[k]['covered'] > 0 for k in ('LINE', 'METHOD', 'CLASS')) or any(c['missed'] for c in counters.values()):
            raise ValueError('actual branch absent, all actual counters zero missed, positive L/M/C; never remove present branches')
    return counters


def case_join(cases, cls, method, source):
    found = [c for c in cases if c['className'] == cls and c['method'] == method and c['source'] == source and c['result'] == 'PASS_ORIGINAL_XML']
    if len(found) != 1:
        raise ValueError('one original current-source XML case per independent TestID')
    return found[0]


def qualify(profile, qname, qsha, counts, oldpath, oldsha, targets, test_ids, outname, tool):
    qp = BASE / qname / 'manifest.json'
    pp = W / qname.lower() / 'manifest.safe.json'
    # Qualification slot names are explicit caller input via the actual public name's PG prefix.
    if qsha is None or sha(qp) != qsha or sha(oldpath) != oldsha:
        raise ValueError('freeze both original qualifications first')
    q, p, old = [json.loads(x.read_bytes()) for x in (qp, pp, oldpath)]
    profile.guard(q['source'])
    if not (q['actualExit'] == 0 and q['source'] == p['source'] and q['privateManifestSha256'] == sha(pp)
      and (q['tests'], q['suites'], q['physicalMain']) == (*counts, 1669) and not q['changedPhysical']
      and q['originalSixSpotBugs'] == q['checkstyleFindings'] == 0 and q['pmdRawFindings'] == 1409
      and p['allSourceHashes'] == old['allSourceHashes'] and p['allPhysicalMainSha256'] == old['allPhysicalMainSha256']):
        raise ValueError('genuine unchanged851/1669 Main and original selected quality')
    if subprocess.check_output(['git', 'diff', q['source'], '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all original Main/Test/gates fixed')
    run = W / profile.SLOT
    original = json.loads((run / 'manifest.safe.json').read_bytes())
    if sha(run / 'manifest.safe.json') != q['originalManifestSha256']:
        raise ValueError('original terminal identity')
    cp = pp.with_name('cases.safe.json')
    if sha(cp) != q['casesSha256']:
        raise ValueError('all original case identities')
    cases = json.loads(cp.read_bytes())
    actual, trace = {}, []
    for target in targets:
        module = target.split(':', 1)[0]
        xml = run / ('source/src/schubert-nk-' + module + '/target/site/jacoco/jacoco.xml')
        if sha(xml) != original['coverage'][module]['sha256'] or target not in p['allPhysicalMainSha256']:
            raise ValueError('original coverage and physical member')
        reason = targets[target] if isinstance(targets, dict) else None
        actual[target] = target_counter(ET.parse(xml).getroot(), target, reason)
        if actual[target] != p['allActualCounters'][target]:
            raise ValueError('same actual original XML counters')
    for path, mapping in test_ids.items():
        cls = path.split('/src/test/java/')[1][:-5].replace('/', '.')
        for method, tid in mapping.items():
            trace.append(dict(testId=tid, sourcePath=path, sourceSha256=sha(ROOT / path), method=method,
              originalCase=case_join(cases, cls, method, q['source'])))
    value = dict(actualExit=0, source=q['source'], qualificationSha256=qsha, originalTerminalSha256=sha(run / 'manifest.safe.json'),
      selectedTests=counts[0], selectedSuites=counts[1], actualTargetCounters=actual, independentTestIdTrace=trace,
      all851MainByteExact=True, all1669PhysicalMainByteExact=True, newSourceGlobalCounters=None,
      oldFullImportedIntoNewGlobal=False, testsExecuted=0, additionalBuildsIssued=0, vmActions=0,
      formalAccepted=False, nativeQualified=False, acceptedLeafDelta=0, effortPercent=None, ptAlternativeCompleted=0,
      toolSha256=sha(tool), sharedReaderSha256=sha(ROOT / 'tools/quality/unchanged_selected_evidence.py'))
    if isinstance(targets, dict):
        value['counterNotApplicable'] = {key: dict(counter='BRANCH', result='NOT_APPLICABLE_ACTUAL_XML_ABSENT', reason=reason) for key, reason in targets.items() if reason is not None}
    out = BASE / outname
    os.umask(0o077)
    out.mkdir()
    path = out / 'manifest.json'
    with path.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(path), targetClasses=len(actual), newJUnitMethods=len(trace))))
    return value
