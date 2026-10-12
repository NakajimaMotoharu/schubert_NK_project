"""Separate no-signal current full post after once owned profile pair handoff."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
import pg1520_profile_retained_pair_proof as proof
from pg1521_profile_pair_once_handoff import SLOT as HANDOFF,PROOF_SHA
from pg1503_retained_pair_independent_closing import BODY

SLOT='pg1522-retained-profile-pair-closing-v1'
def payload():
 raw=proof.payload();start=raw.index('first=snapshot();require(first==snapshot());validate_current(first);a=pair();');prefix=raw[:start]
 begin=prefix.index('q=subprocess.run(');end=prefix.index('\n',prefix.index('sys.argv=',begin))
 prefix=prefix[:begin]+"sys.argv=['readonly-profile-closing','verify','2']"+prefix[end:]
 prefix=prefix.replace('require(not os.path.lexists(PAIR_SAVE))','require(os.path.isdir(PAIR_SAVE))')
 body=BODY
 for a,b in [('pg1503-retained-publication-pair-closing-v1',SLOT),('pg1498-retained-publication-pair-proof-v1',proof.SLOT),('pg1502-retained-publication-pair-handoff-v4',HANDOFF),('b76ba20d9c058cbf07f37f47356ba472bc33270d6bfdac9a804a64584923efba',PROOF_SHA),('92297',str(proof.PID)),('92323',str(proof.CHILD)),("'brokerStillActive':True","'brokerStillActive':False")]:body=body.replace(a,b)
 marker="{'98426.term-once.private','98452.term-once.private'}";assert marker in body
 body=body.replace(marker,"{'98426.term-once.private','98452.term-once.private','after.private.json','complete.private'}")
 return prefix+'\n'+body
def main():
 os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
 prior=json.loads((W/HANDOFF/'manifest.safe.json').read_bytes());assert prior['actualExit']==0
 saved=(W/proof.SLOT/'payload.private.py').read_text();nodes=[n for n in ast.parse(saved).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'EXPECTED_ARGS','FROZEN_HASHES','CHILD_TICKS'}for t in n.targets)];assert len(nodes)==3
 raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+payload();compile(raw,'<independent current profile full closing>','exec');(out/'payload.private.py').write_text(raw)
 r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=90);(out/'stderr.private.log').write_bytes(r.stderr)
 v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'signals0':True,'oldNormalCloseUnknown':True,'formalAccepted':False}
 if r.returncode==0:v['guest']=json.loads(r.stdout)
 with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps(v));return r.returncode
if __name__=='__main__':raise SystemExit(main())
