"""Qualify the original whole20 at the changed Test source; never replay the Product run."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg22434-user-audit-cleanup-twenty-unit-v1';META=RUNS/'pg22436-user-audit-cleanup-passive-metadata-v1';OUT=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22438-user-audit-cleanup-independent-v1';SOURCE='ac1919389902fd4d96ec771d9451c4ab224a8556';CORE='7aed8eace7c844c2f79f2e39db766faf914890d5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserCriticalAuditPortTest.java'
def main():
    assert not OUT.exists();m=load(U/'manifest.json');b=m['begin'];assert b==load(U/'begin.json') and b['source']==SOURCE and b['normalSource']==CORE;assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,20,0,0,0)
    for path,h in b['inputHashes'].items():assert sha(R/path)==h==hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=R)).hexdigest()
    for path,h in b['dependencies'].items():assert sha(path)==h
    terminal=load(U/'unit-exit.safe.json');assert terminal==m['stages']['unit'] and terminal['actualExit']==0 and not terminal['timedOut'];cmd=terminal['command'];assert cmd.count('--select-class')==1 and cmd[-1]=='dev.codex.schubert.nk.api.application.admin.UserCriticalAuditPortTest' and '--select-method' not in cmd and '--scan-classpath' not in cmd
    assert b['expectedTests']==20 and b['newMethods']==0 and b['requalifiedExistingMethods']==20 and b['session']=='PG22434-USER-AUDIT-CLEANUP20'
    for label,stage in m['stages'].items():
        assert stage['actualExit']==0 and not stage['timedOut']
        for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
    oldpub=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG19668-user-critical-audit-twenty-v1/manifest.json';assert sha(oldpub)=='ec8a7f2802909a75d0540ff493408eed6762529584bfb3ac2f8cbdbe1eac0472';old=load(oldpub);assert set(m['physical'])==set(old['physicalHashes'])
    for name,h in m['physical'].items():assert sha(U/'component'/(name+'.class'))==h==old['physicalHashes'][name]
    expected=set(re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/TEST).read_text()));assert len(expected)==20;cases=[];environment={}
    for p in sorted((U/'xml').glob('TEST-*.xml')):
        t=E.parse(p).getroot();assert not t.findall('.//failure') and not t.findall('.//error') and not t.findall('.//skipped')
        cases.extend((c.get('classname'),c.get('name')) for c in t.findall('testcase'))
        for x in t.findall('./properties/property'):
            if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']:environment[x.get('name')]=x.get('value')
    assert len(cases)==len(set(cases))==20 and set(cases)=={('dev.codex.schubert.nk.api.application.admin.UserCriticalAuditPortTest',n+'()') for n in expected}
    stdout=(U/'unit.stdout').read_text()
    for s in ['20 tests found','20 tests started','20 tests successful','0 tests aborted','0 tests failed','0 tests skipped','0 containers aborted']:assert s in stdout
    t=E.parse(U/'coverage.xml').getroot();family={c.get('name'):{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in c.findall('counter')} for c in t.findall('.//class')};assert family==old['coverage'];counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in t.findall('counter')};assert all(x['missed']==0 for x in counters.values());assert {k:counters[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=154,METHOD=20,CLASS=5,BRANCH=68)
    ids={name:crc for crc,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert ids==old['physicalClassIds'];ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22434-USER-AUDIT-CLEANUP20"' in ex
    probes={name:[crc,int(hit),int(total)] for crc,hit,total,name in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
    for name,value in old['execMatches'].items():assert probes[name]==value
    rawold=Path(old['originalManifest']['path']);assert sha(rawold)==old['originalManifest']['sha256'];oldlog=rawold.parent/'class-init.log';assert sha(oldlog)==old['classInitializationLogSha256']
    initial=lambda path:re.findall(r"Initializing '([^']+)",path.read_text())
    canonical=lambda name:re.sub(r'\$\$Lambda\+0x[0-9a-f]+','$$Lambda',name)
    product=lambda path:collections.Counter(canonical(n) for n in initial(path) if n.startswith('dev/codex/schubert/nk/') and 'UserCriticalAuditPortTest' not in n)
    assert product(oldlog)==product(U/'class-init.log') and sum(product(U/'class-init.log').values())==160
    init=set(initial(U/'class-init.log'));blocked=['dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec','dev/codex/schubert/nk/web/bootstrap/WebStartupException'];assert not any(n in init for n in blocked);assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','dev/codex/schubert/nk/batch/','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','java/net/Socket')) for n in init)
    met=load(META/'manifest.json');assert met['actualExit']==0 and met['productTestsExecuted']==0;actual={}
    for module in ['api','protocol']:
        for cl in E.parse(META/(module+'-methods.xml')).getroot().findall('.//class'):
            methods=[dict(name=x.get('name'),desc=x.get('desc')) for x in cl.findall('method') if any(c.get('type')=='INSTRUCTION' and int(c.get('covered'))>0 for c in x.findall('counter'))]
            if methods:actual[cl.get('name')]=methods
    assert not any(n in actual for n in blocked);assert not any(x['name'] in ['canonical','apply','fingerprint','verifyAuthentication','decrypt','encrypt'] for methods in actual.values() for x in methods)
    original=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22426-closed-request-original-static-v1';op=load(original/'manifest.json');before=(original/'UserCriticalAuditPortTest.java').read_text();after=(R/TEST).read_text();assert sha(original/'UserCriticalAuditPortTest.java')==op['originalTestSha256'];start=before.index('    var closed = mutation(Mutation.ENABLE);');end=before.index('    assertEquals(f.prepared, f.closes);',start);block=before[start:end];lines=block.splitlines();replacement=lines[0]+'\n    try {\n'+'\n'.join('  '+x for x in lines[1:])+'\n    } finally {\n      closed.close();\n    }\n';assert after==before[:start]+replacement+before[end:]
    stat=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22432-user-audit-cleanup-static-applicability-v1/manifest.json';st=load(stat);assert st['inputHashes']==b['inputHashes'] and st['pmdRaw']==7 and st['applicableViolations']==st['checkstyle']==st['spotbugs']==st['processingErrors']==0 and all(x['classification']=='NOT_APPLICABLE' and x['reason'] for x in st['individualClassifications']);assert sha(st['staticManifest']['path'])==st['staticManifest']['sha256'];assert all(x['rule']!='CloseResource' for x in st['individualClassifications'])
    OUT.mkdir();files={}
    for base,prefix in [(U,'original-'),(META,'passive-')]:
        for p in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
            if p.is_file() and p.name!='jacoco.exec':
                name=prefix+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,OUT/name);files[name]=sha(OUT/name)
    shutil.copyfile(U/'jacoco.exec',OUT/'jacoco.exec');files['jacoco.exec']=sha(OUT/'jacoco.exec')
    for name,value in [('executed-main-methods.json',actual),('product-init-counter.json',dict(product(U/'class-init.log')))]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n');files[name]=sha(OUT/name)
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=SOURCE,productionCoreMain=CORE,tests=20,newUniqueTests=0,requalifiedExistingTests=20,newSourceProofs=0,retainedWholeSources=3,coverage=counters,physicalClassCount=6,codeClassCount=5,physical=m['physical'],classIds=ids,probes={n:probes[n] for n in ids},generatedNoCodeClass='dev/codex/schubert/nk/api/application/admin/UserAuditWriter$1',manualExclusions=[],oldExecCombined=False,productInitClasses=160,executedMainClasses=len(actual),heldFourInitializations=0,allOtherTestBytesAndAssertionsUnchanged=True,finallyRecoveryPresent=True,staticClassification=dict(path=str(stat.relative_to(R)),sha256=sha(stat)),originalRun=dict(path=str(U/'manifest.json'),sha256=sha(U/'manifest.json')),priorQualification=dict(path=str(oldpub.relative_to(R)),sha256=sha(oldpub)),inputHashes=b['inputHashes'],environment=environment,dependencies=b['dependencies'],files=files,bug='BUG-2431',ykt='YKT-2176',newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=20,requalified=20,newUnique=0,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
