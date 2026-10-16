"""Same fixed148 publication stage/activate, all guards and seven phases retained."""
import hashlib
import json
import subprocess
import pg4006_literal_invariant_publication_dispatch as previous
import pg4540_failed_current_publication_sources as role
from pg4542_failed_current_publication_compile import TARGET,generated
from pg4434_current_candidate_admission_read import authenticate_host
from pg4546_failed_current_publication_post import payload as post_payload

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4544-failed-current-publication-stage-v1'
STAGE=role.bind(previous.STAGE.replace(previous.REMOTE,REMOTE))


def qualify_fixed(fixed):
    names=fixed.get('fileHashes',{})
    required={role.CLASS+'.class',role.CLASS+'.java','Pg4540TransitionTest.class','Pg4540TransitionTest.java','pg4540_ordinary_publication_contract.py','pg4540_native_refs.py','pg4540_input_preflight.py'}
    if type(fixed.get('actualExit'))is not int or fixed['actualExit']!=0 or fixed.get('candidateSource')!=role.SOURCE or fixed.get('productionSource')!=role.CURRENT or fixed.get('candidateManifestSha256')!=role.BOM or not required.issubset(names)or any(n.startswith('Pg4522')or n.startswith('pg4522_')for n in names):raise ValueError('complete actual finite publication family only')


def source():
    raw=previous.source()
    for old,new in [('pg4006','pg4544'),('pg4004','pg4548'),('Pg4002','Pg4540'),('PG3748','PG3976')]:raw=raw.replace(old,new)
    compile(raw,'<new148 finite publication operator>','exec');return raw


def main():
    subprocess.run(['git','merge-base','--is-ancestor','b65d1283e9dc384f761899bc8448cd50b9f572fc','origin/main'],check=True)
    role.qualify();authenticate_host()
    cert=json.loads((role.W/'pg4548-import-graph-v1.safe.json').read_bytes());fixed_raw=(role.W/'pg4548-frozen-v1.safe.json').read_bytes()
    if type(cert.get('actualExit'))is not int or cert['actualExit']!=0 or cert.get('allActualImportLoopsPassed')is not True or cert.get('frozenManifestSha256')!=hashlib.sha256(fixed_raw).hexdigest():raise ValueError('actual full148 frozen import graph first')
    # Prepare/check the independent full11/seven-phase observer before any
    # publication mutation. This generation performs no guest operation.
    post_payload()
    ns={**vars(previous.previous.previous),'role':role,'TARGET':TARGET,'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'qualify_fixed':qualify_fixed}
    exec(compile(source(),'<same148 finite stage/activate>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
