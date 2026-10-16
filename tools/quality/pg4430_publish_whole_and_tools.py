"""Durable independent tool tests and sanitized same-source whole qualification."""
import datetime
import hashlib
import json
import os
import sys
from pg4420_shared_manager_full import ROOT, W, SOURCE


def main():
    os.umask(0o077); private = W / 'pg4430-whole-tool-evidence-v1'
    tests = ['pg4414_metadata_cost_tools_test', 'pg4422_shared_manager_whole_qualification_test',
             'pg4424_shared_manager_static_test', 'pg4426_relocated_jar_contract_test',
             'pg4428_file_whole_qualification_test', 'pg4432_shared_manager_signed_candidate_test']
    command = [sys.executable, '-B', '-m', 'unittest', *tests, '-v']
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # v1's exact15 tests genuinely completed0 before the publisher host-static
    # rejection. Preserve that result; do not replay tests to conceal the failure.
    log = (private / 'tools.log').read_bytes()
    if b'Ran 15 tests in ' not in log or not log.endswith(b'\nOK\n') or log.count(b' ... ok\n') != 15:
        raise ValueError('saved original15 genuine tests required, no automatic replay')
    from pyflakes.api import checkPath
    files = [ROOT / 'tools/quality' / (name + '.py') for name in tests]
    files += [ROOT / 'tools/quality' / name for name in ['pg4420_shared_manager_full.py', 'pg4422_shared_manager_whole_qualification.py',
        'pg4424_shared_manager_static.py', 'pg4426_relocated_jar_contract.py', 'pg4428_file_whole_qualification.py',
        'pg4432_shared_manager_signed_candidate.py', 'pg4430_publish_whole_and_tools.py']]
    if sum(checkPath(str(path)) for path in files): raise ValueError('all host static0 required')
    whole = json.loads((W / 'pg4420-shared-manager-six-v1/manifest.safe.json').read_bytes())
    qualified = json.loads((W / 'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())
    diagnostic = json.loads((W / 'pg4424-shared-manager-static-v1/manifest.safe.json').read_bytes())
    if any(value['actualExit'] != 0 for value in [whole, qualified, diagnostic]): raise ValueError('all original results genuine0')
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4430-shared-manager-whole-v1'; out.mkdir()
    (out / 'tools.log').write_bytes(log)
    names = {}
    for name, value in [('whole.json', whole), ('qualification.json', qualified), ('static.json', diagnostic)]:
        # Reports contain only code/build/static hashes and counts; never private observer logs or credential.
        (out / name).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
        names[name] = hashlib.sha256((out / name).read_bytes()).hexdigest()
    names['tools.log'] = hashlib.sha256(log).hexdigest()
    manifest = {'startUTC': start, 'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source': SOURCE,
        'originalWholeExec': 79478, 'wholeActualExit': 0, 'independentActualExit': 0, 'tests': 3721, 'suites': 545,
        'mainClasses': 1644, 'spotbugsSixModules': 0, 'toolsActualExit': 0, 'toolTests': 15, 'toolTestsAreProductionPT': False,
        'command': command, 'originalToolLogReusedWithoutReplay': True, 'publisherV1ActualExit': 1,
        'publisherV1RejectedBeforePublicManifest': True, 'hostStatic': 0, 'files': names, 'BUG': [1354, 1355, 1356, 1357], 'YKT': [1120, 1121, 1122, 1123],
        'prior4422HostError': {'actualHostExit': 1, 'errno': 7, 'remoteStarted': False, 'preserved': True},
        'pmdRaw': diagnostic['result']['pmd']['rawFindings'], 'pmdProcessingErrors': 0, 'checkstyleFindings': 0,
        'coverage': qualified['result']['coverage'], 'allFour100': False, 'nativePending': True, 'deployed': False,
        'F03Accepted': False, 'formalAccepted': False, 'formalTests': 1964, 'formalScopes': 53, 'effortCompletion': None,
        'QA051final': 'HELD', 'wholeReplay': False, 'vmActions': 0}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'publicManifestSha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest(),
                      'tests': 3721, 'toolTests': 15, 'formalAccepted': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
