"""Finite read-only oracle-literal applicability audit; no Product execution or prior PT replay."""
import ast
import difflib
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG16993-literal-escape-finite-family-post-v1'
FILES=['pg16930_original_start_client_seventeen_independent.py','pg16946_root_memory_truth_deadline_uid_three_independent.py','pg16962_original_stop_client_thirteen_independent.py','pg16978_root_generation_memory_counterexample_eight_independent.py','pg16995_morning_service_memory_readiness_eight_independent_v2.py']
def groups(blob):
    t=ast.parse(blob);rows=[n for n in ast.walk(t) if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='oracle_groups' for v in n.targets)]
    assert len(rows)==1
    return ast.literal_eval(rows[0].value)
def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    rows=[]
    for name in FILES:
        p=data.ROOT/'tools/quality'/name;blob=p.read_bytes();observed=groups(blob);tokens=0;testpins={}
        for owner,values in observed.values():
            path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'+owner+'.java'
            text=(data.ROOT/path).read_bytes();assert data.sha(text)==normal['begin']['inputHashes'][path]
            assert all(v in text.decode() for v in values);tokens+=len(values);testpins[path]=data.sha(text)
        rows.append(dict(path=str(p.relative_to(data.ROOT)),sha256=data.sha(blob),oracleGroups=len(observed),literalTokens=tokens,allTokensMatchFrozenOriginalTest=True,testHashes=testpins,productTestsExecuted=0))
    old=data.ROOT/'tools/quality/pg16994_morning_service_memory_readiness_eight_independent.py';new=data.ROOT/'tools/quality'/FILES[-1]
    oldgroups=groups(old.read_bytes());text=(data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceReadinessTest.java').read_text()
    missing={k:[v for v in values if v not in text] for k,(_,values) in oldgroups.items()};missing={k:v for k,v in missing.items() if v}
    assert set(missing)=={'READY428002','READY428003','READY428006'} and sum(len(v) for v in missing.values())==4
    changed=[line[2:].strip() for line in difflib.ndiff(old.read_text().splitlines(),new.read_text().splitlines()) if line.startswith(('- ','+ '))]
    assert len(changed)==4 and all(line.startswith(('OUT=','oracle_groups=')) for line in changed)
    assert not (data.BASE/'PG16994-morning-service-memory-readiness-eight-independent-v1').exists()
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,rows=rows,finiteFamilyCount=5,oldFailedToolSha256=data.sha(old.read_bytes()),oldFailureRetained=True,oldMismatchGroups=sorted(missing),oldMismatchedLiteralTokens=4,correctionChangedOnlyOracleLiteralAndOutputIdentity=True,previousFourNonApplicableByExactTokenMatch=True,productTestsExecuted=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
