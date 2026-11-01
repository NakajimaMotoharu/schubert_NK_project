"""Metadata-only clock-label correction witness; no Product methods or tests."""
from datetime import datetime
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18268-checkpoint-clock-correction-v1'
DOCS=['documents/400_PGPT/450_品質/456_領域別進捗・利用枠・中断再開管理.md','documents/400_PGPT/450_品質/460_基盤残件・再開優先順.md']
ROWS=[('9d62d676d329831e8dc389d7a31449f99fe600b7','2026-11-01T21:48:00+09:00'),('8e0575f37697d27db6f1d6ce43ce250c70746ffa','2026-11-01T21:59:00+09:00')]
def require_not_future(label,committed):
    if datetime.fromisoformat(label)>datetime.fromisoformat(committed):raise ValueError('future checkpoint label')
def main():
    invocation=capture(__file__);assert not OUT.exists()
    evidence=[];rejected=[]
    for commit,label in ROWS:
        actual=subprocess.check_output(['git','show','-s','--format=%cI',commit],cwd=data.ROOT,text=True).strip()
        docs={}
        for name in DOCS:
            blob=subprocess.check_output(['git','show',commit+':'+name],cwd=data.ROOT)
            short=label[11:16]
            assert ('2026-11-01 '+short+' JST').encode() in blob
            docs[name]=data.sha(blob)
        try:require_not_future(label,actual)
        except ValueError:rejected.append(label)
        else:raise AssertionError('future label not rejected')
        require_not_future(actual,actual)
        evidence.append(dict(commit=commit,commitTime=actual,invalidCheckpointLabel=label,originalDocumentHashes=docs))
    assert len(rejected)==2
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,evidence=evidence,negativeFutureVectors=2,positiveBoundaryVectors=2,actualProductTestsExecuted=0,productTestsReexecuted=0,staticReviewOnly=True,priorProductCountersChanged=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
