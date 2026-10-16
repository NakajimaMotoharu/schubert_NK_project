"""Stage or no-action proof only, while original inspect retains the host gate."""
import inspect
import pg4176_partial_coordinator as previous
import pg4490_inspect_pair_handoff_sources as current

SLOT='pg4492-inspect-pair-tools-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+SLOT


def owner(path):
    raw=inspect.getsource(previous.owner)
    for old,new in [('595379','677797'),('14277246','16590755'),
        ('7bfafc9766fc7469583dd5e760d92c745ef1e14708f53706bfce601b0c003248','327e2d6db2083cd96850447dc8250dad4853af6b3f03571a266a414674fb331c')]:
        if old not in raw:raise ValueError('one fixed current host gate binding')
        raw=raw.replace(old,new)
    ns=dict(vars(previous));exec(compile(raw,'<current pre-operation inspect owner>','exec'),ns);return ns['owner'](path)


def files():return {'keeper.py':current.payload()}


def stage_payload():
    ns={**vars(previous),'files':files,'GUEST':GUEST}
    exec(compile(inspect.getsource(previous.stage_payload),'<new-only inspect keeper stage>','exec'),ns);return ns['stage_payload']()


def main():
    ns={**vars(previous),'SLOT':SLOT,'GUEST':GUEST,'files':files,'stage_payload':stage_payload,'owner':owner}
    exec(compile(inspect.getsource(previous.main),'<new-only stage/proof no recover>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
