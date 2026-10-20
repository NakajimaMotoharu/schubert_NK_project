"""Independent original6014 XML/Jar/allMain/counter reader,never replays PT/runtime operations."""
import inspect
import json
import os
import re
import shlex
import subprocess
from pyflakes.api import check
from lan_server import run,copy
import pg5946_private_lock_qualification as previous
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6014_constants_whole import SOURCE,OLD,SLOT as ORIGINAL,plans
from pg6010_api15_public import STATIC_SHA

# Local pure fixtures supply these; the emitted reader binds them to immutable file data.
EXPECTED_OLD={}
EXPECTED_NEW={}
PHYSICAL_KINDS={}


def physical_difference(old,new,candidate):
    if len(old)!=1666 or set(old)!=set(new) or old!=EXPECTED_OLD or new!=candidate or new!=EXPECTED_NEW or {k for k in old if old[k]!=new[k]}!=set(PHYSICAL_KINDS):
        raise ValueError('all1666 actual old/current/candidate identities and every expected physical difference')
    if any(re.fullmatch('[0-9a-f]{64}',v)is None for mapping in(old,new,candidate)for v in mapping.values()):raise ValueError('actual SHA256 values only')
    return [dict(oldClass=k,**{'class':k},oldSha256=old[k],newSha256=new[k],action='MODIFIED',physicalKind=PHYSICAL_KINDS[k])for k in sorted(PHYSICAL_KINDS)],1666-len(PHYSICAL_KINDS)


def qualifier_source():
    raw=previous.qualifier_source()
    for old,new in (("out = base / 'runs/PG5944-six-v1'","out = base / 'runs/PG6014-six-v1'"),
                    ("source = base / 'source-full-PG5944'","source = base / 'source-full-PG6014'"),
                    ("old = base / 'runs/PG5926-six-v1'","old = base / 'runs/PG5944-six-v1'"),
                    ('transfer/PG5944-source.tar','transfer/PG6014-source.tar')):
        if raw.count(old)!=1:raise ValueError('one exact original/current/prior source-run qualification binding')
        raw=raw.replace(old,new,1)
    return raw


