"""Finite once-only publication, using normal M/A/DB/Ref contract; never a Root start."""
import inspect
import pg3454_current_outbox_publication_dispatch as template
import pg3784_hygiene_ro_dispatch as previous
import pg3788_hygiene_publication_sources as role
from pg3790_hygiene_publication_compile import TARGET, generated

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg3792-hygiene-publication-stage-v1'
STAGE=role.bind(template.stage(template.role.ro.role.BOM).replace(template.REMOTE,REMOTE))


def source():
    raw=inspect.getsource(previous.main).replace('pg3784','pg3792').replace('Pg3780','Pg3788').replace('prepare-ro','activate')
    raw=raw.replace("'Pg3788InputBoundaryTest',role.CLASS","'Pg3788InputBoundaryTest','Pg3788TransitionTest',role.CLASS")
    raw=raw.replace("'candidateHostReadonlyOnly':True,'currentApprovalEpochChanged':False","'finiteCodeOnlyPublication':True,'currentApprovalEpochChanged':(False if action=='stage' else True if result.returncode==0 else None)")
    return raw


def main():
    namespace={**previous.__dict__,'role':role,'TARGET':TARGET,'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(source(),'<new-only finite publication dispatcher>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
