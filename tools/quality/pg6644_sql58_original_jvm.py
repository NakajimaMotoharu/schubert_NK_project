"""Bind all58 caught-variable guards to original4158 Jar/debug lines, without executing Main."""
import json
import os
import re
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6638_current115_receivers import read_whole
from pg6586_api_mapper_jvm_join import jvm_calls


def target_owner(text,line,variable):
    source=text.splitlines()[line-1]
    calls=list(re.finditer(r'(?:(\w+)\.)?preserveFatal\('+re.escape(variable)+r'\)',source))
    if len(calls)!=1:raise ValueError('one exact caught-variable source call')
    qualifier=calls[0][1]
    if qualifier is None:
        imports=re.findall(r'^import static ([\w.]+)\.preserveFatal;',text,re.M)
        if len(imports)!=1:raise ValueError('explicit unique static import')
        return imports[0].replace('.','/')
    imports=re.findall(r'^import ([\w.]+\.'+re.escape(qualifier)+r');',text,re.M)
    if len(imports)>1:raise ValueError('unique explicit imported owner')
    if imports:return imports[0].replace('.','/')
    package=re.findall(r'^package ([\w.]+);',text,re.M)
    if len(package)!=1:raise ValueError('one explicit same-package owner')
    return package[0].replace('.','/')+'/'+qualifier


def match_guard(row,text,bytecode):
    expected=target_owner(text,row['guardLine'],row['catchVariable'])
    hits=[r for r in bytecode if r['line']==row['guardLine'] and r['method']=='preserveFatal' and r['owner']==expected]
    keys={(r['physicalClass'],r['member'],r['bci']) for r in hits}
    if not hits or len(keys)!=len(hits):raise ValueError('distinct original JVM paths to the exact source receiver')
    counter=row['aggregateGuardLineCounter']
    if not counter or counter['ci']<=0:raise ValueError('actual original aggregate guard line must execute')
    return dict(siteId=row['siteId'],sourcePath=row['sourcePath'],sourceSha256=row['sourceSha256'],
        catchVariable=row['catchVariable'],guardLine=row['guardLine'],expectedReceiver=expected,
        actualJvmPaths=hits,aggregateGuardLineCounter=counter,perTestFaultCausalityProved=False,accepted=False)


def main():
    version=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-version'],text=True).strip()
    if version!='25.0.4':raise ValueError('pinned disassembler version required')
    qp,q,_=read_whole();sp=BASE/'PG6638-current115-receivers-v1/manifest.json'
    if sha(sp)!='78d3a432941c5b6329d5044dd4cb090c316de278aa2af21277a80f3fbedd3e6f':raise ValueError('qualified115 exact source/whole join')
    sql=json.loads(sp.read_bytes())
    if sql['source']!=q['productionSource'] or sql['currentWholeQualificationSha256']!=sha(qp):raise ValueError('same original source/whole')
    rows=[];cache={};jars={}
    for row in sql['rows']:
        if row['guardLine'] is None:continue
        path=row['sourcePath'];module=path.split('/')[1].removeprefix('schubert-nk-')
        jar=W/'pg6636-original4158-artifacts-v1/jars'/('schubert-nk-'+module+'.jar')
        if sha(jar)!=q['modules'][module]['jarSha256'] or sha(ROOT/path)!=row['sourceSha256']:
            raise ValueError('original Jar and exact current Main bytes')
        jars[module]=sha(jar)
        if path not in cache:
            owner=module+':'+path.split('/src/main/java/')[1][:-5];calls=[]
            for physical in sorted(k for k in q['allPhysicalMainSha256'] if k==owner+'.class' or k.startswith(owner+'$')):
                name=physical.split(':',1)[1][:-6].replace('/','.')
                raw=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-l',name],text=True)
                calls.extend(dict(physicalClass=physical,**c) for c in jvm_calls(raw))
            cache[path]=calls
        rows.append(match_guard(row,(ROOT/path).read_text(),cache[path]))
    if len(rows)!=58 or len({r['siteId'] for r in rows})!=58:raise ValueError('exact58 original classified caught variables')
    value=dict(actualExit=0,source=q['productionSource'],currentWholeQualificationSha256=sha(qp),
        sql115ManifestSha256=sha(sp),guardSites=58,all58AggregateHit=True,rows=rows,jarHashes=jars,
        javapVersion=version,testsExecuted=0,additionalBuildsIssued=0,acceptedSites=0,vmActions=0,
        formalAccepted=False,ptAlternativeCompleted=0,perTestFaultCausalityProved=False,
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        toolSha256=sha(ROOT/'tools/quality/pg6644_sql58_original_jvm.py'),
        command='python3 -B tools/quality/pg6644_sql58_original_jvm.py')
    out=BASE/'PG6644-sql58-original-jvm-v1';os.umask(0o077);out.mkdir()
    target=out/'manifest.json'
    with target.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,guardSites=58,jvmPaths=sum(len(r['actualJvmPaths']) for r in rows),manifestSha256=sha(target))))


if __name__=='__main__':main()
