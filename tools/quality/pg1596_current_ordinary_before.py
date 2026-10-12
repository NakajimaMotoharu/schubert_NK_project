"""Fresh fully retired/DONE current preflight, data-only before new noargs run."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1595_current_runtime_retired_post import payload as previous
from pg1591_current_runtime_retirement_sources import SOURCE,TOOLS

def payload():
    post=json.loads((W/'pg1595-current-runtime-retired-post-v1.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['runtimeExactEntryRetired']or not post['allClientAdvisoryFlock0']:raise ValueError('current normal retirement fullpost required')
    build=json.loads((W/'pg1592-frozen-v1.safe.json').read_bytes());names=['Pg1591NativeStop.class','Pg1591NativeStop$References.class','pg1591_native_refs.py','pg1591_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg1591_parent_receipt.py','pg1591_durable.py','pg1591_configuration.py','pg1591_configuration_capture.py','pg1591_row_bound.py','pg1591_stable_journal.py']
    hashes={n:build['fileHashes'][n]for n in names};seals={n:post['proofHashes'][n]['sha256']for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
    raw=previous(seals);marker="result={'actualExit':0"
    if raw.count(marker)!=1:raise ValueError('current completed preflight result boundary absent')
    raw=raw[:raw.index(marker)]+BODY
    raw='HASHES='+repr(hashes)+'\nRECEIPT='+repr((W/TOOLS/'pg1591_parent_receipt.py').read_text())+'\n'+raw
    compile(raw,'<current full retired ordinary before>','exec');return raw

BODY=r'''
require(native==after['native'])
parse_raw=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(parse_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
node=next(n for n in ast.parse(parse_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');scope={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<signed declaration parse>','exec'),scope)
declaration=scope['exec_record'](after['configuration']['schubert-nk-morning-controller.service']['ExecStart'])
require(declaration is not None and declaration[1].endswith('dev.codex.schubert.nk.batch.file.MorningProcessMain')and '--resume'not in declaration[1])
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf').exists()and not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
raw=(base/'pg1591-native-stop-v1/after.private.json').read_bytes();require(json.loads(raw)==after)
save=base/'pg1596-current-ordinary-before-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'source':data['source']['commit'],'privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'originalBudgetSeconds':1800,'allTenKernelEmpty':True,'allOriginalDbBackupNativePreserved':True,'genuinePreviousCompletion':summary,'configurationSigned187':True,'authority':False,'formalAccepted':False}))
'''

def main():
    os.umask(0o077);out=W/'pg1596-current-ordinary-before-v1';out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90);(out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:value.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return r.returncode

if __name__=='__main__':raise SystemExit(main())
