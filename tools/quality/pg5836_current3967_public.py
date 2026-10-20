"""Project original3967 XML only after independent qualification; never reissue tests."""
import ast
import hashlib
import json
import os
import pg5822_current3955_public as previous
from pg5834_isolation_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,added_cases


def payload(data):
    raw=previous.payload(data).replace('PG5808','PG5832')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3955:return ast.copy_location(ast.Constant(3967),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if previous.check(raw,'<original3967 case allowlist reader>'):raise ValueError('all reader namespace0')
    if 'PG5808'in raw or'Popen'in raw:raise ValueError('current artifacts only, no new PT')
    return raw


def main():
    qp=W/QUALIFIED/'manifest.safe.json';receipt=json.loads(qp.read_bytes());q=receipt['result']
    if not(receipt['actualExit']==0 and q['productionSource']==SOURCE and(q['tests'],q['suites'],q['mainClasses'])==(3967,590,1666)and q['FESFlakyNotRun']==q['staticSixModules']==0):raise ValueError('independently qualified original3967 first')
    data={'source':SOURCE,'serverManifestSha256':q['serverManifestSha256'],'archiveSha256':q['sourceArchiveSha256'],'modules':q['modules']};raw=payload(data);digest=hashlib.sha256(raw.encode()).hexdigest()
    os.umask(0o077);out=W/'pg5836-current3967-projection-v1';out.mkdir(mode=0o700);path=out/'project.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    remote='/home/mini/schubert-nk-pgpt/transfer/PG5836-case-reader-v1'
    code,_=previous.run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new original reader namespace unavailable; no alternate operation')
    code,_=previous.copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed reader transfer failed')
    code,text=previous.run('sha256sum '+remote+'/project.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('exact original XML reader')
    code,text=previous.run('python3 -B '+remote+'/project.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    if code:raise ValueError('original artifact reader failed; never replay tests for collection')
    cases=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('[')))
    if len(cases)!=3967 or len({r['testId']for r in cases})!=3967 or any(r['result']!='PASS_ORIGINAL_XML'for r in cases):raise ValueError('all actual3967 unique cases')
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5831-isolation66-v1/manifest.json'
    if hashlib.sha256(sp.read_bytes()).hexdigest()!='c6244a36c37c2101c0625c911b35cc94f196b490186414ff034ffcc3d21a4057':raise ValueError('current original66 design identities only, not PASS import')
    selected=json.loads(sp.read_bytes());trace=[]
    for cls,method in added_cases():
        labels={hashlib.sha256(s.encode()).hexdigest()for s in(method,method+'()')};actual=[r for r in cases if r['class']==cls and r['caseNameSha256']in labels];design=[r['designTestId']for r in selected['caseTrace']if r['class']==cls and r['method']==method]
        if len(actual)!=1 or len(design)!=1:raise ValueError('one actual full XML and one independent design ID')
        trace.append({'class':cls,'method':method,'designTestId':design[0],'actualWholeTestId':actual[0]['testId'],'xmlSha256':actual[0]['xmlSha256']})
    if len(trace)!=12 or {r['designTestId']for r in trace}!={'PT-JMS-ISO'+str(i).zfill(3)for i in range(1,13)}:raise ValueError('all twelve new design contracts')
    red=base/'PG5827-isolation-reds-v1/manifest.json'
    if hashlib.sha256(red.read_bytes()).hexdigest()!='f3de8b29bd903ed6d0e007e2bc43f8409a2670fd0e11905db76e7d9a0497a265':raise ValueError('all eight original policy reds first')
    public=base/'PG5832-current3967-cases';public.mkdir();cases_sha=hashlib.sha256((json.dumps(cases,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()
    value={**q,'newCaseTestIdTrace':trace,'casesSha256':cases_sha,'qualificationReceiptSha256':hashlib.sha256(qp.read_bytes()).hexdigest(),'projectionActualExit':code,'projectionPayloadSha256':digest,'selectedDesignManifestSha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'independentRedManifestSha256':hashlib.sha256(red.read_bytes()).hexdigest(),'wholeReplayed':False,'newSourceNativeQualified':False,'acceptedLeafDelta':0,'effortPercent':None,'ptAlternativeCompleted':0,'BUG1494LimitedPolicyScopeVerified':q['coreReceiverTargetFour100'],'globalSpecificationAcceptance':False}
    for name,body in(('cases.json',cases),('qualification.json',value)):
        with(public/name).open('x')as f:json.dump(body,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'tests':3967,'suites':590,'mainClasses':1666,'newCasesTraced':12,'coreReceiverTargetFour100':q['coreReceiverTargetFour100'],'summarySha256':hashlib.sha256((public/'qualification.json').read_bytes()).hexdigest(),'casesSha256':cases_sha,'formalAccepted':False}))


if __name__=='__main__':main()
