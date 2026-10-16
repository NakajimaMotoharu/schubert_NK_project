"""Every finite phase and all original/native46/resource post; no new Root acceptance."""
import inspect
import pg3794_hygiene_publication_post as previous
import pg3978_current_preservation_readonly as readonly
import pg4002_literal_invariant_publication_sources as role

SLOT = 'pg4008-literal-invariant-publication-independent-post-v1'


def publication():
    namespace = {**previous.__dict__, 'role': role}
    raw = inspect.getsource(previous.publication).replace('pg3788_ordinary_publication_contract', 'pg4002_ordinary_publication_contract')
    exec(compile(raw, '<all seven finite phase oracle>', 'exec'), namespace)
    return namespace['publication']()


def payload():
    namespace = {**previous.__dict__, 'readonly': readonly, 'role': role, 'publication': publication}
    raw = inspect.getsource(previous.payload)
    raw = raw.replace('role.ro.mapping.pinned', 'role.ro.unused.pinned')
    for old, new in [('pg3790', 'pg4004'), ('pg3794', 'pg4008'), ('pg3766_configuration_capture.py', 'pg3982_configuration_capture.py'),
                     ('PG3420', 'PG3748'), ('PG3748', 'PG3976'), ('pg3420-manifest.sig', 'pg3748-manifest.sig'), ('pg3748-manifest.sig', 'pg3976-manifest.sig'),
                     ('Native34', 'Native46'), ('native34', 'native46')]:
        # The two release/signature translations must be simultaneous.
        if old in {'PG3420', 'PG3748', 'pg3420-manifest.sig', 'pg3748-manifest.sig'}: continue
        raw = raw.replace(old, new)
    raw = raw.replace("('PG3420','PG3748'),('pg3420-manifest.sig','pg3748-manifest.sig')", "('PG3748','PG3976'),('pg3748-manifest.sig','pg3976-manifest.sig')")
    raw = raw.replace("'pg4008-hygiene-publication-independent-post-v1'", repr(SLOT))
    exec(compile(raw, '<whole new-source finite publication full post>', 'exec'), namespace)
    return namespace['payload']()


def main():
    raw = inspect.getsource(previous.main).replace('pg3792', 'pg4006')
    namespace = {**previous.__dict__, 'role': role, 'SLOT': SLOT, 'payload': payload}
    # Previous main delegates to its transport module, with our exact new roles.
    exec(compile(raw, '<new finite publication independent observer>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
