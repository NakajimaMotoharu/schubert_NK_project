"""Read original API Jar from a rejected static run; never grants PT/whole qualification."""
import json
import os
import subprocess
import zipfile
import hashlib
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6148_api_jms_close_order import close_proofs
from pg6158_api_factory_close_order import configuration, broker_preparation, PROVIDER, BROKER
from pg6056_expiry_read_methods import methods

SOURCE='8f0ba4cb06467e5e1c9b25f8360bbc1db4d963ea'


def main():
    run=W/'pg6154-api-factory-close-selected-v2';mp=run/'manifest.safe.json'
    if sha(mp)!='a4fdb91aa532b488f58802039922d2a95bfce5ae06a83d40a7c46ff3836a7f2a':raise ValueError('original rejected run immutable')
    m=json.loads(mp.read_bytes())
    if (m['source']!=SOURCE or m['actualExit']!=1 or m['mavenActualExit']!=1 or m['phaseExits']!=[0,1]
        or m['tests']!=1034 or m['suites']!=175 or m['failedOrSkipped'] or m['staticIssues']!={'protocol':0,'storage':0,'bootstrap':0,'api':4}
        or not m['sourceFixed'] or not m['targetFour100']):raise ValueError('only original rejected1034 run for diagnostics,not qualification')
    snapshot=run/'source'
    actual=list(ROOT.glob('src/*/src/main/java/**/*.java'))
    if len(actual)!=851 or any(sha(p)!=sha(snapshot/p.relative_to(ROOT)) for p in actual):raise ValueError('same original Main source before any new implementation')
    report=snapshot/'src/schubert-nk-api/target/site/jacoco/jacoco.xml'
    if sha(report)!=m['coverage']['api']['sha256']:raise ValueError('actual original API coverage only')
    oldpub=BASE/'PG6132-api-management-stop-qualification-v1/manifest.json'
    if sha(oldpub)!='a3f833f1b349e7d701e1f4e4abd790ce166794e5479a2c88eb39830dcb38488d':raise ValueError('immutable old Jar proof')
    oldpath=W/'pg6132-api-management-stop-qualification-v1/manifest.safe.json'
    if sha(oldpath)!=json.loads(oldpub.read_bytes())['privateManifestSha256']:raise ValueError('original old class inventory')
    old=json.loads(oldpath.read_bytes())
    jars=[W/(n+'/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar') for n in ('pg6130-api-management-stop-green-v1','pg6154-api-factory-close-selected-v2')]
    for jar,record in zip(jars,(old,m)):
        with zipfile.ZipFile(jar) as z:members={'api:'+n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
        expected={k:v for k,v in record['allPhysicalMainSha256'].items() if k.startswith('api:')}
        if not members or members!=expected:raise ValueError('all actual original API Jar bytes must match saved compiled map')
    def read(cls):return methods(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jars[1]),cls],text=True))
    value=dict(actualExit=0,purpose='PG_DIAGNOSTIC_ONLY_PARENT_RUN_REJECTED',source=SOURCE,
        originalRunExit=1,originalStaticApiFindings=4,originalManifestSha256=sha(mp),all851MainUnchanged=True,
        originalApiJarSha256=sha(jars[1]),closeOrder=close_proofs(jars),providerConfiguration=configuration(read(PROVIDER)),
        brokerPreparation=broker_preparation(read(BROKER)),originalEightTargetCounters=m['targetCounters'],
        testsExecutedByReader=0,additionalBuilds=0,wholeQualified=False,sixModuleStaticAccepted=False,
        formalAccepted=False,nativeQualified=False,ptAlternativeCompleted=0)
    os.umask(0o077);out=BASE/'PG6159-api-original-jvm-diagnostic-v1';out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,purpose=value['purpose'],source=SOURCE,originalRunExit=1,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
