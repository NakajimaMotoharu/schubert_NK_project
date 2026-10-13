"""Read-only full current post plus exact failed-preparation pair, no signal authority."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,SSH
import pg1257_fresh_independent_terminal_post as seal_schema
from pg2280_current_signed_owned_post import payload as current_post
from pg1991_fresh_runtime_partial_full_proof import helpers as old_helpers
from pg2304_current_completed_resume_sources import TOOLS,SAVE,SOURCE

SLOT='pg2309-current-resume-pair-proof-v1'
PID=96640
TICKS=1550071
CHILD=96671
CHILD_TICKS=1550259
BACKEND=96669


def bound(raw):
    for old,new in [('498727',str(PID)),('10276205',str(TICKS)),('498725','96638'),('498758',str(CHILD)),('10276392',str(CHILD_TICKS)),('498756',str(BACKEND)),('pg1980-fresh-resume-tools-v1',TOOLS),('pg1980_native_refs.py','pg2304_native_refs.py'),('pg1984-fresh-resume-preparation-v1',SAVE)]:raw=raw.replace(old,new)
    return raw


def body():
    post=json.loads((W/'pg2281-current-signed-owned-post-v2/manifest.safe.json').read_bytes())
    frozen=json.loads((W/'pg2275-frozen-v1.safe.json').read_bytes())
    seals={n:post['proofHashes'][n]['sha256']for n in seal_schema.previous.SEALS}
    raw=current_post(seals)
    raw=raw[:raw.index("result = {'actualExit': 0")]
    raw=raw.replace("lines[-2:] == [b'0', b'0']","lines[-2:] == ([b'0', b'0']if PEER_CLOSED else[b'1', b'1'])")
    start=raw.index("        for name in ('maintenance.lock', 'startup-admission.lock'):")
    end=raw.index("        require(tree(pathlib.Path('/run/systemd/system'))",start)
    raw=raw[:start]+"        if not PEER_CLOSED:\n            for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n"+raw[end:]
    helper=bound(old_helpers()).replace('require(children == {96671})','require(children == (set()if REF_CLOSED else{96671}))')
    marker='\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker)!=1:raise ValueError('one whole metadata reference scope required')
    raw=raw.replace(marker,'\n'+helper+'\n'+marker)
    cp='/var/lib/pgpt-s1-preservation/'+TOOLS+':/opt/schubert-nk/releases/0.1.0-PG2126/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG2126/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG2126/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG2126/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg2304FreshResumePreparation','prepare-resume']
    receipt=(W/'pg2274-current-signed-owned-stop-tools-v1/pg2274_parent_receipt.py').read_text()
    names=['Pg2274NativeStop.class','Pg2274NativeStop$References.class','pg2274_native_refs.py','pg2274_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg2274_parent_receipt.py','pg2274_durable.py','pg2274_configuration.py','pg2274_configuration_capture.py','pg2274_row_bound.py','pg2274_stable_journal.py']
    header='PEER_CLOSED=False\nREF_CLOSED=False\nEXPECTED_ARGV='+repr(b'\0'.join(x.encode()for x in argv)+b'\0')+'\nHASHES='+repr({n:frozen['fileHashes'][n]for n in names})+'\nRECEIPT='+repr(receipt)+'\n'
    return header+raw


TAIL=r'''
failed=base/'pg2308-current-completed-resume-preparation-v1'
require({p.name for p in failed.iterdir()}=={'refs-prepare.private.log'})
require(hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest()=='09640d25fa96fd2599a0a3e3e52bbb20331501bf245c51a762dab611d3a8ac5a')
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').exists())
tool=base/'pg2304-current-completed-resume-tools-v1'
for name,digest in TOOL_HASHES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'pg2309-current-resume-pair-proof-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'native':native,'toolHashes':TOOL_HASHES,'candidateNotPlaced':True,'runtimeDirectoryAbsent':True,'runtimeWriteReload0':True,'all24And32And187Unchanged':True,'onlyOwnedPeerAndAdvisory':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':96640,'childPid':96671,'backendPid':96669,'parentFdCount':101,'childFdCount':4,'samePeer':True,'ownedLocks':2,'allOriginalValuesPreserved':True,'signals0':True,'formalAccepted':False}))
'''


def payload():
    frozen=json.loads((W/'pg2305-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE:raise ValueError('current sameSource full ABI required')
    raw='TOOL_HASHES='+repr(frozen['fileHashes'])+'\n'+body()+TAIL
    if check(raw,'<whole current preparation pair readonly>'):raise ValueError('all current proof globals required')
    compile(raw,'<current pair full proof>','exec')
    return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload()
    (out/'payload.private.py').write_text(raw)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(result.stderr)
    value={'actualExit':result.returncode,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'signals0':True,'formalAccepted':False}
    if not result.returncode:value['guest']=json.loads(result.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
