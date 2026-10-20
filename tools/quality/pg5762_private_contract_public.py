"""Publish allowlisted original3932 case identities; no PT replay or runtime operation."""
import ast
import hashlib
import inspect
import json
import os
from pyflakes.api import check
from lan_server import run,copy
import pg5058_whole_case_projection as engine
from pg5756_private_contract_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,added_cases

SLOT='PG5754-current3932-cases'


def export_source():
    raw=inspect.getsource(engine.export).replace('PG4968','PG5754')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3791:return ast.copy_location(ast.Constant(3932),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    qpath=W/QUALIFIED/'manifest.safe.json';qraw=qpath.read_bytes();receipt=json.loads(qraw);q=receipt['result']
    if not(receipt['actualExit']==0 and q['productionSource']==SOURCE and(q['tests'],q['suites'],q['mainClasses'])==(3932,581,1664)and q['FESFlakyNotRun']==q['staticSixModules']==0 and q['changedTargetFour100']):raise ValueError('original independently qualified3932/54target four100 first')
    data={'source':SOURCE,'serverManifestSha256':q['serverManifestSha256'],'archiveSha256':q['sourceArchiveSha256'],'modules':q['modules']}
    raw='from pathlib import Path\nimport hashlib,json,re\nimport xml.etree.ElementTree as ET\n'+inspect.getsource(engine.qualify_snapshot)+'\n'+inspect.getsource(engine.project_xml)+'\n'+export_source()+'\nprint(json.dumps(export('+repr(data)+')))\n'
    if check(raw,'<original3932 XML allowlist>'):raise ValueError('standalone reader static names0')
    os.umask(0o077);out=W/'pg5762-current-case-projection-v1';out.mkdir(mode=0o700);path=out/'project.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    remote='/home/mini/schubert-nk-pgpt/transfer/PG5762-case-reader-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only reader namespace refused; no alternate path')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed reader transfer refused')
    code,text=run('sha256sum '+remote+'/project.private.py',timeout=30)
    if code or text.split()[0]!=hashlib.sha256(raw.encode()).hexdigest():raise ValueError('exact actual reader bytes')
    code,text=run('python3 -B '+remote+'/project.private.py',timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    if code:raise ValueError('original case projection failed; do not repeat tests')
    cases=json.loads(next(s for s in reversed(text.splitlines())if s.startswith('[')))
    if len(cases)!=3932 or len({r['testId']for r in cases})!=3932 or any(r['result']!='PASS_ORIGINAL_XML'for r in cases):raise ValueError('all actual3932 unique original successful identities')
    trace=[]
    for cls,method in added_cases():
        hashes={hashlib.sha256(s.encode()).hexdigest()for s in(method,method+'()')};match=[r for r in cases if r['class']==cls and r['caseNameSha256']in hashes]
        if len(match)!=1:raise ValueError('one original actual XML case for each declared addition')
        trace.append({'class':cls,'method':method,'actualWholeTestId':match[0]['testId'],'xmlSha256':match[0]['xmlSha256']})
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT;public.mkdir()
    summary={**q,'newCaseTestIdTrace':trace,'qualificationReceiptSha256':hashlib.sha256(qraw).hexdigest(),'projectionActualExit':code,'projectionPayloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'wholeReplayed':False,'newSourceNativeQualified':False,'acceptedLeafDelta':0,'effortPercent':None,'ptAlternativeCompleted':0}
    for name,value in(('cases.json',cases),('qualification.json',summary)):
        with(public/name).open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'tests':3932,'suites':581,'mainClasses':1664,'newCasesTraced':len(trace),'targetClassesFour100':len(q['changedTargetCounters']),'summarySha256':hashlib.sha256((public/'qualification.json').read_bytes()).hexdigest(),'casesSha256':hashlib.sha256((public/'cases.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
