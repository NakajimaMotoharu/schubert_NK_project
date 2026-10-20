"""Fresh current Main-only pure-catch AST facts;never executes Production/PT/services."""
import datetime
import inspect
import json
import os
import shutil
import subprocess
from collections import Counter
import pg5818_current_reference_facts as input_engine
from pg5940_private_lock_compile import ROOT,W,TC,sha
from pg6010_api15_public import SOURCE,STATIC_SHA
from source_pure_rethrow_inventory_test import facts


def input_source():
    raw=inspect.getsource(input_engine.inputs)
    changes={'PG5810-rollback-static-reauth-v1':'PG6008-api-bounds-static-v1','pg5810-rollback-static-reauth-v1':'pg6008-api-bounds-static-v1',
             "'68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23'":'STATIC_SHA',
             'pg5800-rollback-selected54-v5':'pg6006-api-bounds-selected1021-v1','len(current)!=850':'len(current)!=851','len(physical)!=1665':'len(physical)!=1666'}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one current851/1666 typed-input binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<current Main-only pure-catch input>','exec')
    return raw


def inputs():
    scope={**vars(input_engine),'SOURCE':SOURCE,'STATIC_SHA':STATIC_SHA}
    exec(compile(input_source(),'<fixed current source/class inputs>','exec'),scope)
    return scope['inputs']()


def main():
    snapshot,classpath,identity=inputs();helper=ROOT/'tools/quality/SourcePureRethrowInventory.java';fixture=ROOT/'tools/quality/source_pure_rethrow_inventory_test.py'
    helper_sha=sha(helper);fixture_sha=sha(fixture);os.umask(0o077);out=W/'pg6018-pure-rethrow-facts-v1';out.mkdir(mode=0o700);classes=out/'toolclasses';classes.mkdir()
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH')}
    commands=[['python3','-B','-m','unittest','source_pure_rethrow_inventory_test'],[str(TC/'jdk-25.0.4/bin/javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(helper)]]
    exits=[]
    for i,command in enumerate(commands):
        with(out/('phase-'+str(i)+'.private.log')).open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=60)
        exits.append(r.returncode)
        if r.returncode:raise ValueError('independent pure-catch fixture/helper compile actual0 first')
    mirror=out/'input';mirror.mkdir()
    for name in identity['sourceHashes']:
        target=mirror/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(snapshot/name,target)
    if {p.relative_to(mirror).as_posix():sha(p)for p in mirror.rglob('*.java')}!=identity['sourceHashes']:raise ValueError('all851 immutable Main only;no Test/operational inputs')
    command=[str(TC/'jdk-25.0.4/bin/java'),'-Xmx1536m','-cp',str(classes),'SourcePureRethrowInventory',str(mirror),classpath]
    result=subprocess.run(command,capture_output=True,text=True,env=env,timeout=180)
    with(out/'typed.private.log').open('x')as f:f.write(result.stdout+result.stderr);f.flush();os.fsync(f.fileno())
    if result.returncode:raise ValueError('all current source catch/type symbols must resolve;preserve failure')
    rows=facts(result.stdout)
    if len(rows)!=1094 or any(r['path']not in identity['sourceHashes']for r in rows)or inputs()!=(snapshot,classpath,identity)or sha(helper)!=helper_sha or sha(fixture)!=fixture_sha:
        raise ValueError('same1094 source catches/all851/1666/type/helper inputs immutable')
    flags=Counter(k for r in rows for k in ('pureSingleRethrow','exactUncheckedRoots','laterCatchOverlap','residualTryStable','proposedRemoval')if r[k]=='true')
    value=dict(actualExit=0,source=SOURCE,startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),identity=identity,helperSha256=helper_sha,fixtureSha256=fixture_sha,
               independentFixtureExit=exits[0],compileExit=exits[1],command=command,rows=rows,flagCounts=dict(flags),sourceSymbolsAreNotTestSuccess=True,
               sourceCodeChanged=False,executedProductionPtAdded=0,newDispositionsCreated=0,ptAlternativeCompleted=0,F03Accepted=False,formalAccepted=False,vmActions=0)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=SOURCE,typedCatches=len(rows),flagCounts=dict(flags),manifestSha256=sha(out/'manifest.safe.json'),productionExecuted=False)))


if __name__=='__main__':main()
