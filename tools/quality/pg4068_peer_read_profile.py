"""Fixed manager/kernel read timings, no HTTP/access-log writes or service action."""
import inspect
import pg4050_root_unit_read_profile as transport
import pg4056_file_profile_compile_dependency as compiled

SLOT = 'pg4068-peer-read-profile-v1'


def payload():
    namespace = {**transport.__dict__}
    raw = inspect.getsource(transport.payload).replace('RootUnitReadProfile', 'RootPeerReadProfile')
    raw = raw.replace('pg4050-unit-read-profile-v1', SLOT)
    exec(compile(raw, '<fixed peer diagnostic>', 'exec'), namespace)
    old = compiled.previous.payload
    try:
        compiled.previous.payload = namespace['payload']
        result = compiled.payload().replace(compiled.SLOT, SLOT)
    finally: compiled.previous.payload = old
    compile(result, '<new-only real peer read diagnostic>', 'exec')
    return result


def main():
    namespace = {**transport.__dict__, 'payload': payload}
    raw = inspect.getsource(transport.main).replace('pg4050-unit-read-profile-v1', SLOT)
    exec(compile(raw, '<peer read-only profile>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