def actual_counters(data,value):
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import xml.etree.ElementTree as ET
    base=Path('/home/mini/schubert-nk-pgpt');out=base/'runs/PG6014-six-v1';source=base/'source-full-PG6014'
    original=json.loads((out/'manifest.safe.json').read_bytes());returned=data['returnedOriginalResult']
    for key in ('actualExit','mavenExit','productionSource','sourceSnapshotHead','run','tests','startUTC','endUTC','logSha256','sourceInputsUnchanged'):
        if original[key]!=returned[key]:raise ValueError('original genuine terminal exactly equals returned original job,not another run')
    end=int(datetime.datetime.fromisoformat(original['endUTC']).timestamp()*1e9)
    start=json.loads((out/'format-before-pt.safe.json').read_bytes())['ptStartEpochNs']
    all_counts={};files={}
    for module in ('protocol','storage','bootstrap','api','web','batch'):
        target=source/('src/schubert-nk-'+module+'/target');path=target/'site/jacoco/jacoco.xml';raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=value['modules'][module]['coverageXmlSha256']:raise ValueError('actual current JaCoCo XML hash remains fixed')
        for artifact in (path,target/'spotbugsXml.xml',target/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')):
            if not start<=artifact.stat().st_mtime_ns<=end:raise ValueError('every actual coverage/static/Jar belongs to original current PT time window')
        files[module]=dict(coverageXmlSha256=hashlib.sha256(raw).hexdigest())
        for node in ET.fromstring(raw).findall('package/class'):
            key=module+':'+node.get('name')+'.class'
            if key in all_counts or key not in data['candidateMain']:raise ValueError('unique current physical Main coverage class only')
            all_counts[key]={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in node.findall('counter')if c.get('type')in('LINE','METHOD','CLASS','BRANCH')}
    targets={key:all_counts.get(key,{})for key in data['changedOuterTargets']}
    if len(targets)!=67 or any(set(c)!={'LINE','METHOD','CLASS','BRANCH'}or any(c[k]['missed']!=0 or c[k]['covered']<=0 for k in c)for c in targets.values()):
        raise ValueError('all67 changed executable outer classes have explicit four nonzero100 counters;no 0/0 or absent inference')
    return dict(allActualClassCounters=all_counts,coveragePhysicalClassKeysNotInXml=sorted(set(data['candidateMain'])-set(all_counts)),changed67Counters=targets,
                changed67ActualFour100=True,actualCounterFiles=files,returnedOriginalTerminalExact=True)


def emitted(data_hash):
    raw='import json,hashlib,pathlib,re\np=pathlib.Path("/home/mini/schubert-nk-pgpt/transfer/PG6016-qualified-v1/input.safe.json")\n'
    raw+='if hashlib.sha256(p.read_bytes()).hexdigest()!='+repr(data_hash)+':raise ValueError("immutable independent input hash")\n'
    raw+='DATA=json.loads(p.read_bytes())\nEXPECTED_OLD=DATA["oldMainClassMap"]\nEXPECTED_NEW=DATA["candidateMain"]\nPHYSICAL_KINDS=DATA["physicalKinds"]\n'
    raw+=inspect.getsource(physical_difference)+'\n'+qualifier_source()+'\n'+inspect.getsource(actual_counters)+'\nvalue=qualify(DATA)\nvalue.update(actual_counters(DATA,value))\nprint(json.dumps(value))\n'
    if check(raw,'<complete independent current3973 qualifier>'):raise ValueError('complete generated independent namespace')
    compile(raw,'<independent current3973 artifacts only>','exec')
    return raw


def main():
    originalp=W/ORIGINAL/'manifest.safe.json';original=json.loads(originalp.read_bytes())
    if not(original['actualExit']==0 and original['source']==SOURCE and original['result']['run']=='PG6014-six-v1'and original['result']['tests']==3973):raise ValueError('original genuine3973 terminal0 first;not completion inferred from begin')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('fixed current Main/Test/settings,not another source')
    oldp=W/'pg5946-private-lock-qualified-v1/manifest.safe.json'
    if sha(oldp)!='80054d8b75bf2003f5e8cc3fbec635cf186a0e9a7cb78a2ba4af1429a7673f6b':raise ValueError('prior independently qualified3973 identity')
    old_wrapper=json.loads(oldp.read_bytes());old=old_wrapper['result']
    if old_wrapper['source']!=OLD or (old['tests'],old['suites'],old['mainClasses'])!=(3973,592,1666):raise ValueError('actual prior baseline/source separated from new current test')
    sp=BASE/'PG6008-api-bounds-static-v1/manifest.json';private=W/'pg6008-api-bounds-static-v1/manifest.safe.json'
    if sha(sp)!=STATIC_SHA or sha(private)!=json.loads(sp.read_bytes())['privateManifestSha256']:raise ValueError('independent current static source/class identity hash')
    candidate=json.loads(private.read_bytes())
    if candidate['source']!=SOURCE or candidate['actualExit']!=0:raise ValueError('actual current8511666 source only')
    before=old['allPhysicalMainSha256'];after=candidate['auxClassHashes'];targets=sorted({r['path'].split('/')[1].removeprefix('schubert-nk-')+':'+r['path'].split('/src/main/java/')[1][:-5]+'.class'for p in plans()for r in p['sourcePlans']})
    changes={k for k in before if before[k]!=after[k]}
    if len(targets)!=67 or not set(targets)<=changes or any(not any(k==key or k.startswith(key[:-6]+'$')for key in targets)for k in changes):raise ValueError('all67 actual outer changes;only declared owner nested/debug differences')
    begin=json.loads((W/ORIGINAL/'begin.safe.json').read_bytes());data=dict(source=SOURCE,priorManifestSha256=old['serverManifestSha256'],priorJarHashes=old['jarHashes'],archiveSha256=begin['archiveSha256'],
         aliases={},newCases=[],declaredNewCases=[],invocationAliases={},candidateMain=after,allMainSourceSha256=candidate['allSourceHashes'],oldMainClassMap=before,
         changedOuterTargets=targets,physicalKinds={k:'SAME_VALUE_PRIVATE_CONSTANT'if k in targets else 'DECLARED_OWNER_DEBUG_EQUIVALENCE_PROVED_IN_STATIC_GROUP'for k in sorted(changes)},returnedOriginalResult=original['result'])
    os.umask(0o077);out=W/'pg6016-constants-qualified-v1';out.mkdir(mode=0o700);data_path=out/'input.safe.json'
    with data_path.open('x')as f:json.dump(data,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    raw=emitted(sha(data_path));path=out/'qualify.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    remote='/home/mini/schubert-nk-pgpt/transfer/PG6016-qualified-v1';status,_=run('mkdir -m700 '+remote,timeout=30)
    if status:raise ValueError('new independent reader namespace unavailable;inspect existing evidence,do not restart PT')
    for local in (data_path,path):
        status,_=copy(local,remote+'/',timeout=60)
        if status:raise ValueError('fixed reader input transfer failed')
    status,text=run('sha256sum '+remote+'/input.safe.json '+remote+'/qualify.private.py',timeout=30)
    if status or sha(data_path)not in text or sha(path)not in text:raise ValueError('exact independent reader/data transfer bytes')
    status,text=run('python3 -B '+shlex.quote(remote+'/qualify.private.py'),timeout=180)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value=dict(actualExit=status,source=SOURCE,payloadSha256=sha(path),inputSha256=sha(data_path),originalReturnedManifestSha256=sha(originalp),wholeReplayed=False,formalAccepted=False,vmActions=0,refusedPtRetried=False,staticPublicManifestSha256=sha(sp))
    if status==0:value['result']=json.loads(next(line for line in reversed(text.splitlines())if line.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if status==0:print(json.dumps({k:value['result'][k]for k in('tests','suites','mainClasses','unchangedPhysicalClasses','FESFlakyNotRun','staticSixModules','changed67ActualFour100','global100')}))
    return status


if __name__=='__main__':raise SystemExit(main())
