"""Independent full current/native46 plus candidate PID1 RO and normal receipt post."""
import inspect
import pg3786_hygiene_ro_post as previous
import pg3988_literal_invariant_unused_post as unused_post
import pg3994_literal_invariant_ro_sources as role

SLOT = 'pg4000-literal-invariant-ro-independent-post-v1'
EXTRA = previous.EXTRA.replace('PG3748', 'PG3976').replace('pg3784-hygiene-ro-completed-v1', role.SAVE)


def payload():
    namespace = {**previous.__dict__, 'previous': unused_post, 'EXTRA': EXTRA}
    exec(compile(inspect.getsource(previous.payload), '<full new candidate RO post>', 'exec'), namespace)
    return namespace['payload']()


def main():
    raw = inspect.getsource(previous.main).replace('pg3784', 'pg3998')
    namespace = {**previous.__dict__, 'role': role, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<independent new candidate RO result only>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
