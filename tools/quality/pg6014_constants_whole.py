"""One necessary same-source3973 after four constant PG groups;isolated ordinary host fixtures."""
import json
import os
import subprocess
from pyflakes.api import check
import pg5944_private_lock_whole as previous
from pg5780_jms_primary_whole import RUNTIME
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6010_api15_public import SOURCE,STATIC_SHA

OLD='288062f3960a0a50ec82685da3b407f0c9e2934e'
LABEL='PG6014'
SLOT='pg6014-constants-six-v1'
PLANS=(('PG5964-api-sql21-plan-v1','56b461725810f8a706b0c1e9dd092dabf68f631a99593462bc01b7ca9784c2b8'),
       ('PG5974-web-form22-plan-v1','9e6b5dc20ef4a767993b9f21725ab6b66200affc7810504e7d42c8a8cddc136b'),
       ('PG5988-web-contract42-plan-v1','82031f26c9cd398fe674ba00aae48609b4c12ea0d80be481f0455ae76db8df37'),
       ('PG6004-api-bounds18-plan-v1','c10cb0ae8fab810e4a43140218a26c3a332c3a18401cee5d4060367feef972fa'))


def plans():
    values=[]
    for name,digest in PLANS:
        path=BASE/name/'manifest.json'
        if sha(path)!=digest:raise ValueError('all four immutable pre-PG condition declarations')
        values.append(json.loads(path.read_bytes()))
    return values


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5944',LABEL).replace('pg5944','pg6014').replace(previous.SOURCE,SOURCE)
    if check(raw,'<coherent67 source ordinary3973>')or any(s in raw for s in('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume')):
        raise ValueError('complete same approved finite fixture profile;held real runtime actions excluded')
    compile(raw,'<coherent67 source ordinary3973>','exec')
    return raw


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace(previous.SLOT,SLOT).replace('PG5944',LABEL).replace('pg5944','pg6014')
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger='PG-D449..452:four declared same-value constant groups/67Main/103conditions after original qualified source288 whole3973. Current isolated selected module PT,all8511666/source byte/static/null/ABI/debug/executable equivalence first. One necessary full3973/592 verifies current shared dependencies/source;not a replay of old source for confirmation. All Test/oracle/resources/POM unchanged;no VM/current/Root/failed-cohort or old native success import.'
    raw=raw[:start]+"'trigger': "+repr(trigger)+raw[end:]
    compile(raw,'<new-only coherent3973 driver>','exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator/source first')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('canonical Main/Test/config fixed')
    declarations=plans();paths={r['path']for p in declarations for r in p['sourcePlans']}
    if len(paths)!=67 or set(subprocess.check_output(['git','diff','--name-only',OLD,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines())!=paths:
        raise ValueError('exact67 declared Main changes;all3973 Test/oracle/resources unchanged')
    if subprocess.check_output(['git','diff',OLD,SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('same approved build/quality/compatibility gates')
    for p in declarations:
        for r in p['sourcePlans']:
            if sha(ROOT/r['path'])!=r['predictedAfterSha256']:raise ValueError('all67 exact predicted source hashes')
    sp=BASE/'PG6008-api-bounds-static-v1/manifest.json';private=W/'pg6008-api-bounds-static-v1/manifest.safe.json'
    if sha(sp)!=STATIC_SHA:raise ValueError('actual current independent raw1348 first')
    public=json.loads(sp.read_bytes());proof=json.loads(private.read_bytes())
    if sha(private)!=public['privateManifestSha256']or proof['source']!=SOURCE or proof['actualExit']!=0 or len(proof['allSourceHashes'])!=851 or len(proof['auxClassHashes'])!=1666:raise ValueError('actual same-source all8511666 identity')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:raise ValueError('every current851 Main fixed before whole')
    selected=W/'pg6006-api-bounds-selected1021-v1/manifest.safe.json';v=json.loads(selected.read_bytes())
    if not(v['source']==SOURCE and v['actualExit']==v['mavenActualExit']==0 and v['selectedQualified'] and(v['tests'],v['suites'])==(1021,175)and not v['failedOrSkipped']and v['targetFour100']and public['selectedManifestSha256']==sha(selected)):
        raise ValueError('current actual1021/175,15four100 first')
    if not(public['pmdRawFindings']==1348 and public['rawDiagnosticsRemovedByPg']==18 and public['pmdProcessingErrors']==public['checkstyleFindings']==0 and public['all15ExecutableProof']['allMethodDescriptorsAndSymbolicInstructionsEqual']):raise ValueError('all current static/full15 executable equivalence')
    old=W/'pg5946-private-lock-qualified-v1/manifest.safe.json'
    if sha(old)!='80054d8b75bf2003f5e8cc3fbec635cf186a0e9a7cb78a2ba4af1429a7673f6b':raise ValueError('original qualified3973 reference retained,not imported PASS')


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=RUNTIME.preflight();os.umask(0o077)
    with(W/'pg6014-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(RUNTIME.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<one coherent current3973>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
