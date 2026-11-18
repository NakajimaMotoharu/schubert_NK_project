"""Check original XML, CRC and initializer witnesses for the two journal record tests."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree
import gzip
import re
import runpy

HERE = Path(__file__).resolve()
A = runpy.run_path(str(HERE.with_name('5271_p01810_detached_journal_values.py')))
B = runpy.run_path(str(HERE.with_name('5257_p01810_broker_evidence_value_post.py')))
E, OUT, IDS, TARGETS, MAIN, TEST = (A[key] for key in ('E', 'OUT', 'IDS', 'TARGETS', 'MAIN', 'TEST'))
read, save, ref, git = (A[key] for key in ('read', 'save', 'ref', 'git'))


def main():
    run = read(OUT / 'manifest.json')
    begin = read(OUT / 'begin.json')
    assert run['actualExit'] == 0 and run['tests'] == 2
    assert all(run[k] == 0 for k in ('fails', 'errors', 'skips', 'notRun', 'actualJournalOrBrokerActions'))
    assert not run['pmd']
    assert run['sourceCore'] == begin['sourceCore'] and run['testSource'] == begin['unitSource']
    for stage, entry in run['stageResults'].items():
        assert entry == read(OUT / (stage + '-exit.json')) and entry['actualExit'] == 0
    for name in ('testXml', 'raw', 'exec', 'init'):
        assert ref(Path(run[name]['path'])) == run[name]
    test_ref = Path(begin['testInput']['path'])
    assert ref(test_ref) == begin['testInput']
    test_src = git('show', f"{run['testSource']}:{TEST}")
    assert test_src == test_ref.read_bytes()
    assert b'BrokerJournalEvidence.anchor(' not in test_src and b'BrokerJournalEvidence.inspect(' not in test_src
    assert git('show', f"{run['testSource']}:{MAIN}") == git('show', f"{run['sourceCore']}:{MAIN}")
    results = ElementTree.parse(run['testXml']['path'])
    assert all(n.tag not in ('failure', 'error', 'skipped') for n in results.iter())
    assert {n.get('name') for n in results.iter('testcase')} == {name + '()' for name in IDS.values()}
    assert set(run['counters']) == set(TARGETS)
    execinfo = (OUT / 'execinfo.log').read_text()
    assert execinfo.count('Session "') == 1 and run['session'] in execinfo
    raw_rows = {
        parts[1]: parts for line in (OUT / 'raw.tsv').read_text().splitlines()
        if (parts := line.split('\t'))[0] == 'CLASS'
    }
    assert set(raw_rows) == set(TARGETS)
    crcs = {}
    for name in TARGETS:
        physical = run['physical'][name + '.class']
        recorded = Path(physical['snapshot']['path'])
        assert ref(recorded) == physical['snapshot']
        assert ref(Path(physical['origin']['path'])) == physical['origin']
        assert physical['origin']['sha256'] == physical['snapshot']['sha256']
        crc = B['crc64'](recorded.read_bytes())
        assert crc == raw_rows[name][2]
        assert re.search(rf'^{crc}\s+[1-9][0-9]* of\s+\d+\s+{re.escape(name)}$', execinfo, re.M)
        assert all(row['missed'] == 0 for row in run['counters'][name].values())
        crcs[name] = crc
    init = gzip.decompress(Path(run['init']['path']).read_bytes())
    loaded = set(re.findall(rb"Initializing '(dev/codex/schubert/nk/[^']+)'", init))
    assert loaded == {name.encode() for name in TARGETS} | {A['TYPE'].replace('.', '/').encode()}
    proof = dict(
        actualExit=0, sourceCore=run['sourceCore'], testSource=run['testSource'],
        manifest=ref(OUT / 'manifest.json'), testIds=IDS, tests=2, suites=1, newDefinitions=2,
        firstDynamicSuccess=2, firstDynamicTotal=2, pmdRaw=0, pmdApplicable=0, pmdUnclassified=0,
        crc64=crcs, counters=run['counters'], exactTargetOnly=True, runtimeOperationCount=0,
        actualJournalAcquired=False, absentOuterParserInitialization=True,
        oldExecReplayedOrMerged=False, whole451Accepted=False, newAcceptance=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(HERE),
    )
    destination = OUT / 'independent.json'
    save(destination, proof)
    print(ref(destination), crcs)


if __name__ == '__main__':
    main()
