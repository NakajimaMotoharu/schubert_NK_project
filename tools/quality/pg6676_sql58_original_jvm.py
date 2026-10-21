"""Original4170 disassembly only; no Main/PT rebuild or execution."""
import json
import os
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6644_sql58_original_jvm import match_guard
from pg6586_api_mapper_jvm_join import jvm_calls
from pg6670_original4170_artifacts import read_whole

SQLSHA=None  # Freeze the genuine current115 result before any original-JVM export.


def main():
    version=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-version'],text=True).strip()
    if version!='25.0.4':raise ValueError('pinned original disassembler version')
    qp,q,_=read_whole();sp=BASE/'PG6672-current115-receivers-v1/manifest.json'
    if SQLSHA is None or sha(sp)!=SQLSHA:raise ValueError('freeze qualified current115 manifest first')
    sql=json.loads(sp.read_bytes())
    if sql['source']!=q['productionSource'] or sql['currentWholeQualificationSha256']!=sha(qp):raise ValueError('same original source/whole')
    rows=[];cache={};jars={}
    for row in sql['rows']:
        if row['guardLine'] is None:continue
        path=row['sourcePath'];module=path.split('/')[1].removeprefix('schubert-nk-')
        jar=W/'pg6670-original4170-artifacts-v1/jars'/('schubert-nk-'+module+'.jar')
        if sha(jar)!=q['modules'][module]['jarSha256'] or sha(ROOT/path)!=row['sourceSha256']:raise ValueError('actual original Jar/current Main identity')
        jars[module]=sha(jar)
        if path not in cache:
            owner=module+':'+path.split('/src/main/java/')[1][:-5];calls=[]
            for physical in sorted(k for k in q['allPhysicalMainSha256'] if k==owner+'.class' or k.startswith(owner+'$')):
                name=physical.split(':',1)[1][:-6].replace('/','.')
                raw=subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-classpath',str(jar),'-p','-c','-l',name],text=True)
                calls.extend(dict(physicalClass=physical,**c) for c in jvm_calls(raw))
            cache[path]=calls
        rows.append(match_guard(row,(ROOT/path).read_text(),cache[path]))
    if len(rows)!=58 or len({r['siteId'] for r in rows})!=58:raise ValueError('all58 actual classified caught variables')
    value=dict(actualExit=0,source=q['productionSource'],currentWholeQualificationSha256=sha(qp),
        sql115ManifestSha256=sha(sp),guardSites=58,all58AggregateHit=True,rows=rows,jarHashes=jars,
        javapVersion=version,testsExecuted=0,additionalBuildsIssued=0,acceptedSites=0,vmActions=0,
        formalAccepted=False,ptAlternativeCompleted=0,perTestFaultCausalityProved=False,
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        toolSha256=sha(ROOT/'tools/quality/pg6676_sql58_original_jvm.py'),command='python3 -B tools/quality/pg6676_sql58_original_jvm.py')
    out=BASE/'PG6676-sql58-original-jvm-v1';os.umask(0o077);out.mkdir();target=out/'manifest.json'
    with target.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,guardSites=58,jvmPaths=sum(len(r['actualJvmPaths']) for r in rows),manifestSha256=sha(target))))


if __name__=='__main__':main()
