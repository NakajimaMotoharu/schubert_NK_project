"""Independent full owned-stop post on current4856, no lifecycle authority."""
import inspect
import pg2716_operation_owned_post as old
import pg3490_outbox_owned_sources as role

SLOT = 'pg3496-outbox-owned-post-v1'


def namespace():
    base = old.previous
    ns = {**base.__dict__, 'context': role.context, 'TOOLS': role.TOOLS, 'SOURCE': role.SOURCE,
          'SLOT': SLOT, 'candidate_bom': role.candidate_bom}
    for fn in [base.emit, base.payload, base.entry]:
        exec(compile(role.bind(inspect.getsource(fn)), '<new actual independent owned post>', 'exec'), ns)
    emit_fn = ns['emit']
    ns['emit'] = lambda *args, **kwargs: role.bind(emit_fn(*args, **kwargs))
    return ns


def entry():
    return namespace()['entry']()


if __name__ == '__main__':
    # Delegated2040.main encloses both seal capture and post in one gate.
    raise SystemExit(entry()())
