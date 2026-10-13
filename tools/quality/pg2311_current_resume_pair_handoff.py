"""SSC274/275 same-peer fresh proof then owned Ref/Java ordinary TERM once."""
import datetime
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W,SSH
from pg2309_current_resume_pair_proof import body,bound,SLOT as PROOF_SLOT,SOURCE
from pg1667_unused_pair_once_handoff import BODY
from pg1665_unused_pair_contract import fresh_parent,parent_after_ref
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence

SLOT='pg2311-current-resume-pair-handoff-v1'
PROOF_SHA='dde2e4aef140fec30e7577b51d377b76fc09a25034f431982298af24d57d5d4c'


def payload():
    raw=body()
    handoff=BODY.replace('pg1664-current-unused-pair-proof-v1',PROOF_SLOT).replace('pg1667-unused-pair-owned-handoff-v1',SLOT)
    for old,new in [('291213','96640'),('5962776','1550071'),('291242','96671'),('5962938','1550259')]:handoff=handoff.replace(old,new)
    handoff=handoff.replace("['29']","['31']").replace("['32']","['90']")
    old="  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')"
    if handoff.count(old)!=1:raise ValueError('one exact current release required')
    handoff=handoff.replace(old,"  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG2126')")
    old="  require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())"
    if handoff.count(old)!=1:raise ValueError('one signed current artifact boundary required')
    handoff=handoff.replace(old,"  require(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126').is_dir()and(base/'pg2126-manifest.sig').is_file())")
    fresh=inspect.getsource(fresh_parent).replace("'29'","'31'").replace("'32'","'90'")
    raw='import errno\n'+inspect.getsource(confirmed_absence)+'\nPROOF_SHA='+repr(PROOF_SHA)+'\n'+fresh+'\n'+inspect.getsource(parent_after_ref)+'\n'+inspect.getsource(terminate)+'\n'+raw+handoff
    if check(raw,'<current resume owned pair once>'):raise ValueError('all recovery globals required')
    compile(raw,'<current same-peer owned pair>','exec')
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed rescue operator required')
    proof=json.loads((W/PROOF_SLOT/'manifest.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['productionSource']!=SOURCE or proof['guest']['proofSha256']!=PROOF_SHA:raise ValueError('actual full current owned pair proof required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw)
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(result.stderr);(out/'stages.private.jsonl').write_bytes(result.stdout)
    frames=[json.loads(line)for line in result.stdout.splitlines()if line.startswith(b'{')]
    value={'actualExit':result.returncode,'operatorSource':head,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'proofSha256':PROOF_SHA,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stages':frames,'oldCloseUnknown':True,'formalAccepted':False}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
