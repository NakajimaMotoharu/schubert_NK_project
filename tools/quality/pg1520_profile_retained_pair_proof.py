"""BUG1121 exact still-owned profile Java/Ref proof; read-only, no signal."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1512_original_component_profile_sources import refs,TOOLS
import pg1498_retained_pair_readonly_proof as original

PID=98426
TICKS=1876733
CHILD=98452
CHILD_TICKS=1876815
SLOT='pg1520-retained-profile-pair-proof-v1'

def payload():
 nodes=[]
 for n in ast.parse(refs()).body:
  if isinstance(n,ast.Try):break
  nodes.append(n)
 raw=ast.unparse(ast.Module(body=nodes,type_ignores=[])).replace('os.getppid()',str(PID)).replace('os.getpid()',str(CHILD))
 pre=original.PRE.replace('PG266-publication-recover','PG269-original-io-profile')
 body=original.BODY
 for a,b in [('pg1498-retained-publication-pair-proof-v1',SLOT),('92297',str(PID)),('1431673',str(TICKS)),('92323',str(CHILD)),('pg1493-publication-only-tools-v2',TOOLS),('pg1493_publication_recovery_refs.py','pg1512_original_component_refs.py')]:body=body.replace(a,b)
 marker='first=snapshot();require(first==snapshot());validate_current(first);a=pair();'
 assert marker in body
 raw+='\ndef validate_current(value):\n require(value==profile_expected)\n for unit in UNITS:kernel_empty(unit)\n'
 return pre+raw+'\n'+body

def main():
 os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
 begin=json.loads((W/'pg1514-original-component-profile-v1/begin.safe.json').read_bytes());args=begin['command'];expected=args[args.index('/opt/jdk-25.0.4/bin/java'):]
 fixed=json.loads((W/'pg1512-original-component-frozen-v1.safe.json').read_bytes());assert fixed['actualExit']==0 and fixed['operatorSource']=='00a2a590e51a6a41d8d1014ba1c608b7a6507316'
 raw='EXPECTED_ARGS='+repr(expected)+'\nFROZEN_HASHES='+repr(fixed['fileHashes'])+'\nCHILD_TICKS='+str(CHILD_TICKS)+'\n'+payload();compile(raw,'<current retained profile pair proof>','exec')
 (out/'payload.private.py').write_text(raw)
 r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=90)
 (out/'stderr.private.log').write_bytes(r.stderr)
 value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'signals0':True,'formalAccepted':False}
 if r.returncode==0:value['guest']=json.loads(r.stdout)
 with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps(value));return r.returncode
if __name__=='__main__':raise SystemExit(main())
