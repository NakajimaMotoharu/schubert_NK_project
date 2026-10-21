"""Inspect original purposeful red XML only; no test rerun, no missing-stage success."""
import json
import os
import xml.etree.ElementTree as ET
from pg6534_jdbc_fatal_graph_selected import W, BASE, TESTS, guard_source
from pg5940_private_lock_compile import sha

EXPECTED = {
 'api-red': ('pg6534-jdbc-api-red-v1', (10, 6), {
  ('dev.codex.schubert.nk.api.security.AuthenticationJdbcGraph328Test',
   'auth328001CauseFatalCannotBecomeAnInfrastructureResult'),
  ('dev.codex.schubert.nk.api.security.AuthenticationJdbcGraph328Test',
   'auth328002SqlNextCycleTerminatesAndPreservesTheOriginalFatal')}),
 'web-red': ('pg6536-jdbc-web-red-v1', (17, 8), {
  ('dev.codex.schubert.nk.web.'+pkg+'.'+cls, method)
  for pkg, cls in (('session', 'SessionJdbcGraph328Test'), ('revocation', 'RevocationJdbcGraph328Test'))
  for method in ('graph328001SqlNextFatalCannotBecomeAnOrdinaryCatalog',
                 'graph328002MixedCyclesAreFiniteAndLateFatalRetainsIdentity')})}


def require_missing_fatal_assertion(failed):
    if not failed.get('type', '').endswith('AssertionFailedError') or 'Expected java.lang.AssertionError to be thrown, but nothing was thrown' not in failed.get('message', ''):
        raise ValueError('only independently predicted missing fatal assertion is a counterexample')


def inspect_red(phase):
    slot, counts, expected = EXPECTED[phase]; run = W/slot
    mp = run/'manifest.safe.json'; m = json.loads(mp.read_bytes())
    bp = run/'begin.safe.json'; b = json.loads(bp.read_bytes())
    guard_source(m['source'], phase)
    if not (m['source'] == b['source'] and m['actualExit'] == m['mavenActualExit'] == 1
            and m['phaseExits'] == [0, 0, 1] and m['sourceFixed'] and not m['selectedQualified']
            and (m['tests'], m['suites']) == counts and sha(run/'source.tar') == b['archiveSha256']):
        raise ValueError('purposeful exact original red only, not compile/format/timeout/incomplete result')
    failures = set(); xmls = {}; actual_count = 0
    for path in (run/'source').glob('src/*/target/surefire-reports/TEST-*.xml'):
        root = ET.parse(path).getroot(); xmls[root.get('name')] = sha(path)
        for case in root.findall('testcase'):
            actual_count += 1
            if any(x.tag in ('error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for x in case.iter()):
                raise ValueError('no unexpected exception, skip or flaky failure accepted as red')
            failed = case.find('failure')
            if failed is not None:
                require_missing_fatal_assertion(failed)
                failures.add((root.get('name'), case.get('name', '').split('(', 1)[0]))
    if failures != expected or actual_count != counts[0] or len(xmls) != counts[1]:
        raise ValueError('all exact named red assertions and saved original XML')
    return dict(source=m['source'], run=slot, originalExit=1, tests=counts[0], suites=counts[1],
                expectedPurposefulFailures=[list(v) for v in sorted(failures)], errorsSkippedFlaky=0,
                originalManifestSha256=sha(mp), beginSha256=sha(bp), archiveSha256=b['archiveSha256'],
                xmlHashes=xmls, TestHashes={p: sha(run/'source'/p) for p in sorted(TESTS)},
                unavailableLaterReactorModulesNotPassed=True, actualPassNotFullInventory=True)


def main():
    rows = {phase: inspect_red(phase) for phase in EXPECTED}
    if len({r['source'] for r in rows.values()}) != 1 or rows['api-red']['TestHashes'] != rows['web-red']['TestHashes']:
        raise ValueError('same Main/Test source across independent API/Web originals')
    out = BASE/'PG6536-jdbc-original-red-v1'; os.umask(0o077); out.mkdir()
    value = dict(actualExit=0, source=rows['api-red']['source'], originals=rows,
                 bug='BUG-1591', rollout='YKT-1344', testsExecutedByReader=0,
                 formalAccepted=False, ptAlternativeCompleted=0, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, redFailures=6, source=value['source'], manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
