"""Close the original template run from its native terminal receipts without replaying JUnit."""

import importlib.util
from pathlib import Path

from jacoco_readonly_exec_subset import decode

prepare = Path(__file__).with_name('5686_scr011_012_template_current_six.py')
spec = importlib.util.spec_from_file_location('template_receipt_helpers', prepare)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def main():
    home = helpers.ROOT.parent / 'pgpt-runs/PG379' / helpers.RUN
    begin = helpers.read(home / 'begin.json')
    assert begin['source'] == helpers.git('rev-parse', 'HEAD').decode().strip()
    steps = []
    for stage in ('main-compile', 'test-compile', 'analyzer-compile', 'junit', 'coverage'):
        data = helpers.read(home / f'{stage}.terminal.json')
        assert data['stage'] == stage and data['exit'] == 0
        for channel in ('output', 'error'):
            assert data[channel] == helpers.pin(Path(data[channel]['path']))
        steps.append(data)
    initial = helpers.read(helpers.evidence('27750'))
    old_report = helpers.evidence('27750').parent / 'original-TEST-junit-jupiter.xml'
    assert helpers.pin(old_report)['sha256'] == initial['files'][old_report.name]
    actual_xml = home / 'xml/TEST-junit-jupiter.xml'
    expected = [r for r in helpers.cases(old_report) if r[1] == helpers.TEST]
    assert len(expected) == 6 and helpers.cases(actual_xml) == expected
    assert all(result == 'pass' for _, _, result in expected)
    classes = Path(begin['scratch']) / 'main'
    inventory = {p.relative_to(classes).as_posix().removesuffix('.class'): p
                 for p in classes.rglob('*.class')}
    raw = (home / 'coverage.stdout').read_bytes()
    counters = {}
    observed = {}
    for line in raw.decode().splitlines():
        cells = line.split('\t')
        if cells[0] != 'CLASS':
            continue
        name, crc, present = cells[1:4]
        assert name not in counters and name in inventory
        counters[name] = {counter: dict(missed=int(missed), covered=int(covered))
                          for counter, missed, covered in (c.split(':') for c in cells[6:])}
        if present == 'true':
            observed[name] = crc
    assert len(inventory) == 35 and set(inventory) == set(counters)
    actual_exec = home / 'unit.exec'
    session = decode(actual_exec.read_bytes(), set(observed), strict_class_names=True)
    assert len(session['sessions']) == 1 and session['sessions'][0]['labelBytesHex'] == helpers.RUN.encode().hex()
    assert all(int(v, 16) == int(session['classes'][k]['crc64'], 16) for k, v in observed.items())
    assert all(not any(counters[k][m]['covered'] for m in ('LINE','METHOD','CLASS','BRANCH'))
               for k in set(inventory) - set(observed))
    for name, checksum in begin['scope'].items():
        assert helpers.pin(Path(name))['sha256'] == checksum

    folder = helpers.OPS / helpers.RUN
    folder.mkdir()
    destination = folder / 'unfiltered.tsv'
    destination.write_bytes(raw)
    scope = {k: v for k, v in counters.items() if k.startswith(helpers.PREFIXES)}
    helpers.write(folder / 'manifest.json', dict(run=helpers.RUN, source=begin['source'], productionCore=begin['core'],
        admittedSku='Original finite MockServlet/Thymeleaf fixture and exact current source; no actual endpoint authorization',
        currentMainFixtureAndResourceHashes=begin['scope'], currentProtocol=begin['protocol'], actualExit=0,
        parentRunnerExit=1, parentPostFailure='The post demanded an exec entry for every compiled class',
        actualJUnitExit=0, jUnitInvocations=1, recoveredOriginalReceipt=True, ownProofDecoderCorrectedOnly=True,
        outcomeCounts=dict(passed=6, failures=0, errors=0, skips=0, notRun=0, newDefinitions=0),
        exactTestCases=expected, testXml=helpers.pin(actual_xml), singleOriginalExec=helpers.pin(actual_exec),
        physicallyCompiled=35, execObserved=len(observed), execNotObserved=sorted(set(inventory)-observed.keys()),
        physicalHashes={k: helpers.pin(v)['sha256'] for k,v in inventory.items()},
        completeRawCounters=counters, selectedCounters=scope, coverageFilteredOrMerged=False, raw=helpers.pin(destination),
        originalReceipt=helpers.pin(helpers.evidence('27750')), originalStages=steps, executedScript=helpers.pin(prepare),
        postScript=helpers.pin(Path(__file__)), formalAcceptanceId=None, whole451=False, terminalAtUTC=helpers.now()))
    print('passed', len(expected), 'actual instrumented classes', len(observed), 'all classes', len(inventory))


if __name__ == '__main__':
    main()
