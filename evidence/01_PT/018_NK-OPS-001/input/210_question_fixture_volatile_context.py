"""Read-only twelve-control source proof including monotone true publications; no original Test execution."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
R=Path(__file__).resolve().parents[4];BASE=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22470-question-volatile12-context-v2'
TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/QuestionControllerTest.java'
FIELDS={'failReceipt','verifyNoTransaction','afterReply','code','state','summary','answer','owner','count','total','replyId','responder'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
LITERAL=re.compile(r'"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/')
def mask(text):return LITERAL.sub(lambda m:''.join('\n' if x=='\n' else ' ' for x in m.group()),text)
def block_end(code,start):
    depth=1
    for at in range(start,len(code)):
        if code[at]=='{':depth+=1
        elif code[at]=='}':
            depth-=1
            if depth==0:return at+1
    raise ValueError('balanced block')
def main():
    assert not OUT.exists();bm=BASE/'manifest.json';assert sha(bm)=='e4eea946c71b78db2cca778259ef366cd4cd60c208708941a61067f48cee25a2';base=load(bm);assert sha(R/TEST)==base['begin']['inputHashes'][TEST];text=(R/TEST).read_text();code=mask(text);rows=[x for x in load(BASE/'unclassified-sites.json') if x['attributes']['rule']=='AvoidUsingVolatile'];assert len(rows)==12 and all(x['path']==TEST and x['attributes']['class']=='QuestionControllerTest.Fixture' for x in rows);assert {x['attributes']['variable'] for x in rows}==FIELDS
    line=lambda offset:code.count('\n',0,offset)+1;methods=[]
    for m in re.finditer(r'@Test\s+void\s+(\w+)\s*\(\s*\)(?:\s+throws\s+[^{}]+)?\s*\{',code):
        end=block_end(code,m.end());methods.append(dict(name=m[1],start=m.start(),end=end,body=code[m.end():end],beginLine=line(m.start()),endLine=line(end-1)))
    fields='|'.join(sorted(FIELDS,key=len,reverse=True));writes=[]
    for w in re.finditer(r'\bf\.('+fields+r')\s*=(?!=)',code):
        owners=[m for m in methods if m['start']<w.start()<m['end']];assert len(owners)==1;owner=owners[0];assert re.search(r'\b(?:var|Fixture)\s+f\s*=\s*new\s+Fixture\s*\(\s*\)',owner['body']);writes.append(dict(field=w[1],receiver='f',method=owner['name'],line=line(w.start()),offset=w.start(),localFixtureInMethod=True))
    assert not re.search(r'\bf\.('+fields+r')\s*(?:\+\+|--|[+\-*/|&^]=)',code);assert not re.search(r'(?:\+\+|--)\s*f\.('+fields+r')\b',code)
    fixture=re.search(r'\bclass\s+Fixture\b[^{}]*\{',code);assert fixture;fend=block_end(code,fixture.end());fc=code[fixture.end():fend];declLines={int(x['attributes']['beginline']) for x in rows};bare=[]
    for w in re.finditer(r'(?<![\w.])('+fields+r')\s*=(?!=)',fc):
        absolute=fixture.end()+w.start();at=line(absolute)
        if at in declLines:continue
        assert w[1]=='verifyNoTransaction' and re.match(r'\s*true\s*;',fc[w.end():]);before=fc[:w.start()];header=list(re.finditer(r'\b(?:QuestionController|AnnotationConfigWebApplicationContext)\s+(accepting|acceptanceMvc)\s*\(\s*\)\s*\{',before));assert header;bare.append(dict(field=w[1],receiver='this',method=header[-1][1],line=at,assignedBoolean=True,profile='IDEMPOTENT_MONOTONE_TRUE_PUBLICATION'))
    assert len(bare)==2 and {x['method'] for x in bare}=={'accepting','acceptanceMvc'};assert not re.search(r'(?<![\w.])('+fields+r')\s*(?:\+\+|--|[+\-*/|&^]=)',fc)
    phases=[]
    for m in methods:
        if 'Executors.newFixedThreadPool(' not in m['body']:continue
        first=code.index('pool.submit(',m['start'],m['end']);pw=[w for w in writes if w['method']==m['name']];assert all(w['offset']<first for w in pw);unbounded=[line(m['start']+x.start()) for x in re.finditer(r'\b(?:job|future)\.get\(\s*\)',code[m['start']:m['end']])];phases.append(dict(method=m['name'],beginLine=m['beginLine'],endLine=m['endLine'],firstSubmitLine=line(first),setupWrites=[dict(field=w['field'],line=w['line']) for w in pw],directControlWritesAfterFirstSubmit=0,acceptingMayPublishMonotoneTrue='f.accepting()' in m['body'],actualExecution=False,finiteWaitWitness='TimeUnit.SECONDS' in m['body'],unboundedFutureWaitLines=unbounded,deadlineIssueOpen=bool(unbounded)))
    assert len(phases)==2;assert not re.search(r'\bset(?:Accessible|Boolean|Int|Long)\s*\(',code);OUT.mkdir();context=dict(fieldNames=sorted(FIELDS),externalWrites=writes,fixtureMethodWrites=bare,concurrentPhases=phases,readModifyWriteControls=0,reflectionMutation=False,atomicAggregateTransitionClaimed=False,dynamicExecutionQualified=False,openDeadlineIssue='BUG-2432',openLateralIssue='YKT-2177')
    (OUT/'contexts.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n');value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',originalRawManifest=dict(path=str(bm.relative_to(R)),sha256=sha(bm)),testPath=TEST,testSha256=sha(R/TEST),targetSites=12,originalSites=rows,contextExternalWrites=len(writes),fixtureMethodMonotoneWrites=2,concurrentMethods=2,newIndividualClassifications=12,currentRawSitesRetained=346,subsetClassifiedBefore=271,subsetClassifiedAfter=283,subsetUnclassifiedBefore=75,subsetUnclassifiedAfter=63,inspectionStatus='COMPLETED_WITH_OPEN_TEST_DEADLINE_DEFECT',openTestDefect='BUG-2432',productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,sourceBytesUnchanged=True,suppressionAdded=False,ruleConfigurationChanged=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files={'contexts.json':sha(OUT/'contexts.json')},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)))
    (OUT/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,fields=12,externalWrites=len(writes),monotoneBareWrites=2,remaining=63,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
