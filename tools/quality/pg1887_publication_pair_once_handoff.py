"""QA047 one current Ref->Java TERM, full fresh proof and queued same host gate."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1883_publication_retained_diagnosis import owner
from pg1884_publication_current_pair_proof import Typed
from pg1885_publication_current_fd_proof import payload as proof_payload,SLOT as PROOF_SLOT
from pg1667_unused_pair_once_handoff import BODY
from pg1665_unused_pair_contract import fresh_parent,parent_after_ref
from pg782_owned_handoff import terminate
from pg1680_proc_reap_contract import confirmed_absence
from pg1724_retained_host_gate import queued_gate
from pg1877_warning_publication_sources import once

SLOT='pg1887-publication-pair-once-handoff-v1'
PROOF_SHA='5e7a7fefa13de5eb24a30894eaa836307756f7deb7151463e9159bd0907190a5'


def payload():
    raw=proof_payload();raw=raw[:raw.index("tool = base / 'pg1877-warning-publication-tools-v1'")]
    raw=once(raw,'require(children == {491029})','require(children == (set()if REF_CLOSED else{491029}))')
    raw=once(raw,"lines[-2:] == [b'1', b'1']","lines[-2:] == [b'1', b'1']")
    body=BODY.replace("expected['candidateNotPlaced']is True","expected['currentPublicationNotStarted']is True")
    body=body.replace('pg1664-current-unused-pair-proof-v1',PROOF_SLOT).replace('pg1667-unused-pair-owned-handoff-v1',SLOT)
    body=once(body,"  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')","  require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1638')")
    body=once(body,"  require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638').exists()and not(base/'pg1638-manifest.sig').exists())","  require(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846').is_dir()and(base/'pg1846-manifest.sig').is_file())")
    tree=Typed().visit(ast.parse(body));ast.fix_missing_locations(tree);body=ast.unparse(tree)+'\n'
    body=body.replace("['29']","['31']").replace("['32']","['90']")
    fresh=inspect.getsource(fresh_parent).replace("'29'","'31'").replace("'32'","'90'")
    raw='import errno\n'+inspect.getsource(confirmed_absence)+'\nREF_CLOSED=False\nPROOF_SHA='+repr(PROOF_SHA)+'\n'+fresh+'\n'+inspect.getsource(parent_after_ref)+'\n'+inspect.getsource(terminate)+'\n'+raw+body
    from pyflakes.api import check
    if check(raw,'<actual queued current publication recovery>'):raise ValueError('all actual recovery globals required')
    compile(raw,'<new one current pair handoff>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator required')
    for path in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md','documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']:
        raw=subprocess.check_output(['git','show','origin/main:'+path],text=True)
        if 'SSC283'not in raw and'SSC-283'not in raw:raise ValueError('published normal deployment recovery contract required')
    proof=json.loads((W/PROOF_SLOT/'manifest.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['guest']['proofSha256']!=PROOF_SHA:raise ValueError('actual full current proof required')
    os.umask(0o077);held=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw);completed=False
    def validate_owner(path):
        if path!=P/'current-management-critical.lock'or owner()!=held:raise ValueError('same retained sole host gate required')
        return True
    with queued_gate(P/'current-management-critical.lock',validate_owner=validate_owner,require_completion=lambda:completed)as acquired:
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=240)
        completed=r.returncode==0
        if completed and not acquired.wait(30):raise ValueError('normal original wrapper handoff required')
    (out/'stderr.private.log').write_bytes(r.stderr);(out/'stages.private.jsonl').write_bytes(r.stdout)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldRetainedHostOwner':held,'queuedSameHostGateAcquired':completed,'oldNormalCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:value['guest']=[json.loads(line)for line in r.stdout.splitlines()if line.startswith(b'{')]
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
