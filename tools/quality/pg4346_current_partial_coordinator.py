"""SSC292 new-only stage/proof under current original gate; no recover entry here."""
import inspect
import pg4176_partial_coordinator as previous
import pg4338_current_partial_sources as current

SLOT = 'pg4346-current-partial-tools-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + SLOT


def owner(path):
    raw = inspect.getsource(previous.owner)
    for old, new in [('595379', '634760'), ('14277246', '15505417'),
                     ('7bfafc9766fc7469583dd5e760d92c745ef1e14708f53706bfce601b0c003248',
                      '3e3ae1f6ccbcdb4d168804900b607bdaf441e8c52c8fe7db3bf594a778ab3c33')]:
        if old not in raw:
            raise ValueError('exact current host ownership binding required')
        raw = raw.replace(old, new)
    ns = dict(vars(previous))
    exec(compile(raw, '<current original host gate owner>', 'exec'), ns)
    return ns['owner'](path)


def files():
    return current.files()


def stage_payload():
    ns = {**vars(previous), 'files': files, 'GUEST': GUEST}
    exec(compile(inspect.getsource(previous.stage_payload), '<current stage factory>', 'exec'), ns)
    return ns['stage_payload']()


def main():
    ns = {**vars(previous), 'SLOT': SLOT, 'GUEST': GUEST, 'files': files,
          'stage_payload': stage_payload, 'owner': owner}
    exec(compile(inspect.getsource(previous.main), '<current stage/proof transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
