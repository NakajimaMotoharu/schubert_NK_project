"""Qualified native27 + one successful isolated negative cohort, same a9/3694.

451/SS355/PT-OPS-LFACT-CRC001. No VM operation or new build/sign/deploy.
All failed and prior unqualified fixture streams are excluded, not normalized.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pyflakes.api import check
from lan_server import run, copy
from pg1446_current_cold_stage import W
import pg3208_expiry_group_native_rejoin as previous

OUT = W / 'pg3234-legacy-negative-native-v1'
TRANSFER = '/home/mini/schubert-nk-pgpt/transfer/PG3234-negative-native-v1'

CAPSULE = r'''
import tarfile
transfer=Path(TRANSFER);archive=transfer/'capsule.private.tar';require(sha(archive)==CAPSULE_SHA)
with tarfile.open(archive,'r:')as tar:
 members=tar.getmembers();require(len({m.name for m in members})==len(members)and all(m.isfile()and not Path(m.name).is_absolute()and '..'not in Path(m.name).parts for m in members))
 capsule=json.loads(tar.extractfile('capsule.safe.json').read());require(capsule['actualExit']==0 and capsule['source']==SOURCE and capsule['boot']=='dd710ec8-bfdf-4157-b445-8073895110d2'and capsule['oldFailedNativeImported']is False)
 require({m.name for m in members}==set(capsule['files'])|{'capsule.safe.json'})
 material={n:tar.extractfile(n).read()for n in capsule['files']}
 for n,digest in capsule['files'].items():require(hashlib.sha256(material[n]).hexdigest()==digest)
 require(capsule['inputSha256']==INPUT_SHA)
 meta=json.loads(material['runtime-input.safe.json']);require(meta['loadedMainSource']==SOURCE and meta['allMainSameBytes']==1643 and meta['allResourceMetaSameBytes']==79 and meta['hostTests']==3694 and meta['sourceSnapshot']==full['sourceSnapshot'])
 for m in modules:require(meta['files']['jars/schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar']['sha256']==full['jarHashes'][m])
 require(meta['runtimeClasspath'][:7]==['classes']+['jars/schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'for m in modules])
 whole=json.loads(material['manifest.safe.json']);post=json.loads(material['post.safe.json'])
 require(whole['actualExit']==post['actualExit']==0 and whole['cases']==post['cases']==7 and whole['source']==post['source']==SOURCE and whole['boot']==post['boot']==capsule['boot']and whole['naturalUnitExit']==0 and whole['privateSystemctlExecVerified']and whole['publicBusScopeLimited'])
 require(whole['syscallSha256']==hashlib.sha256(material['syscall.private.log']).hexdigest())
 require(all(post[k]is True for k in ['all24AndHistoryTwiceUnchanged','allTenUnitKernelEmpty','clientAdvisoryLockZero','protectedTreeUnchanged','oneFixtureStartAndOwnedStopOnly']))
 for i in range(1,8):
  tid='PT-OPS-LFACT'+str(i).zfill(3);v=json.loads(material['observer/'+tid+'.safe.json']);a=json.loads(material['case/'+tid+'.safe.json'])
  require(v['testId']==a['testId']==tid and v['actualExit']==0 and a['status']=='PASS'and a['source']==SOURCE and v['approvalAccessObserved']and v['actualPublicNativeReadConnects']>0 and v['privateManagerConnects']==0 and v['unsafeSystemctlExecs']==0 and v['inetConnects']==0)
 native=transfer/'native.exec'
 with native.open('xb')as f:f.write(material['native.exec']);f.flush();os.fsync(f.fileno())
 require(sha(native)==whole['nativeSha256']==post['nativeSha256'])
r=subprocess.run([str(J/'java'),'-cp',cp,'NativeSessions571',str(capsule['nativeLowerMs']),str(capsule['nativeUpperMs']),str(native)],capture_output=True,timeout=30)
require(r.returncode==0 and not r.stderr);negative_sessions=[json.loads(line)for line in r.stdout.splitlines()]
require(len(negative_sessions)==1 and negative_sessions[0]['sessions']==1 and negative_sessions[0]['sessionIdSha256']==capsule['expectedSessionIdSha256']==hashlib.sha256(b'PG3236-LFACT-v5').hexdigest())
sessions.extend(negative_sessions);streams.append(native)
require(len(streams)==28 and len(sessions)==28 and len({s['sessionIdSha256']for s in sessions})==28)
'''


def build(raw, capsule_sha, input_sha):
    for value in [capsule_sha, input_sha]:
        if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value): raise ValueError('fixed actual capsule/runtime SHA required')
    marker = "require(len(sessions)==27 and len({s['sessionIdSha256']for s in sessions})==27)"
    if raw.count(marker) != 1: raise ValueError('one exact 27 qualified session boundary required')
    raw = raw.replace(marker, marker + '\n' + CAPSULE).replace('PG3208', 'PG3234')
    raw = raw.replace("'qualifiedNativeStreams':27,'distinctSessions':27", "'qualifiedNativeStreams':28,'distinctSessions':28,'qualifiedNegativeFixtureCohorts':1,'qualifiedNegativeFixtureStreams':1,'negativeWholePassedCases':7")
    if "'qualifiedNativeStreams':28" not in raw: raise ValueError('whole native provenance cardinality required')
    raw = 'TRANSFER=' + repr(TRANSFER) + '\nCAPSULE_SHA=' + repr(capsule_sha) + '\nINPUT_SHA=' + repr(input_sha) + '\n' + raw
    if check(raw, '<whole exact native27 plus one qualified negative fixture>'): raise ValueError('complete join namespace required')
    compile(raw, '<same a9 28 unique native streams>', 'exec')
    return raw


def main():
    os.umask(0o077)
    proof = json.loads((W / 'pg3238-legacy-negative-post-v1/manifest.safe.json').read_bytes())
    compiled = json.loads((W / 'pg3214-legacy-fixture-compile-v1/manifest.safe.json').read_bytes())
    if proof['actualExit'] != 0 or compiled['actualExit'] != 0: raise ValueError('actual independent post and exact compiled runtime required')
    archive = W / 'pg3238-legacy-negative-post-v1/capsule.private.tar'
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != proof['capsuleSha256']: raise ValueError('fixed successful capsule required')
    raw = build(previous.payload(), digest, compiled['inputSha256'])
    OUT.mkdir(mode=0o700); (OUT / 'command.private.py').write_text(raw)
    code, status = run("python3 -B - <<'PREP'\nfrom pathlib import Path\np=Path(" + repr(TRANSFER) + ");assert not p.exists();p.mkdir(mode=0o700)\nPREP", timeout=20)
    if code: raise ValueError('new-only current capsule receiver refused')
    code, status = copy(str(archive), TRANSFER + '/', timeout=30)
    if code: raise ValueError('same-user current capsule transfer refused')
    code, status = run("python3 -B - <<'QUALIFY'\n" + raw + '\nQUALIFY', timeout=240)
    (OUT / 'observer.private.log').write_text(status)
    value = {'actualExit': code, 'productionSource': previous.SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if code == 0: value.update(json.loads(next(line for line in status.splitlines() if line.startswith('{'))))
    (OUT / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    safe = {'actualExit': code, 'formalAccepted': False}
    if code == 0: safe.update(streams=28, currentNegativeCases=7, classByteMismatch=0, mainClasses=1643, remaining={k: sum(m[k]['missed'] for m in value['result']['moduleCounters'].values()) for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']}, manifestSha256=value['manifestSha256'])
    print(json.dumps(safe)); return code


if __name__ == '__main__':
    raise SystemExit(main())
