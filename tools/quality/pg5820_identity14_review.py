"""Thirteen source-changed guards rechecked and one constructor identity contract; no PT credit."""
import copy
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT,sha
from static_disposition_overlay import BASE,load
from pg5808_rollback_whole import SOURCE,W


def prior_reason(row):
    value=row.get('reason')or row.get('priorReason')
    if not isinstance(value,str)or not value.strip():raise ValueError('verified prior individual reason required')
    return value


def guarded_identity(text,fact,constructor=False):
    left,right=fact['leftExpression'],fact['rightExpression'];op='!='if fact['operator']=='NOT_EQUAL_TO'else'=='if fact['operator']=='EQUAL_TO'else None
    if op is None or not left.isidentifier()or not right.isidentifier()or left==right:raise ValueError('two distinct simple reference symbols')
    lines=text.splitlines(keepends=True)
    if fact['firstLine']!=fact['lastLine']:raise ValueError('one exact binary source span')
    start=sum(map(len,lines[:int(fact['firstLine'])-1]))+int(fact['firstColumn'])-1;end=sum(map(len,lines[:int(fact['lastLine'])-1]))+int(fact['lastColumn'])
    expr=text[start:end]
    if re.sub(r'\s+','',expr)!=left+op+right or re.search(r'\bif\s*\(\s*$',text[:start])is None:raise ValueError('actual compiler expression is the whole if condition')
    tail=text[end:]
    if constructor:
        if fact['method']!='<init>'or (left,right)!=('rollbackFailure','primary')or op!='!=':raise ValueError('exact new constructor cause-node de-duplication only')
        if re.match(r'\s*\)\s*\{\s*addSuppressed\(rollbackFailure\);',tail)is None:raise ValueError('fresh wrapper receives only distinct rollback node')
        if 'Objects.requireNonNull(primary, "primary failure")'not in text or 'Objects.requireNonNull(rollbackFailure, "rollback failure")'not in text:raise ValueError('both constructor invariants before guard')
        return 'FRESH_WRAPPER_CAUSE_NODE_DEDUPLICATION'
    pattern=r'\s*\)\s*(?:\{\s*)?(\w+)\.addSuppressed\((\w+)\);'if op=='!='else r'\s*\)\s*return;\s*(\w+)\.addSuppressed\((\w+)\);'
    match=re.match(pattern,tail)
    if match is None or set(match.groups())!={left,right}:raise ValueError('same symbol pair controls append directly, no intervening mutation or callback')
    return 'DISTINCT_THROWABLE_APPEND'if op=='!='else'IDENTICAL_THROWABLE_EARLY_RETURN'


