"""Four exact notification-only catches; actual3939 binding, no runtime execution."""
import copy
import json
import os
import re
from collections import Counter
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT,sha
from static_disposition_overlay import BASE,load,apply_decisions

SOURCE='2bbb85a297d7f7bd1b0c243d343e0da509faf99a'
PARENT='75b86e546fd5266d25b89cb509df1b13854ac2fd18c876921b108a7f53bf4b55'
SPECS={
 ('ApiProcessLifetime.java',120):('java.lang.IllegalStateException','close()',
  ['api.bootstrap.ApiProcessLifetimeTest'],
  'Shutdown is already in progress for the exact registered hook. The catch only ignores removeShutdownHook refusal; the enclosing finally still counts down finished after caller-owned release. No close, ACK, retry or success marker occurs in this catch. The JVM hook waits on the same finished latch. This is not a proof that any external process has ended.'),
 ('WebProcessLifetime.java',88):('java.lang.IllegalStateException','close()',
  ['web.bootstrap.WebProcessLifetimeTest'],
  'The exact hook is already participating in JVM shutdown. stop is set before removal, installed is cleared once, and finally notifies finished under the private state lock. Removal refusal must not suppress the owner-completion notification. External resource confirmation is a caller precondition, not proved here.'),
 ('WebProcessLifetime.java',107):('java.lang.InterruptedException','holdUnknownInterval()',
  ['web.bootstrap.WebUnknownRetentionTest'],
  'A sleep interruption is only an observation wakeup. retainUnknown immediately repeats this finite interval without releasing the retained failure frame or resources. Sleep consumes the interrupt; restoring it here would spin on every next sleep. No termination, cleanup or retry is inferred from a wakeup. This is a static local notification contract, not current VM ownership evidence.'),
 ('ServiceProcessResources.java',195):('java.lang.InterruptedException','observeUnconfirmed()',
  ['api.file.ServiceNativeReleaseTest','api.file.ServiceOwnedReleaseTest'],
  'Only the finite sleep interval returns; each ownedRelease/release failure catch contains its enclosing endless observation loop. Interruption never exits that failure frame, calls release again, or unwinds outer resources. Consuming the sleep interrupt avoids immediate busy rethrow. Real pending resource release remains unconfirmed, not made successful by this decision.')}


def empty_block(text,end):
    match=re.match(r'\)\s*\{(.*?)\}',text[end:],re.S)
    if match is None:raise ValueError('one immediate catch block')
    body=re.sub(r'/\*.*?\*/|//[^\n]*','',match[1],flags=re.S)
    if body.strip():raise ValueError('only the exact comment-only notification catch')


def main():
    parent=BASE/'PG5792-current-static-whole-v1/manifest.json';rows=load(parent,PARENT,SOURCE)
    qp=BASE/'PG5780-current3939-cases/qualification.json';cp=qp.with_name('cases.json')
    if sha(qp)!='1a5a5db819bde6bf01c85b4bb43017b8aae15bd59407b66adfbc4f5a0ca23c45'or sha(cp)!='6b8489660ecb397be6e020893eb3257df216ed5845923c4c93c832451b99bfbb':raise ValueError('actual source-bound original3939 only')
    q=json.loads(qp.read_bytes());cases=json.loads(cp.read_bytes());fp=ROOT.parent/'pgpt-runs/PG379/pg5770-current-catch-facts-v1/manifest.safe.json'
    if sha(fp)!='63e865210e51cdb6dcae78f0784d970b1bc1fa38aae403acab4f9e843b69d7e5':raise ValueError('exact prior typed catch facts')
    facts=json.loads(fp.read_bytes());decisions=[]
    for row in rows:
        key=(Path(row['sourcePath']).name,int(row['beginline']));spec=SPECS.get(key)
        if spec is None or row['rule']!='EmptyCatchBlock':continue
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE':raise ValueError('no repeated disposition')
        path=row['sourcePath'];text=(ROOT/path).read_text()
        if sha(ROOT/path)!=row['sourceSha256']or facts['identity']['sourceHashes'][path]!=row['sourceSha256']:raise ValueError('entire current owning source exact before typed reuse')
        module=path.split('/')[1].removeprefix('schubert-nk-');cls=path.split('/src/main/java/')[1][:-5]
        own={k:v for k,v in q['allPhysicalMainSha256'].items()if k==module+':'+cls+'.class'or k.startswith(module+':'+cls+'$')}
        if not own or any(facts['identity']['physicalMainSha256'].get(k)!=v for k,v in own.items()):raise ValueError('all current actual owning class bytes unchanged')
        matches=[r for r in facts['rows']if r['path']==path and int(r['firstLine'])==key[1]]
        if len(matches)!=1:raise ValueError('one exact typed catch parameter')
        fact=matches[0]
        if fact['type']!=spec[0]or not fact['method'].endswith('#'+spec[1])or any(fact[k]!='0'for k in('returns','sameThrows','otherThrows','assignments','breaks','continues')):raise ValueError('typed catch and no executable transfer/state mutation')
        empty_block(text,int(fact['end']))
        if spec[1]=='close()':
            if not all(s in text for s in('removeShutdownHook(hook)','installed = false','finally {','finished.countDown()')):raise ValueError('exact finally notification owner contract')
        else:
            if 'while (true)'not in text or 'Thread.sleep(1000)'not in text:raise ValueError('outer retaining loop and finite observation, no release on wake')
        refs=[c for c in cases if c['class']in{'dev.codex.schubert.nk.'+s for s in spec[2]}]
        if not refs or any(c['result']!='PASS_ORIGINAL_XML'for c in refs):raise ValueError('actual current original case identities')
        decision=copy.deepcopy(row);decision.update(status='REQUIRED_CONTRACT',reason='SS342/343/352; PG-D334/369/378. '+spec[3],typedCatchFact=fact,typedFactsSha256=sha(fp),owningCurrentClassSha256=own,currentWholeCaseRefs=refs,currentWholeQualificationSha256=sha(qp),currentWholeJoinPending=False,rawWarningRetained=True,localStaticContractOnly=True,externalOwnershipConfirmed=False,newPtExecuted=0)
        decisions.append(decision)
    if len(decisions)!=4:raise ValueError('all and only four exact catches')
    final=apply_decisions(rows,decisions);counts=dict(Counter(r['status']for r in final));out=BASE/'PG5798-lifetime-empty4-v1';os.umask(0o077);out.mkdir()
    dp=out/'decisions.json'
    with dp.open('x')as f:json.dump(decisions,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':parent.relative_to(ROOT).as_posix(),'baseManifestSha256':PARENT,'decisionsSha256':sha(dp),'newIndividualDispositions':4,'rawFindings':len(rows),'statusCounts':counts,'currentWholeQualificationSha256':sha(qp),'executedPtAdded':0,'ptAlternativeCompleted':0,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'externalResourceConfirmation':False,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'decisionsSha256':sha(dp)}))


if __name__=='__main__':main()
