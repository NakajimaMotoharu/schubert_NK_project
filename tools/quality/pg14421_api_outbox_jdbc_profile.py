"""Metadata-only API Outbox fixture checks; do not compile/load/invoke target classes."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_jdbc_fixture_scope_v2 as scope

TESTS={'OutboxMetricCollectorTest': {'path': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxMetricCollectorTest.java', 'sha256': '2c7b20b6944018b912d5f6ad0419e069b93c4a1d704d3958609043464f9d0bb4'}, 'OutboxObservationRepositoryTest': {'path': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxObservationRepositoryTest.java', 'sha256': '60de5831df6c273130930756bef2d5551c265d17eda8e2b7d80a0eb27bd2b9e8'}, 'OutboxRowsMetricRecorderTest': {'path': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxRowsMetricRecorderTest.java', 'sha256': '193ecfb3b0fd738452560f52fbe0a069aa097162fc75b74d53dfc804d160eb36'}, 'OutboxAgeMetricRecorderTest': {'path': 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxAgeMetricRecorderTest.java', 'sha256': 'f782006859ef273e9cb498a97ec8c20fc050de47c0ab1e53ca46d9ea8f9de2cf'}}
REQUIRED={'OutboxMetricCollectorTest': ['class OutboxMetricCollectorTest', 'new OutboxObservationRepository()'], 'OutboxObservationRepositoryTest': ['Proxy.newProxyInstance(', 'Connection.class', 'PreparedStatement.class', 'ResultSet.class', 'borrowed connection must not be mutated or closed', 'FROM schubert.mq_outbox GROUP BY status'], 'OutboxRowsMetricRecorderTest': ['class OutboxRowsMetricRecorderTest', 'SimpleMeterRegistry'], 'OutboxAgeMetricRecorderTest': ['class OutboxAgeMetricRecorderTest', 'SimpleMeterRegistry', '3045']}
OUT=data.BASE/'PG14421-api-outbox-jdbc-profile-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    texts={}
    for n,item in TESTS.items():
        raw=(data.ROOT/item['path']).read_bytes();assert data.sha(raw)==item['sha256'];texts[n]=raw.decode()
    assert scope.eligible(texts,REQUIRED) is True
    labels=[]
    def reject(label,value):
        assert scope.eligible(value,REQUIRED) is False;labels.append(label)
    for n in TESTS:
        for token in scope.FORBIDDEN:
            bad=copy.deepcopy(texts);bad[n]+='\n'+token;reject(n+':forbidden:'+token,bad)
        for token in REQUIRED[n]:
            bad=copy.deepcopy(texts);bad[n]=bad[n].replace(token,'REMOVED_REVIEWED_TEXT');reject(n+':missing:'+token,bad)
    reject('null',None);reject('empty',{});reject('unknown-key',{**texts,'Unknown':texts[next(iter(texts))]})
    bad=copy.deepcopy(texts);bad[next(iter(bad))]=None;reject('null-text',bad)
    assert len(labels)==len(set(labels))==len(scope.FORBIDDEN)*len(TESTS)+sum(map(len,REQUIRED.values()))+4==77
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',invocation=invocation,positive=1,negativeVectors=len(labels),toolChecks=1+len(labels),labels=labels,testHashes=TESTS,required=REQUIRED,helperSha256=data.sha((data.ROOT/'tools/quality/reviewed_jdbc_fixture_scope_v2.py').read_bytes()),productTestsExecuted=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,safetyOrPermissionOverride=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
