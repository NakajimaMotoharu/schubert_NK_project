"""SSC274/276/283: current proved Ref then Java pidfd TERM, queued sole gate."""
import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W, P, SSH
import pg2138_current_normal_pair_proof as proof
from pg1667_unused_pair_once_handoff import BODY
from pg1665_unused_pair_contract import fresh_parent, parent_after_ref
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence
from pg1724_retained_host_gate import queued_gate

SLOT='pg2140-current-normal-pair-owned-handoff-v1'
PROOF_SHA='83eaa0ae5d3b17c06871841fe856c848f3b0ba355d399cf1c02c4945dc67a7a8'


def owner():
    q=Path('/proc/388894');st=(q/'stat').read_text().rpartition(')')[2].split()
    if (int(st[19]),int(st[1]))!=(12454900,4233) or hashlib.sha256((q/'cmdline').read_bytes()).hexdigest()!='2c1d5dd068a3f01aad439bd64913558e85717650d413372182c35003be36d318':
        raise ValueError('current retained immutable wrapper required')
    path=P/'current-management-critical.lock';s=path.stat();fd=(q/'fd/4').stat()
    if (s.st_dev,s.st_ino)!=(fd.st_dev,fd.st_ino):raise ValueError('current gate FD required')
    hits=[]
    for line in Path('/proc/locks').read_text().splitlines():
        v=line.split()
        if len(v)>=8 and v[1]=='FLOCK' and v[5]==f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}':hits.append(v)
    if len(hits)!=1 or hits[0][1:5]!=['FLOCK','ADVISORY','WRITE','388894']:
        raise ValueError('same sole current host gate required')
    return {'pid':388894,'ticks':12454900,'fd':4,'dev':s.st_dev,'inode':s.st_ino}


def payload():
    raw=proof.payload();raw=raw[:raw.index("tool=base/'"+proof.TOOLS+"'")]
    needle='require(children == {676916})'
    if raw.count(needle)!=1:raise ValueError('exact current child boundary required')
    raw=raw.replace(needle,'require(children == (set()if REF_CLOSED else{676916}))')
    body=BODY.replace('pg1664-current-unused-pair-proof-v1',proof.SLOT).replace('pg1667-unused-pair-owned-handoff-v1',SLOT)
    body=body.replace('0.1.0-PG1544','0.1.0-PG1846').replace('0.1.0-PG1638','0.1.0-PG2126').replace('pg1638-manifest.sig','pg2126-manifest.sig')
    tree=proof.Current().visit(ast.parse(body));ast.fix_missing_locations(tree)
    body=ast.unparse(tree).replace("['29']","['31']").replace("['32']","['90']")+'\n'
    fresh=inspect.getsource(fresh_parent).replace("'29'","'31'").replace("'32'","'90'")
    raw='import errno\n'+inspect.getsource(confirmed_absence)+'\nREF_CLOSED=False\nPROOF_SHA='+repr(PROOF_SHA)+'\n'+fresh+'\n'+inspect.getsource(parent_after_ref)+'\n'+inspect.getsource(terminate)+'\n'+raw+body
    from pyflakes.api import check
    if check(raw,'<actual current normal pair handoff>'):raise ValueError('whole actual namespace required')
    compile(raw,'<current normal owned pair once>','exec');return raw


def main():
    # WIP recovery tools are separate bytes: do not change the retained operator HEAD.
    if subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!='7e519fe34b07beef24a3d943fddba639299842ed':
        raise ValueError('unchanged original operator HEAD required')
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']:
        raw=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        if 'SSC283'not in raw and 'SSC-283'not in raw:raise ValueError('published normal recovery contract required')
    old=json.loads((W/proof.SLOT/'manifest.safe.json').read_bytes())
    if old['actualExit']!=0 or old['guest']['proofSha256']!=PROOF_SHA:raise ValueError('full current proof required')
    os.umask(0o077);held=owner();out=W/SLOT;out.mkdir(mode=0o700)
    raw=payload().encode();(out/'payload.private.py').write_bytes(raw);completed=False
    def validate(path):
        if path!=P/'current-management-critical.lock' or owner()!=held:raise ValueError('same host owner required')
        return True
    with queued_gate(P/'current-management-critical.lock',validate_owner=validate,require_completion=lambda:completed)as acquired:
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=240)
        completed=r.returncode==0
        if completed and not acquired.wait(30):raise ValueError('normal queued gate handoff required')
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stages.private.jsonl').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldRetainedHostOwner':held,'queuedSameHostGateAcquired':completed,'oldNormalCloseUnknown':True,'formalAccepted':False}
    if not r.returncode:value['guest']=[json.loads(line)for line in r.stdout.splitlines()if line.startswith(b'{')]
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
