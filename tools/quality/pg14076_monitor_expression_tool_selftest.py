"""New monitor-expression schema only; no replay of prior core/manifest vectors."""
import copy
import hashlib
import json
import static_context_reader_v2 as reader
from static_context_post_v1 import independent_location
from pg14060_static_context_common_core_selftest import fixture,NAME,TEXT
from host_tool_invocation import capture,verify

OUT=reader.data.BASE/'PG14076-monitor-expression-tool-selftest-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    data=fixture();plan,catalog,facts,texts,owners=data
    qualified=TEXT.replace('synchronized (lock)','synchronized (owned.lock)')
    target=plan['targets'][NAME]
    target.update(sha256=hashlib.sha256(qualified.encode()).hexdigest(),monitor={'PMD-00001':'owned.lock'},guards=['private final Object lock = new Object();','synchronized (owned.lock)'],ordered=[])
    catalog[0]['inputSha256']=facts[0]['sourceSha256']=target['sha256'];texts[NAME]=qualified
    row,=reader.bind_rows(*data)
    assert row['monitor']=='owned.lock' and independent_location(qualified,catalog[0]['attributes'])==(77,89,'synchronized')
    positives=['qualified-monitor-row-and-independent-golden']
    literal=json.loads('{"java":"owner != null","empty":null}')
    assert literal['java']=='owner != null' and literal['empty'] is None
    positives.append('java-null-string-not-structural-null')
    negatives=[]
    def reject(label,action):
        try:action()
        except ValueError:negatives.append(label)
        else:raise AssertionError('unsafe monitor schema admitted: '+label)
    for label,value in [('empty-map',{}),('unknown-id',{'PMD-00002':'owned.lock'}),('extra-id',{'PMD-00001':'owned.lock','PMD-00002':'lock'}),('null-map-value',{'PMD-00001':None}),('bool-map-value',{'PMD-00001':True}),('list-map-value',{'PMD-00001':[]}),('expression-call',{'PMD-00001':'owner().lock'}),('expression-index',{'PMD-00001':'owner[0].lock'}),('deeper-expression',{'PMD-00001':'a.b.lock'}),('empty-name',''),('space','owned. lock'),('null',None)]:
        bad=copy.deepcopy(plan);bad['targets'][NAME]['monitor']=value
        assert reader.wire(bad)!=reader.wire(plan)
        reject(label,lambda bad=bad:reader.validate_plan(bad))
    bad=copy.deepcopy(data);bad[0]['targets'][NAME]['monitor']={'PMD-00001':'other.lock'}
    reject('wrong-original-monitor-expression',lambda:reader.bind_rows(*bad))
    bad=copy.deepcopy(data);bad[0]['targets'][NAME]['ids'].append('PMD-00002')
    reject('missing-mapped-original-id',lambda:reader.bind_rows(*bad))
    assert len(positives)==2 and len(negatives)==14
    verify(invocation);OUT.mkdir()
    reader.data.write(OUT/'manifest.json',dict(actualExit=0,source=reader.cfg.SOURCE,invocation=invocation,toolPositiveVectors=len(positives),positiveLabels=positives,toolNegativeVectors=len(negatives),negativeLabels=negatives,productTestsExecuted=0,coverage=None,newAccepted=0,priorCoreVectorsReexecuted=0,actualExternalActions=0,pureMemoryMetadataOnly=True,correctedToolBugs=['BUG2087/YKT1835','BUG2088/YKT1836'],formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(reader.data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
