"""Allowlisted original3955 XML projection after independent qualification; no PT invocation."""
import ast
import hashlib
import inspect
import json
import os
from pyflakes.api import check
from lan_server import run,copy
import pg5790_jms_whole_public as previous
from pg5814_rollback_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,added_cases


def export_source():
    raw=previous.export_source().replace('PG5780','PG5808')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3939:return ast.copy_location(ast.Constant(3955),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def payload(data):
    engine=previous.engine
    raw='from pathlib import Path\nimport hashlib,json,re\nimport xml.etree.ElementTree as ET\n'+inspect.getsource(engine.qualify_snapshot)+'\n'+inspect.getsource(engine.project_xml)+'\n'+export_source()+'\nprint(json.dumps(export('+repr(data)+')))\n'
    if check(raw,'<original3955 allowlist artifact reader>'):raise ValueError('complete namespace0')
    if 'PG5780'in raw or'PG4968'in raw:raise ValueError('only original3955 current artifact paths')
    return raw


def main():
    qp=W/QUALIFIED/'manifest.safe.json';qraw=qp.read_bytes();receipt=json.loads(qraw);q=receipt['result']
    if not(receipt['actualExit']==0 and q['productionSource']==SOURCE and(q['tests'],q['suites'],q['mainClasses'])==(3955,587,1665)and q['FESFlakyNotRun']==q['staticSixModules']==0):raise ValueError('independently qualified original3955 first')
    data={'source':SOURCE,'serverManifestSha256':q['serverManifestSha256'],'archiveSha256':q['sourceArchiveSha256'],'modules':q['modules']};raw=payload(data)
    os.umask(0o077);out=W/'pg5822-current3955-projection-v1';out.mkdir(mode=0o700);path=out/'project.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    remote='/home/mini/schubert-nk-pgpt/transfer/PG5822-case-reader-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new original reader namespace unavailable; no replay/alternate runtime action')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed reader transfer failed')
    code,text=run('sha256sum '+remote+'/project.private.py',timeout=30)
    if code or text.split()[0]!=hashlib.sha256(raw.encode()).hexdigest():raise ValueError('exact reader payload')
    code,text=run('python3 -B '+remote+'/project.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    if code:raise ValueError('original XML reader failed, never replay tests for result collection')
    cases=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('[')))
    if len(cases)!=3955 or len({r['testId']for r in cases})!=3955 or any(r['result']!='PASS_ORIGINAL_XML'for r in cases):raise ValueError('all actual original3955 unique cases')
    sp=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5812-current-rollback54-v1/manifest.json'
    if hashlib.sha256(sp.read_bytes()).hexdigest()!='b822a415878f1794b30f27320bbfc1353afd6b7aaa8b07dd7fed25bb5402b797':raise ValueError('same-source selected design identities, never PASS import')
    selected=json.loads(sp.read_bytes());trace=[]
    for cls,method in added_cases():
        labels={hashlib.sha256(s.encode()).hexdigest()for s in(method,method+'()')};matches=[r for r in cases if r['class']==cls and r['caseNameSha256']in labels];design=[r['designTestId']for r in selected['caseTrace']if r['class']==cls and r['method']==method and r['designTestId']]
        if len(matches)!=1 or len(design)!=1:raise ValueError('one original full case and one independent design identity per new method')
        trace.append({'class':cls,'method':method,'designTestId':design[0],'actualWholeTestId':matches[0]['testId'],'xmlSha256':matches[0]['xmlSha256']})
    if len(trace)!=16 or len({r['designTestId']for r in trace})!=16:raise ValueError('exact16 new design contracts')
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5808-current3955-cases';public.mkdir()
    cases_sha=hashlib.sha256((json.dumps(cases,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()
    value={**q,'newCaseTestIdTrace':trace,'casesSha256':cases_sha,'qualificationReceiptSha256':hashlib.sha256(qraw).hexdigest(),'projectionActualExit':code,'projectionPayloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'wholeReplayed':False,'newSourceNativeQualified':False,'acceptedLeafDelta':0,'effortPercent':None,'ptAlternativeCompleted':0,'BUG1494Open':True,'wholePassIsNotSpecificationAcceptance':True}
    for name,body in(('cases.json',cases),('qualification.json',value)):
        with(public/name).open('x')as f:json.dump(body,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'tests':3955,'suites':587,'mainClasses':1665,'newCasesTraced':16,'coreReceiverTargetFour100':q['coreReceiverTargetFour100'],'summarySha256':hashlib.sha256((public/'qualification.json').read_bytes()).hexdigest(),'casesSha256':hashlib.sha256((public/'cases.json').read_bytes()).hexdigest(),'BUG1494Open':True,'formalAccepted':False}))


if __name__=='__main__':main()
