"""New immutable metadata-only proof under the exact current original host gate."""
import inspect
import pg4176_partial_coordinator as previous
import pg4510_metadata_only_handoff_sources as current

SLOT='pg4512-metadata-only-tools-v1';GUEST='/var/lib/pgpt-s1-preservation/'+SLOT


def owner(path):
    raw=inspect.getsource(previous.owner)
    for old,new in [('595379','684367'),('14277246','16801848'),
        ('7bfafc9766fc7469583dd5e760d92c745ef1e14708f53706bfce601b0c003248','4ab84c72f05adb16d0edef0fd3b41563692a6efc9e00fcaede27bfa04fa66b74')]:
        if old not in raw:raise ValueError('exact current metadata-only host binding')
        raw=raw.replace(old,new)
    ns=dict(vars(previous));exec(compile(raw,'<current metadata-only host gate>','exec'),ns);return ns['owner'](path)


def files():return {'keeper.py':current.payload()}


def stage_payload():
    ns={**vars(previous),'files':files,'GUEST':GUEST};exec(compile(inspect.getsource(previous.stage_payload),'<metadata-only stage>','exec'),ns);return ns['stage_payload']()


def main():
    ns={**vars(previous),'SLOT':SLOT,'GUEST':GUEST,'files':files,'stage_payload':stage_payload,'owner':owner}
    exec(compile(inspect.getsource(previous.main),'<metadata-only stage/proof>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
