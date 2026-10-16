"""SSC293 new only entry; previous4348 was refused before signals and is never replayed."""
import inspect
import pg4188_exact_partial_recover as transport
import pg4348_current_partial_recover as previous
import pg4366_pool_bound_coordinator as staged
import pg4360_pool_bound_partial_sources as sources

OUT = transport.W / 'pg4368-pool-bound-recover-v1'
DESIGN_MAIN = 'PENDING_SSC293_MAIN'
original_receipt = previous.original_receipt


def bootstrap(name, hashes):
    ns = {**vars(transport), 'GUEST': staged.GUEST}
    exec(compile(inspect.getsource(transport.bootstrap), '<pool-bound frozen envelope>', 'exec'), ns)
    return ns['bootstrap'](name, hashes)


def remote_args(name, hashes, mode=None):
    ns = {**vars(transport), 'bootstrap': bootstrap}
    exec(compile(inspect.getsource(transport.remote_args), '<pool-bound phase transport>', 'exec'), ns)
    return ns['remote_args'](name, hashes, mode)


def main_source():
    return previous.main_source().replace('SSC292_', 'SSC293_')


def main():
    if DESIGN_MAIN == 'PENDING_SSC293_MAIN':
        raise ValueError('no authority until final design-only main publication')
    if OUT.exists():
        raise ValueError('one new current job only; never replay')
    ns = {**vars(transport), 'OUT': OUT, 'DESIGN_MAIN': DESIGN_MAIN,
          'TOOLS': staged.SLOT, 'GUEST': staged.GUEST, 'owner': staged.owner,
          'files': sources.files, 'remote_args': remote_args, 'original_receipt': original_receipt}
    exec(compile(inspect.getsource(transport.private), '<pool-bound durable receipt>', 'exec'), ns)
    exec(compile(main_source(), '<new pool-bound one-shot handoff>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
