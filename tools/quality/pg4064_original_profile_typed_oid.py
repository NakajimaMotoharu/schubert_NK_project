"""BUG1335: exact typed metadata; reuse sealed4060 compile, never recompile/replay."""
import inspect
import pg4060_original_profile_dual_stack as previous
from pg4058_original_read_profile import main as transport_main
import pg4058_original_read_profile as transport

SLOT = 'pg4064-original-read-profile-v1'


def payload(action):
    if action != 'run': raise ValueError('existing sealed compile; run only')
    raw = previous.payload(action).replace(previous.SLOT, SLOT)
    raw = previous.once(raw, 'require(save.is_dir())', "require(not os.path.lexists(save));save.mkdir(mode=0o700)")
    frozen = "Path('/var/lib/pgpt-s1-preservation/" + previous.SLOT + "')"
    raw = previous.once(raw, "java=save/'RootOriginalReadProfile.java';annotation=save/'spotbugs-annotations-4.10.4.jar';classes=save/'classes'",
                        "frozen=" + frozen + "\njava=frozen/'RootOriginalReadProfile.java';annotation=frozen/'spotbugs-annotations-4.10.4.jar';classes=frozen/'classes'")
    raw = raw.replace("save/'compile.safe.json'", "frozen/'compile.safe.json'")
    raw = previous.once(raw, 'select pid,classid,objid,objsubid,mode,granted from pg_locks',
                        'select pid,classid::bigint as classid,objid::bigint as objid,objsubid,mode,granted from pg_locks')
    compile(raw, '<typed-oid finite original profile>', 'exec')
    return raw


def main():
    namespace = {**transport.__dict__, 'payload': payload, 'SLOT': SLOT}
    exec(compile(inspect.getsource(transport_main), '<new diagnostic scope, immutable old classes>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
