"""One new stage then same-source candidate-only RO; no public/start authority."""
import inspect
import subprocess
import pg3784_hygiene_ro_dispatch as base
import pg3998_literal_invariant_ro_dispatch as previous
import pg4522_failed_current_ro_sources as role
from pg4524_failed_current_ro_compile import TARGET,generated
from pg1446_current_cold_stage import W
import hashlib
import json
from pg4434_current_candidate_admission_read import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4532-fixed-stage-v1'
STAGE=role.bind(previous.STAGE)


def source():
    raw=inspect.getsource(base.main)
    for old,new in [('pg3784','pg4532'),('pg3782','pg4530'),('Pg3780','Pg4522'),('PG3420','PG3976')]:raw=raw.replace(old,new)
    return raw


def main():
    subprocess.run(['git','merge-base','--is-ancestor','b65d1283e9dc384f761899bc8448cd50b9f572fc','origin/main'],check=True)
    authenticate_host()
    certificate=json.loads((W/'pg4530-import-graph-v1.safe.json').read_bytes())
    if certificate.get('actualExit')!=0 or certificate.get('allActualImportLoopsPassed')is not True or certificate.get('frozenManifestSha256')!=hashlib.sha256((W/'pg4530-frozen-v1.safe.json').read_bytes()).hexdigest():raise ValueError('actual complete same141 import closure first')
    ns={**vars(base),'role':role,'TARGET':TARGET,'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(source(),'<current failed-data RO finite operator>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
