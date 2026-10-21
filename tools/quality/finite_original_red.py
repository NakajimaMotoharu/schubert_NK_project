"""Read an already-ended finite original against preregistered exact assertion messages."""
import json
import os
import xml.etree.ElementTree as ET
from pg5940_private_lock_compile import sha


def validate_failure(key, node, expected):
    if (key not in expected or not node.get('type', '').endswith('AssertionFailedError')
            or node.get('message') != expected[key]):
        raise ValueError('exact independently predicted assertion only, not compile/error/timeout')


def inspect(run, guard, counts, expected, tests, later_not_run):
    m = json.loads((run/'manifest.safe.json').read_bytes())
    begin = json.loads((run/'begin.safe.json').read_bytes()); guard(m['source'])
    if not (m['source'] == begin['source'] and m['actualExit'] == m['mavenActualExit'] == 1
            and m['phaseExits'] == [0, 0, 1] and m['sourceFixed'] and not m['selectedQualified']
            and (m['tests'], m['suites']) == counts and sha(run/'source.tar') == begin['archiveSha256']):
        raise ValueError('exact existing source/archive/original red terminal')
    count = 0; xmls = {}; failures = set()
    for path in (run/'source').glob('src/*/target/surefire-reports/TEST-*.xml'):
        root = ET.parse(path).getroot(); name = root.get('name')
        if name in xmls: raise ValueError('no duplicated original suite')
        xmls[name] = sha(path)
        methods = set()
        for case in root.findall('testcase'):
            count += 1; method = case.get('name', '').split('(', 1)[0]
            if method in methods: raise ValueError('no duplicated original case')
            methods.add(method)
            if any(n.tag in ('error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for n in case.iter()):
                raise ValueError('unexpected test error/skipped/flaky is not purposeful red')
            failed = case.find('failure')
            if failed is not None:
                key = (name, method); validate_failure(key, failed, expected); failures.add(key)
    if count != counts[0] or len(xmls) != counts[1] or failures != set(expected):
        raise ValueError('all exact actual XML and named counterexamples')
    return dict(actualExit=0, originalExit=1, source=m['source'], run=run.name,
        originalManifestSha256=sha(run/'manifest.safe.json'), archiveSha256=begin['archiveSha256'],
        TestHashes={p: sha(run/'source'/p) for p in sorted(tests)}, tests=count, suites=len(xmls),
        expectedFailures=[list(k) for k in sorted(failures)], xmlHashes=xmls, laterNotRun=later_not_run,
        testsExecutedByReader=0, formalAccepted=False, ptAlternativeCompleted=0, vmActions=0)


def publish(value, out):
    os.umask(0o077); out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    return dict(actualExit=0, redFailures=len(value['expectedFailures']), manifestSha256=sha(out/'manifest.json'))
