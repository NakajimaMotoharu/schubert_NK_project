"""Metadata-only tests for fixed pure JDBC source eligibility, no target/runtime execution."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pure_jdbc_fixture_scope_v1 as scope

TESTS=json.loads("{\"AsyncJobMetricCollectorTest\":{\"path\":\"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricCollectorTest.java\",\"sha256\":\"e91c368880999ba74d2157210ecaa3c80f4388ee80a4d94f1862a0efc1c973ed\"},\"AsyncJobMetricRecorderTest\":{\"path\":\"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricRecorderTest.java\",\"sha256\":\"714b91b3dd34aed6cc3379bf02d161f6f12f0216bffbb9859822efb4ee5aa3d6\"},\"AsyncJobCountRepositoryTest\":{\"path\":\"src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobCountRepositoryTest.java\",\"sha256\":\"3f6c16ee0a85788b96746a87d870d2874d4ee753e639abb89796f0fcba632042\"}}")
OUT=data.BASE/'PG14401-pure-jdbc-fixture-preflight-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    texts={}
    for n,item in TESTS.items():
        raw=(data.ROOT/item['path']).read_bytes();assert data.sha(raw)==item['sha256'];texts[n]=raw.decode()
    assert scope.eligible(texts) is True
    labels=[]
    def rejected(name,value):
        assert scope.eligible(value) is False
        labels.append(name)
    for token in scope.FORBIDDEN:
        bad=copy.deepcopy(texts);bad['AsyncJobCountRepositoryTest']+='\n'+token
        rejected('forbidden:'+token,bad)
    for token in scope.REQUIRED:
        bad=copy.deepcopy(texts);bad['AsyncJobCountRepositoryTest']=bad['AsyncJobCountRepositoryTest'].replace(token,'REMOVED_REVIEWED_CONTRACT')
        rejected('missing:'+token,bad)
    rejected('null',None);rejected('empty',{});rejected('unknown-key',{**texts,'Unknown':texts['AsyncJobCountRepositoryTest']})
    bad=copy.deepcopy(texts);bad['AsyncJobCountRepositoryTest']=None;rejected('null-text',bad)
    assert len(labels)==len(set(labels))==25
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',invocation=invocation,toolChecks=26,positive=1,negativeVectors=len(labels),labels=labels,testHashes=TESTS,helperSha256=data.sha((data.ROOT/'tools/quality/pure_jdbc_fixture_scope_v1.py').read_bytes()),productTestsExecuted=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,bug='BUG-2100',ykt='YKT-1847'))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
