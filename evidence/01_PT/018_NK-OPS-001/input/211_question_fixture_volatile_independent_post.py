"""Independent AST declarations/assignments/owner scopes/concurrent phases, deadline defect remains open."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22470-question-volatile12-context-v2';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22474-question-volatile12-independent-v1';SLOT=RUNS/'pg22474-question-volatile12-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def contract(fields,writes,bare,phases,rmw):
    expected={'failReceipt','verifyNoTransaction','afterReply','code','state','summary','answer','owner','count','total','replyId','responder'}
    if set(fields)!=expected or len(fields)!=12 or rmw:return False
    if len(bare)!=2 or {(x['method'],x['field'],x['rhs']) for x in bare}!={('accepting','verifyNoTransaction','true'),('acceptanceMvc','verifyNoTransaction','true')}:return False
    if any(not x['ownerVerified'] for x in writes):return False
    if len(phases)!=2 or any(x['directWritesAfterSubmit'] for x in phases):return False
    return True

def main():
    assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='b58e0dd8024f343bf54392ac8f94947af271fe250c69cd436e6b45a48206b649' and m['actualExit']==0 and m['source']=='a0e505937b602df4a7cfa00e8761b21bc48b703e';ctx=load(P/'contexts.json');assert sha(P/'contexts.json')==m['files']['contexts.json'];test=R/m['testPath'];assert sha(test)==m['testSha256']==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+m['testPath']],cwd=R)).hexdigest();assert m['openTestDefect']=='BUG-2432' and not ctx['dynamicExecutionQualified']
    tool=R/'evidence/01_PT/018_NK-OPS-001/input/212_QuestionFixtureControlAstCheck.java';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert sha(tool)==hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(tool.relative_to(R))],cwd=R)).hexdigest();SLOT.mkdir();(SLOT/'source').mkdir();(SLOT/'classes').mkdir();mirror=SLOT/'source/QuestionFixtureControlAstCheck.java';mirror.write_bytes(tool.read_bytes());assert sha(mirror)==sha(tool);c.SLOT=SLOT;jdk=R.parent/'toolchain/jdk-25.0.4/bin';stages={}
    stages['tool-javac']=c.step('tool-javac',[str(jdk/'javac'),'-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-d',str(SLOT/'classes'),str(mirror)],R);assert stages['tool-javac']['actualExit']==0
    stages['parse']=c.step('parse',[str(jdk/'java'),'-cp',str(SLOT/'classes'),'QuestionFixtureControlAstCheck',str(R),m['testPath']],R,timeout=120);assert stages['parse']['actualExit']==0 and not stages['parse']['timedOut'];ast=[x.split('\t') for x in (SLOT/'parse.stdout').read_text().splitlines()];fieldrows=[x for x in ast if x[0]=='FIELD'];assert len(fieldrows)==12 and all(x[1]=='QuestionControllerTest.Fixture' for x in fieldrows);fields={x[2]:dict(type=x[3],line=int(x[4])) for x in fieldrows};assert set(fields)==set(ctx['fieldNames'])
    for row in m['originalSites']:assert fields[row['attributes']['variable']]['line']==int(row['attributes']['beginline'])
    owners=[x for x in ast if x[0]=='LOCAL_F'];writes=[];bare=[]
    for x in ast:
        if x[0]!='WRITE':continue
        _,cl,method,receiver,field,line,rhs=x;line=int(line)
        if receiver=='f':
            candidates=[o for o in owners if o[1]==cl and o[2]==method and int(o[3])<line and int(o[4])<=line<=int(o[5])];assert len(candidates)==1;writes.append(dict(field=field,receiver=receiver,method=method,line=line,ownerVerified=True,rhs=rhs))
        else:assert cl=='QuestionControllerTest.Fixture';bare.append(dict(field=field,method=method,line=line,rhs=rhs))
    assert len(writes)==47 and {(x['field'],x['method'],x['line']) for x in writes}=={(x['field'],x['method'],x['line']) for x in ctx['externalWrites']};assert {(x['field'],x['method'],x['line']) for x in bare}=={(x['field'],x['method'],x['line']) for x in ctx['fixtureMethodWrites']}
    phases=[]
    for p in ctx['concurrentPhases']:
        submits=[int(x[4]) for x in ast if x[0]=='CALL' and x[2]==p['method'] and x[3]=='pool.submit'];assert min(submits)==p['firstSubmitLine'];after=[x for x in writes if x['method']==p['method'] and x['line']>=min(submits)];assert not after;phases.append(dict(method=p['method'],directWritesAfterSubmit=len(after),firstSubmitLine=min(submits),acceptingCalls=sum(x[0]=='CALL' and x[2]==p['method'] and x[3]=='f.accepting' for x in ast)))
    rmw=[x for x in ast if x[0]=='RMW'];assert contract(fields,writes,bare,phases,rmw);waits=[x for x in ast if x[0]=='UNBOUNDED_GET'];assert len(waits)==1 and waits[0][2]=='rcpt006HConcurrentSameTokenAndImmutableLocator';assert [int(waits[0][4])]==next(p['unboundedFutureWaitLines'] for p in ctx['concurrentPhases'] if p['method']==waits[0][2]);assert ctx['openDeadlineIssue']=='BUG-2432'
    import copy
    negatives=[]
    for kind in ['field-loss','nonmonotone-boolean','missing-owner','concurrent-write','rmw']:
        f,w,b,p,z=copy.deepcopy((fields,writes,bare,phases,rmw))
        if kind=='field-loss':f.pop('replyId')
        elif kind=='nonmonotone-boolean':b[0]['rhs']='false'
        elif kind=='missing-owner':w[0]['ownerVerified']=False
        elif kind=='concurrent-write':p[0]['directWritesAfterSubmit']=1
        else:z.append(['RMW'])
        assert not contract(f,w,b,p,z);negatives.append(kind)
    OUT.mkdir();files={}
    for name in ['tool-javac.stdout','tool-javac.stderr','tool-javac-exit.safe.json','parse.stdout','parse.stderr','parse-exit.safe.json']:(OUT/name).write_bytes((SLOT/name).read_bytes());files[name]=sha(OUT/name)
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalContextManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),testPath=m['testPath'],testSha256=m['testSha256'],targetSites=12,independentlyParsedFields=fields,externalWrites=47,fixtureMethodMonotoneWrites=bare,concurrentPhases=phases,unboundedFutureWaits=waits,openTestDefect='BUG-2432',openYkt='YKT-2177',deadlineOrThreadOwnershipQualified=False,negativeMetadataGuards=negatives,newIndividualClassifications=12,currentRawSitesRetained=346,subsetClassifiedBefore=271,subsetClassifiedAfter=283,subsetUnclassifiedBefore=75,subsetUnclassifiedAfter=63,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,sourceBytesUnchanged=True,suppressionAdded=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,stages=stages,files=files,tool=dict(path=str(tool.relative_to(R)),sha256=sha(tool),mirrorSha256=sha(mirror)),verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=head))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,fields=12,writes=47,remaining=63,deadlineDefectOpen=True,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
