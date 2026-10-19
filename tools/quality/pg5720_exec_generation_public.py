"""Publish only allowlisted original3908 case identities; no test rerun or runtime access."""
import ast
import hashlib
import inspect
import json
import os
from pyflakes.api import check
from lan_server import run,copy
import pg5058_whole_case_projection as engine
import pg5576_monitor_whole_public as prior
from pg5718_exec_generation_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,ADDED

SLOT='PG5716-current3908-cases'


def main():
    qpath=W/QUALIFIED/'manifest.safe.json';qraw=qpath.read_bytes();receipt=json.loads(qraw);q=receipt['result']
    if not(receipt['actualExit']==0 and q['productionSource']==SOURCE and(q['tests'],q['suites'],q['mainClasses'])==(3908,563,1664)and q['FESFlakyNotRun']==q['staticSixModules']==0):raise ValueError('original independently qualified3908 first')
    data={'source':SOURCE,'serverManifestSha256':q['serverManifestSha256'],'archiveSha256':q['sourceArchiveSha256'],'modules':q['modules']}
    raw=prior.export_source().replace('PG5588','PG5716')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3905:return ast.copy_location(ast.Constant(3908),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    script='from pathlib import Path\nimport hashlib,json,re\nimport xml.etree.ElementTree as ET\n'+inspect.getsource(engine.qualify_snapshot)+'\n'+inspect.getsource(engine.project_xml)+'\n'+raw+'\nprint(json.dumps(export('+repr(data)+')))\n'
    if check(script,'<allowlisted original3908 XML reader>'):raise ValueError('all standalone static0')
    os.umask(0o077);out=W/'pg5720-current-case-projection-v1';out.mkdir(mode=0o700);path=out/'project.private.py'
    with path.open('x')as f:f.write(script);f.flush();os.fsync(f.fileno())
    remote='/home/mini/schubert-nk-pgpt/transfer/PG5720-case-reader-v1'
    code,_=run('mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new result-reader output refused; no alternate path')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed result reader transfer refused')
    code,text=run('sha256sum '+remote+'/project.private.py',timeout=30)
    if code or text.split()[0]!=hashlib.sha256(script.encode()).hexdigest():raise ValueError('exact allowlisted reader bytes')
    code,text=run('python3 -B '+remote+'/project.private.py',timeout=180)
    with(out/'original-projection.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    if code:raise ValueError('original projection not successful; preserve, do not repeat tests')
    cases=json.loads(next(line for line in reversed(text.splitlines())if line.startswith('[')))
    if len(cases)!=3908 or len({r['testId']for r in cases})!=3908 or any(r['result']!='PASS_ORIGINAL_XML'for r in cases):raise ValueError('all3908 original successful identities')
    trace=[]
    for cls,method in sorted(ADDED):
        hashes={hashlib.sha256(s.encode()).hexdigest()for s in(method,method+'()')}
        match=[r for r in cases if r['class']==cls and r['caseNameSha256']in hashes]
        if len(match)!=1:raise ValueError('one actual source-declared new TestID')
        ident='PT-OPS-EXECGEN'+method[len('execgen'):len('execgen')+6]
        trace.append({'class':cls,'method':method,'designTestId':ident,'actualWholeTestId':match[0]['testId'],'xmlSha256':match[0]['xmlSha256']})
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/SLOT;public.mkdir()
    summary={**q,'newCaseTestIdTrace':trace,'qualificationReceiptSha256':hashlib.sha256(qraw).hexdigest(),'wholeReplayed':False,'newSourceNativeQualified':False,'acceptedLeafDelta':0,'effortPercent':None,'ptAlternativeCompleted':0}
    for name,value in(('cases.json',cases),('qualification.json',summary)):
        with(public/name).open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'tests':3908,'suites':563,'mainClasses':1664,'newDesignTestIds':trace,'summarySha256':hashlib.sha256((public/'qualification.json').read_bytes()).hexdigest(),'casesSha256':hashlib.sha256((public/'cases.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
