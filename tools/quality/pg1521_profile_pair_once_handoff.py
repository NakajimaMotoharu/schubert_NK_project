"""Exact proved failed readonly profile Ref then Java once TERM, bounded separate reap."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
import pg1520_profile_retained_pair_proof as proof
from pg1499_retained_pair_owned_handoff import EXTRA

SLOT='pg1521-retained-profile-pair-handoff-v1'
PROOF_SHA='5b77c687329103ed1ef210c6ba69db033801ed7310b2774ff591fd1ec727cd51'

def payload():
 raw=proof.payload();marker='first=snapshot();require(first==snapshot());validate_current(first);a=pair();'
 start=raw.index(marker);prefix=raw[:start]
 marker0='require(not os.path.lexists(PAIR_SAVE))';assert prefix.count(marker0)==1
 prefix=prefix.replace(marker0,'require(os.path.isdir(PAIR_SAVE))')
 body=EXTRA
 for a,b in [('pg1499-retained-publication-pair-handoff-v1',SLOT),('pg1498-retained-publication-pair-proof-v1',proof.SLOT),('b76ba20d9c058cbf07f37f47356ba472bc33270d6bfdac9a804a64584923efba',PROOF_SHA),('92297',str(proof.PID)),('1431673',str(proof.TICKS)),('92323',str(proof.CHILD)),('PG266-publication-recover','PG269-original-io-profile')]:body=body.replace(a,b)
 marker='contract.terminate_once('+str(proof.CHILD)+',CHILD_TICKS,before_child,reserve,os.pidfd_open,send,wait,os.close)\nparent_after_child()'
 assert marker in body
 reap='''def wait_reaped(pid,ticks):
 deadline=time.monotonic()+30
 while pathlib.Path('/proc',str(pid)).exists():
  p=pathlib.Path('/proc',str(pid),'stat')
  try:require(int(p.read_text().rpartition(')')[2].split()[19])==ticks)
  except FileNotFoundError:break
  require(time.monotonic()<deadline);time.sleep(.05)
'''
 body=body.replace(marker,reap+marker.replace('\nparent_after_child()','\nwait_reaped('+str(proof.CHILD)+',CHILD_TICKS)\nparent_after_child()'))
 marker='contract.terminate_once('+str(proof.PID)+','+str(proof.TICKS)+',parent_after_child,reserve,os.pidfd_open,send,wait,os.close)'
 assert marker in body;body=body.replace(marker,marker+'\nwait_reaped('+str(proof.PID)+','+str(proof.TICKS)+')')
 return prefix+body

def main():
 os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
 saved=(W/proof.SLOT/'payload.private.py').read_text();nodes=[n for n in ast.parse(saved).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'EXPECTED_ARGS','FROZEN_HASHES','CHILD_TICKS'}for t in n.targets)];assert len(nodes)==3
 raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+payload();compile(raw,'<fixed once profile pair handoff>','exec')
 (out/'payload.private.py').write_text(raw)
 r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=180)
 (out/'stderr.private.log').write_bytes(r.stderr)
 v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'oldNormalCloseUnknown':True,'serviceStops0':True,'formalAccepted':False}
 if r.returncode==0:v['guest']=json.loads(r.stdout)
 with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps(v));return r.returncode
if __name__=='__main__':raise SystemExit(main())