def main():
    parent=BASE/'PG5816-current-dispositions-v1/manifest.json';digest='7faf04eb1070ed49c2284a75ec361e7f67f1374a2ba7c55e30a11aac9722c5c8';rows=load(parent,digest,SOURCE);meta=json.loads(parent.read_bytes())
    oldp=BASE/'PG5798-lifetime-empty4-v1/manifest.json';oldrows=load(oldp,'dd2928921bae7193dcd95e1a604a85393abb3d8554a944247ebb8b6dd4e22c5c','2bbb85a297d7f7bd1b0c243d343e0da509faf99a');held={r['findingId']for r in meta['heldPriorDispositions']};old_by_id={r['findingId']:r for r in oldrows};prior_index={};cache={}
    for ident in held:
        row=old_by_id[ident];path=row['sourcePath']
        if path not in cache:cache[path]=subprocess.check_output(['git','show','2bbb85a297d7f7bd1b0c243d343e0da509faf99a:'+path],cwd=ROOT,text=True)
        text=cache[path]
        if hashlib.sha256(text.encode()).hexdigest()!=row['sourceSha256']or row['beginline']!=row['endline']:raise ValueError('exact previous source binary expression')
        expr=text.splitlines()[int(row['beginline'])-1][int(row['begincolumn'])-1:int(row['endcolumn'])].rstrip(')');key=(path,re.sub(r'\s+','',expr))
        if key in prior_index:raise ValueError('unambiguous old guard symbol pair')
        prior_index[key]=row
    fp=W/'pg5818-current-reference-facts-v1/manifest.safe.json'
    if sha(fp)!='7a30e3ed84fcacdb928317fec8a9182aa9fbdbd2e426f590be3123de15df72a4':raise ValueError('actual current76 type facts')
    typed=json.loads(fp.read_bytes());proof=json.loads((W/'pg5810-rollback-static-reauth-v1/manifest.safe.json').read_bytes())
    if typed['source']!=SOURCE or typed['actualExit']!=typed['compileExit']or typed['compileExit']!=typed['independentFixtureExit']or typed['actualExit']!=0 or typed['identity']['physicalMainSha256']!=proof['auxClassHashes']:raise ValueError('actual current type input and independent fixture0')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=typed['identity']['sourceHashes']:raise ValueError('all850 source fixed')
    facts={(f['path'],int(f['firstLine']),int(f['firstColumn'])):f for f in typed['rows']}
    qp=BASE/'PG5812-current-rollback54-v1/manifest.json'
    if sha(qp)!='b822a415878f1794b30f27320bbfc1353afd6b7aaa8b07dd7fed25bb5402b797':raise ValueError('actual current54, not a whole success')
    selected=json.loads(qp.read_bytes());decisions=[];used=set();new=0
    for row in rows:
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or row['rule']!='CompareObjectsWithEquals':continue
        fact=facts.get((row['sourcePath'],int(row['beginline']),int(row['begincolumn'])))
        if fact is None:continue
        op='!='if fact['operator']=='NOT_EQUAL_TO'else'=='if fact['operator']=='EQUAL_TO'else None
        if op is None:continue
        old=prior_index.get((row['sourcePath'],fact['leftExpression']+op+fact['rightExpression']));constructor=row['sourcePath'].endswith('/UnconfirmedJmsRollbackException.java')
        if old is None and not constructor:continue
        if int(row['endline'])!=int(fact['lastLine'])or int(row['endcolumn'])!=int(fact['lastColumn'])+1 or any(t not in('java.lang.Throwable','java.lang.Exception','java.lang.RuntimeException','dev.codex.schubert.nk.protocol.codec.PermanentProtocolException')for t in(fact['leftType'],fact['rightType'])):raise ValueError('exact current typed Throwable span, no primitive/value exemption')
        text=(ROOT/row['sourcePath']).read_text()
        if sha(ROOT/row['sourcePath'])!=row['sourceSha256']:raise ValueError('current full owner source')
        shape=guarded_identity(text,fact,constructor);value=copy.deepcopy(row)
        reason='PG-D440/441; SS321/352. Reference identity distinguishes actual Throwable nodes even for equals-true distinct failures. The current compiler resolves this exact pair and direct append/early-return control, with no intervening assignment/callback. This local retention fact does not validate retry policy, resource completion, or BUG1494 fatal-isolation handling.'
        extra={}
        if old is not None:
            used.add(old['findingId']);extra.update(priorFindingId=old['findingId'],priorReason=prior_reason(old),historicalWholeCaseRefs=old.get('currentWholeCaseRefs',[]),recheckedChangedSource=True,newDispositionCreated=False)
        else:
            new+=1;refs=[r for r in selected['caseTrace']if r['designTestId']in{'PT-JMS-UNC'+str(i).zfill(3)for i in range(5,9)}]
            counter=selected['targetCounters']['protocol:protocol/transport/UnconfirmedJmsRollbackException']
            if len(refs)!=4 or any(counter[k]['missed']for k in('LINE','METHOD','CLASS','BRANCH')):raise ValueError('new constructor independent same/distinct/disabled/null cases and actual four counters')
            reason='PG-D441; SS321/352. This fresh wrapper retains primary as its cause; only a distinct rollback Throwable becomes an additional diagnostic node. Value equality is not node identity. Current Throwable parameters and exact constructor guard, independent same/distinct-equals-true/disabled-suppression/null fixtures and actual both identity branches establish this narrow contract, not external receiver or owned cleanup success.'
            extra.update(currentSelectedCaseRefs=refs,currentSelectedManifestSha256=sha(qp),actualConstructorCounters=counter,newDispositionCreated=True)
        value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition='REQUIRED_CONTRACT',reason=reason,typedReferenceFact=fact,typedFactsSha256=sha(fp),directGuardShape=shape,currentWholeCaseRefs=[],currentWholeJoinPending=True,rawWarningRetained=True,**extra);decisions.append(value)
    if used!=held or len(used)!=13 or new!=1 or len(decisions)!=14:raise ValueError('all and only thirteen moved guards and one new constructor')
    out=BASE/'PG5820-identity14-v3';os.umask(0o077);out.mkdir();dp=out/'decisions.json'
    with dp.open('x')as f:json.dump(decisions,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    counts=Counter(r['status']for r in rows);counts['NOT_REVIEWED_CURRENT_SOURCE']-=14;counts['SOURCE_REBOUND_CURRENT_WHOLE_PENDING']+=14
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':parent.relative_to(ROOT).as_posix(),'baseManifestSha256':digest,'decisionsSha256':sha(dp),'typedFactsSha256':sha(fp),'rawFindings':1595,'statusCounts':dict(counts),'recheckedChangedPrior':13,'newIndividualDispositions':1,'currentWholeJoinPending':True,'executedPtAdded':0,'ptAlternativeCompleted':0,'rawWarningsRemoved':0,'analyzerReexecuted':False,'sourceCodeChanged':False,'BUG1494Resolved':False,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'decisionsSha256':sha(dp)}))


if __name__=='__main__':main()
