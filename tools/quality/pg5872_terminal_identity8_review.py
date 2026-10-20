"""Recheck eight changed-owner Throwable identity guards; no old PT/native or rule suppression."""
import copy
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT,sha
from static_disposition_overlay import BASE,load
from pg5860_terminal_whole import SOURCE,W
from pg5820_identity14_review import guarded_identity,prior_reason

OLD='6b5cea563b6f68b0b604afc06490063793e49662'


def prior_index(rows,held):
    byid={r['findingId']:r for r in rows};result={};cache={}
    for ident in held:
        row=byid[ident];path=row['sourcePath']
        if path not in cache:cache[path]=subprocess.check_output(['git','show',OLD+':'+path],cwd=ROOT,text=True)
        text=cache[path]
        if hashlib.sha256(text.encode()).hexdigest()!=row['sourceSha256']or row['beginline']!=row['endline']:raise ValueError('exact previous guard source span')
        expr=text.splitlines()[int(row['beginline'])-1][int(row['begincolumn'])-1:int(row['endcolumn'])].rstrip(')');key=(path,re.sub(r'\s+','',expr))
        if key in result:raise ValueError('one prior identity per source/symbol pair')
        result[key]=row
    return result


def main():
    parent=BASE/'PG5868-terminal-dispositions-v1/manifest.json';digest='58408654af3af57edc4d8e961ecf7b14dde788dccc63e37419a9b6df300a1d90';rows=load(parent,digest,SOURCE);meta=json.loads(parent.read_bytes())
    oldp=BASE/'PG5846-current-static3967-v3/manifest.json';oldrows=load(oldp,'f42681dbfd498db8a13b9374d0d2c94c9cddc149fea8f83597ce0d90b0491a9d',OLD);held={r['findingId']for r in meta['heldPriorDispositions']};prior=prior_index(oldrows,held)
    fp=W/'pg5870-terminal-reference-facts-v1/manifest.safe.json'
    if sha(fp)!='666f75579d550f7b5ec9cd69600dffe5d7cdf1e8d29ac68a9c70ae6b8445b45e':raise ValueError('actual current compiler facts')
    typed=json.loads(fp.read_bytes());proof=json.loads((W/'pg5858-terminal-static-v1/manifest.safe.json').read_bytes())
    if typed['source']!=SOURCE or typed['actualExit']!=typed['compileExit']or typed['compileExit']!=typed['independentFixtureExit']or typed['actualExit']!=0 or typed['identity']['physicalMainSha256']!=proof['auxClassHashes']:raise ValueError('actual current type inputs and independent fixture0')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=typed['identity']['sourceHashes']:raise ValueError('all851 current Main inputs unchanged')
    facts={(f['path'],int(f['firstLine']),int(f['firstColumn'])):f for f in typed['rows']};decisions=[];used=set()
    for row in rows:
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or row['rule']!='CompareObjectsWithEquals':continue
        fact=facts.get((row['sourcePath'],int(row['beginline']),int(row['begincolumn'])))
        if fact is None:continue
        op='!='if fact['operator']=='NOT_EQUAL_TO'else'=='if fact['operator']=='EQUAL_TO'else None
        if op is None:continue
        old=prior.get((row['sourcePath'],fact['leftExpression']+op+fact['rightExpression']))
        if old is None:continue
        if int(row['endline'])!=int(fact['lastLine'])or int(row['endcolumn'])!=int(fact['lastColumn'])+1 or any(t not in('java.lang.Throwable','java.lang.Exception','java.lang.RuntimeException','dev.codex.schubert.nk.protocol.codec.PermanentProtocolException')for t in(fact['leftType'],fact['rightType'])):raise ValueError('exact typed Throwable condition, no value comparison exemption')
        text=(ROOT/row['sourcePath']).read_text()
        if sha(ROOT/row['sourcePath'])!=row['sourceSha256']:raise ValueError('actual whole owner source')
        shape=guarded_identity(text,fact,False);used.add(old['findingId']);value=copy.deepcopy(row)
        value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition='REQUIRED_CONTRACT',priorFindingId=old['findingId'],priorReason=prior_reason(old),historicalWholeCaseRefs=old.get('currentWholeCaseRefs',[]),recheckedChangedSource=True,newDispositionCreated=False,reason='PG-D444; SS322/352. The compiler resolves this exact Throwable pair and the whole condition directly controls diagnostic append/early-return. Identity distinguishes nodes even for equals-true distinct failures. No assignment/callback intervenes. This narrow retention rationale does not establish receiver admission coverage, retry policy, Root ownership or cleanup.',typedReferenceFact=fact,typedFactsSha256=sha(fp),directGuardShape=shape,currentWholeCaseRefs=[],currentWholeJoinPending=True,rawWarningRetained=True)
        decisions.append(value)
    if len(held)!=8 or used!=held or len(decisions)!=8:raise ValueError('all and only eight changed prior guards')
    out=BASE/'PG5872-terminal-identity8-v1';os.umask(0o077);out.mkdir();dp=out/'decisions.json'
    with dp.open('x')as f:json.dump(decisions,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    counts=Counter(r['status']for r in rows);counts['NOT_REVIEWED_CURRENT_SOURCE']-=8;counts['SOURCE_REBOUND_CURRENT_WHOLE_PENDING']+=8
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':parent.relative_to(ROOT).as_posix(),'baseManifestSha256':digest,'decisionsSha256':sha(dp),'typedFactsSha256':sha(fp),'rawFindings':1586,'statusCounts':dict(counts),'recheckedChangedPrior':8,'newIndividualDispositions':0,'currentWholeJoinPending':True,'executedPtAdded':0,'ptAlternativeCompleted':0,'rawWarningsRemoved':0,'sourceCodeChanged':False,'analyzerReexecuted':False,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'decisionsSha256':sha(dp)}))


if __name__=='__main__':main()
