"""Preserve selected XML/exec/jars and compare every main class to frozen PG540."""
import hashlib
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def main():
    os.umask(0o077)
    root = Path('/home/mini/codex/project1/work/pgpt-foundation')
    work = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
    base = work / 'pg565-child-context-selected-v1'
    assert base.with_suffix('.exit').read_bytes() == b'0\n'
    source = base.with_suffix('.source').read_text().strip()
    target = work / 'pg565-selected-frozen-v1'
    assert not target.exists()
    target.mkdir(mode=0o700)
    summary = {}
    for module in ('storage', 'bootstrap'):
        current = root / 'src' / ('schubert-nk-' + module) / 'target'
        jar_name = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
        frozen = work / 'pg540-six-host-v1' / module / jar_name
        with zipfile.ZipFile(frozen) as old, zipfile.ZipFile(current / jar_name) as new:
            previous = {name: old.read(name) for name in old.namelist() if name.endswith('.class')}
            actual = {name: new.read(name) for name in new.namelist() if name.endswith('.class')}
            assert previous == actual and len(previous) > 0
        reports = list((current / 'surefire-reports').glob('TEST-*.xml'))
        assert reports
        totals = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
        destination = target / module
        destination.mkdir(mode=0o700)
        files = {jar_name: current / jar_name, 'jacoco.exec': current / 'jacoco.exec',
                 'jacoco.xml': current / 'site/jacoco/jacoco.xml',
                 'spotbugs.xml': current / 'spotbugsXml.xml'}
        for report in reports:
            suite = ET.parse(report).getroot()
            for counter in totals:
                totals[counter] += int(suite.attrib[counter])
            assert suite.findall('testcase') and len(suite.findall('testcase')) == int(suite.attrib['tests'])
            files[report.name] = report
        assert totals['tests'] > 0 and sum(totals[k] for k in ('failures', 'errors', 'skipped')) == 0
        assert not ET.parse(files['spotbugs.xml']).getroot().findall('BugInstance')
        hashes = {}
        for name, file in files.items():
            raw = file.read_bytes(); hashes[name] = hashlib.sha256(raw).hexdigest()
            with (destination / name).open('xb') as output:
                output.write(raw); output.flush(); os.fsync(output.fileno())
        coverage = ET.parse(files['jacoco.xml']).getroot()
        counters = {c.attrib['type']: {'missed': int(c.attrib['missed']), 'covered': int(c.attrib['covered'])}
                    for c in coverage.findall('counter')}
        context = []
        for package in coverage.findall('package'):
            for cls in package.findall('class'):
                if cls.attrib['name'].endswith('/ChildStartupContext'):
                    context = [{**counter.attrib} for counter in cls.findall('counter')]
        summary[module] = {'totals': totals, 'suites': len(reports), 'allMainClassBytesEqualPG540': True,
                           'mainClasses': len(previous), 'counter': counters,
                           'childStartupContext': context, 'hashes': hashes, 'spotbugs0': True}
    receipt = {'operatorSource': source, 'productionSource': '969d8ded10c0bf5841d9e3a5c531e922caf4a24a',
               'actualExit': 0, 'moduleResults': summary, 'formalAccepted': False,
               'privateLogSha256': hashlib.sha256(base.with_suffix('.log').read_bytes()).hexdigest(),
               'sourceFilesSha256': hashlib.sha256(base.with_suffix('.source-files.sha256').read_bytes()).hexdigest()}
    with (target / 'manifest.safe.json').open('x') as output:
        json.dump(receipt, output, indent=2); output.write('\n'); output.flush(); os.fsync(output.fileno())
    print(json.dumps({'actualExit': 0, 'source': source,
                      'totals': {m: v['totals'] for m, v in summary.items()},
                      'childStartupContext': summary['bootstrap']['childStartupContext'],
                      'manifestSha256': hashlib.sha256((target / 'manifest.safe.json').read_bytes()).hexdigest(),
                      'mainByteDiff0': True, 'formalAccepted': False}))


if __name__ == '__main__':
    main()
