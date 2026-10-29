"""Metadata-only Web Outbox fixture checks; do not compile/load/invoke target classes."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_jdbc_fixture_scope_v2 as scope

TESTS=json.loads("{\"WebOutboxMetricCollectorTest\":{\"path\":\"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebOutboxMetricCollectorTest.java\",\"sha256\":\"4c4596c912ef7772249b63e75becd7b396deb6defce9599bfb829e6e711240d5\"},\"WebOutboxMetricRecorderTest\":{\"path\":\"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebOutboxMetricRecorderTest.java\",\"sha256\":\"ff7e8faa0bc057eaa1a691b0ee855b7c37b65463d458a573667e3896e1a41b32\"},\"WebOutboxObservationRepositoryTest\":{\"path\":\"src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebOutboxObservationRepositoryTest.java\",\"sha256\":\"175d1c5385409c114cc2e8cf4d80f7028acf2c5bac6918e6293191a7d2f88078\"}}")
REQUIRED=json.loads("{\"WebOutboxObservationRepositoryTest\":[\"Proxy.newProxyInstance(\",\"Connection.class\",\"PreparedStatement.class\",\"ResultSet.class\",\"borrowed connection must not be mutated or closed\",\"FROM schubert_web_session.web_log_outbox GROUP BY status\"],\"WebOutboxMetricCollectorTest\":[\"class WebOutboxMetricCollectorTest\",\"new WebOutboxObservationRepository()\",\"Thread.State.BLOCKED\"],\"WebOutboxMetricRecorderTest\":[\"class WebOutboxMetricRecorderTest\",\"SimpleMeterRegistry\",\"90715647\"]}")
OUT=data.BASE/'PG14417-web-outbox-jdbc-profile-v1'

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
    assert len(labels)==len(set(labels))==len(scope.FORBIDDEN)*len(TESTS)+sum(map(len,REQUIRED.values()))+4==61
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',invocation=invocation,positive=1,negativeVectors=len(labels),toolChecks=1+len(labels),labels=labels,testHashes=TESTS,required=REQUIRED,helperSha256=data.sha((data.ROOT/'tools/quality/reviewed_jdbc_fixture_scope_v2.py').read_bytes()),productTestsExecuted=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,safetyOrPermissionOverride=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
