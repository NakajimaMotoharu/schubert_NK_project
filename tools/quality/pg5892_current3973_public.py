"""Project genuine3973 original XML and all six terminal contracts; never replay PT."""
import ast
import hashlib
import json
import os
from pyflakes.api import check
from lan_server import run,copy
import pg5864_current3971_public as previous
from pg5888_terminal_serial_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,added_cases


def payload(data):
    raw=previous.payload(data).replace('PG5860','PG5886')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3971:return ast.copy_location(ast.Constant(3973),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<original3973 case allowlist reader>'):raise ValueError('complete generated namespace')
    if 'PG5860'in raw or 'Popen'in raw:raise ValueError('current original artifacts only')
    return raw


def terminal_trace(cases,selected,new):
    trace=[];newtrace=[]
    for design in selected['caseTrace']:
        labels={hashlib.sha256(s.encode()).hexdigest()for s in(design['method'],design['method']+'()')};actual=[r for r in cases if r['class']==design['class']and r['caseNameSha256']in labels]
        if len(actual)!=1:raise ValueError('one actual full XML per current terminal design')
        value={'class':design['class'],'method':design['method'],'designTestId':design['designTestId'],'actualWholeTestId':actual[0]['testId'],'xmlSha256':actual[0]['xmlSha256']};trace.append(value)
        if(design['class'],design['method'])in new:newtrace.append(value)
    if len(trace)!=6 or{r['designTestId']for r in trace}!={'PT-JMS-TERM'+str(i).zfill(3)for i in range(1,7)}or len(newtrace)!=2 or{r['designTestId']for r in newtrace}!={'PT-JMS-TERM005','PT-JMS-TERM006'}:raise ValueError('all six current and exactly two new terminal design traces')
    return trace,newtrace


def main():
    qp=W/QUALIFIED/'manifest.safe.json';receipt=json.loads(qp.read_bytes());q=receipt['result']
    if not(receipt['actualExit']==0 and q['productionSource']==SOURCE and(q['tests'],q['suites'],q['mainClasses'])==(3973,592,1666)and q['FESFlakyNotRun']==q['staticSixModules']==0):raise ValueError('independently qualified original3973 first')
    data={'source':SOURCE,'serverManifestSha256':q['serverManifestSha256'],'archiveSha256':q['sourceArchiveSha256'],'modules':q['modules']};raw=payload(data);digest=hashlib.sha256(raw.encode()).hexdigest()
    os.umask(0o077);out=W/'pg5892-current3973-projection-v1';out.mkdir(mode=0o700);path=out/'project.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    remote='/home/mini/schubert-nk-pgpt/transfer/PG5892-case-reader-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new artifact reader namespace unavailable; no alternate path')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed reader transfer failed')
    code,text=run('sha256sum '+remote+'/project.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('exact reader payload')
    code,text=run('python3 -B '+remote+'/project.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    if code:raise ValueError('original artifact reader failed, never replay PT for collection')
    cases=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('[')))
    if len(cases)!=3973 or len({r['testId']for r in cases})!=3973 or any(r['result']!='PASS_ORIGINAL_XML'for r in cases):raise ValueError('all actual3973 unique XML cases')
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5890-terminal83-v1/manifest.json'
    if hashlib.sha256(sp.read_bytes()).hexdigest()!='62cd080ef9e88a3c26cf65a6e004e3cdc62541e082d6cc1b4e2a1d6cebc5691a':raise ValueError('current selected design identity proof only, no PASS import')
    selected=json.loads(sp.read_bytes());trace,newtrace=terminal_trace(cases,selected,set(added_cases()));public=base/'PG5886-current3973-cases';public.mkdir();cases_sha=hashlib.sha256((json.dumps(cases,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()
    value={**q,'newCaseTestIdTrace':newtrace,'currentTerminalContractTrace':trace,'casesSha256':cases_sha,'qualificationReceiptSha256':hashlib.sha256(qp.read_bytes()).hexdigest(),'projectionActualExit':code,'projectionPayloadSha256':digest,'selectedDesignManifestSha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'wholeReplayed':False,'newSourceNativeQualified':False,'acceptedLeafDelta':0,'effortPercent':None,'ptAlternativeCompleted':0,'BUG1501ReceiverCoverageScopeVerified':q['coreReceiverTargetFour100'],'globalSpecificationAcceptance':False}
    for name,body in(('cases.json',cases),('qualification.json',value)):
        with(public/name).open('x')as f:json.dump(body,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'tests':3973,'suites':592,'mainClasses':1666,'newCasesTraced':2,'allCurrentTerminalDesignTraces':6,'coreReceiverTargetFour100':q['coreReceiverTargetFour100'],'summarySha256':hashlib.sha256((public/'qualification.json').read_bytes()).hexdigest(),'casesSha256':cases_sha,'formalAccepted':False}))


if __name__=='__main__':main()
