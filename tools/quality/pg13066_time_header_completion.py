"""Bind the same six new XML cases into two Program indexes without double-counting the run."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
OUT = data.BASE/'PG13066-time-header-completion-v1'
SPEC = 'evidence/01_PT/018_NK-OPS-001/2410_業務時刻・媒体header境界6_単体テスト仕様.md'
RESULT = 'evidence/01_PT/018_NK-OPS-001/2411_業務時刻・媒体header境界6_実行結果.md'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    proof_path = data.BASE/'PG13062-time-header-post-v1/manifest.json'
    proof = data.read_checked(proof_path,'b40146077c160e89ae69a0f370440040422174f2d24c4a2050f9da7cb5934bbd')
    plan = data.read_checked(data.BASE/'PG13054-time-header-plan-v1/manifest.json','2088beba343b5c547520d3c55fa3cc6cc1e286319df6a4f60606d2e8cff6df13')
    trace = data.read_checked(data.BASE/'PG13065-time-header-trace-post-v1/manifest.json','dd5279a9e7ec84fa91d415dc77318160b0ed4f0916d4bd263fe94fcdaf058e6b')
    host = data.read_checked(data.BASE/'PG13058-time-header-host-v1/manifest.json','535b37b54a8922e4633320f99d95ce69f355c84f70e360ea4ad1352037867a4d')
    assert proof['source'] == plan['source'] == trace['source'] == host['source'] == SOURCE
    assert proof['actualExit'] == trace['actualExit'] == host['actualExit'] == 0 and proof['observedTestExecutions'] == 6
    assert trace['wholeWbsAudit']['actualExit'] == 1 and not trace['wholeWbsAudit']['passed']
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in host['begin']['sourceInputHashes'].items())
    cases = {(row['className'],row['method']) for row in plan['cases']}
    assert cases == {(row['classname'],row['name']) for row in host['cases']} and len(cases) == 6 and not any(row['nonPass'] for row in host['cases'])
    spec = (data.ROOT/SPEC).read_text(); outputs = {}; included = set()
    configs = [('011_NK-QST-001','command-time-boundaries','QuestionCommandTimeBoundaryTest','QuestionCommandMetadata','PT-CMD-TIMEBOUND','001_NK-QST-001_受付ID単体テスト仕様書.md','002_NK-QST-001_受付ID実行結果.md'),('009_NK-MED-001','header-byte-boundaries','ContentDispositionBoundaryTest','ContentDispositionFactory','PT-MED-HEADERBOUND','001_NK-MED-001_単体テスト仕様書.md','002_NK-MED-001_実行結果.md')]
    pending = []
    for program,name,test,subject,prefix,program_spec,program_result in configs:
        base = data.ROOT/'evidence/01_PT'/program; parent = base/'evidence'; directory = parent/name
        assert parent.is_dir() and not parent.is_symlink() and not directory.exists()
        documents = [SPEC,RESULT,str((base/program_spec).relative_to(data.ROOT)),str((base/program_result).relative_to(data.ROOT))]
        selected = [row for row in plan['cases'] if row['className'].endswith('.'+test)]
        assert len(selected) == 3
        for index,row in enumerate(selected,1):
            identifier = prefix+'-'+str(index).zfill(3); assert identifier in spec and (row['className'],row['method']) not in included
            included.add((row['className'],row['method'])); row['testId'] = identifier
        item = dict(source=SOURCE,actualExit=0,program=program,cases=selected,observedOwnTests=3,sharedRunTotalTests=6,sharedRunTotalSuites=2,
            sessionId=host['sessionId'],hostManifestSha256='535b37b54a8922e4633320f99d95ce69f355c84f70e360ea4ad1352037867a4d',
            proofManifest=str(proof_path.relative_to(data.ROOT)),proofManifestSha256='b40146077c160e89ae69a0f370440040422174f2d24c4a2050f9da7cb5934bbd',
            selectedMain=proof['selectedMain'][subject],newAccepted=0,formalUpdated=False,oldExecUnion=False,
            documentHashes={path:data.sha((data.ROOT/path).read_bytes()) for path in documents},coverageMeaning='Own class counters only; do not add old sources or call whole Program accepted',
            inputExpectedActual='2410 literal input/independent byte or UTC oracle and immutable Test sources; all corresponding XML cases SUCCESSFUL',
            whole451Accepted=False,effortPercent=None,relatedNewProductBugs=[],relatedNewSsc=[])
        pending.append((directory,item))
    assert included == cases; verify(invocation)
    for directory,item in pending:
        directory.mkdir(); target = directory/'manifest.json'; data.write(target,item)
        outputs[str(target.relative_to(data.ROOT))] = data.sha(target.read_bytes())
    OUT.mkdir();data.write(OUT/'manifest.json',dict(source=SOURCE,actualExit=0,invocation=invocation,programIndexes=outputs,
        observedTests=6,newUniqueTestIds=6,distinctProgramCaseBindings=6,runDuplicated=False,productReruns=0,
        sourceMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1970,newTestPhysical=2,newAccepted=0,whole451Accepted=False,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
