"""Independent immutable Program index/document/case union review; no Product invocation."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13067-time-header-completion-post-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    m = data.read_checked(data.BASE/'PG13066-time-header-completion-v1/manifest.json','506dd72b609489248e9a71e1cba6567389d25fa33053d0b0e6314e729e6bee58')
    p = data.read_checked(data.BASE/'PG13054-time-header-plan-v1/manifest.json','2088beba343b5c547520d3c55fa3cc6cc1e286319df6a4f60606d2e8cff6df13')
    proof = data.read_checked(data.BASE/'PG13062-time-header-post-v1/manifest.json','b40146077c160e89ae69a0f370440040422174f2d24c4a2050f9da7cb5934bbd')
    assert m['actualExit'] == proof['actualExit'] == 0 and m['source'] == p['source'] == proof['source'] == '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
    expected = {(r['className'],r['method']) for r in p['cases']}; seen = set(); ids = set(); programs = {}
    for path,sha in m['programIndexes'].items():
        item = data.read_checked(data.ROOT/path,sha)
        assert item['source'] == m['source'] and item['actualExit'] == 0 and item['observedOwnTests'] == 3
        assert item['sharedRunTotalTests'] == 6 and item['sharedRunTotalSuites'] == 2 and item['sessionId'] == 'PG13058-TIMEHEADER-JP'
        assert item['newAccepted'] == 0 and not item['formalUpdated'] and not item['whole451Accepted'] and not item['oldExecUnion']
        subject,prefix = ('QuestionCommandMetadata','PT-CMD-TIMEBOUND') if item['program'] == '011_NK-QST-001' else ('ContentDispositionFactory','PT-MED-HEADERBOUND')
        assert item['selectedMain'] == proof['selectedMain'][subject]
        for index,row in enumerate(item['cases'],1):
            pair = (row['className'],row['method']); assert pair in expected and pair not in seen
            identifier = prefix+'-'+str(index).zfill(3); assert row['testId'] == identifier and identifier not in ids
            ids.add(identifier); seen.add(pair)
            assert data.sha((data.ROOT/row['path']).read_bytes()) == row['sourceSha256']
        assert all(data.sha((data.ROOT/doc).read_bytes()) == digest for doc,digest in item['documentHashes'].items())
        directory = (data.ROOT/path).parent
        assert not directory.is_symlink() and [entry.name for entry in directory.iterdir()] == ['manifest.json']
        programs[item['program']] = dict(ownTests=3,counterSubject=subject,indexSha256=sha)
    assert len(programs) == 2 and seen == expected and len(ids) == 6
    assert m['observedTests'] == m['newUniqueTestIds'] == m['distinctProgramCaseBindings'] == len(ids)
    assert m['productReruns'] == 0 and not m['runDuplicated'] and m['newAccepted'] == 0
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,
        completionManifestSha256='506dd72b609489248e9a71e1cba6567389d25fa33053d0b0e6314e729e6bee58',
        programs=programs,uniqueTestIds=sorted(ids),observedSharedTests=6,programBindings=6,
        sourceAndDocumentHashesMatched=True,runDuplicated=False,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
