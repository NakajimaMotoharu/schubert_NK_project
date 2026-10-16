"""Run the frozen operational Java in inspect-only mode under full guards; no stop/revoke."""
import base64
import inspect
import json
import pg4084_recovery_inspection as previous
import pg4058_original_read_profile as transport
import pg4088_failed_done_owned_sources as role
from pg4060_original_profile_dual_stack import once


def payload():
    oldpins = json.loads((transport.W / (previous.SLOT + '-compile') / 'manifest.safe.json').read_bytes())['result']['classHashes']
    fixed = json.loads((transport.W / (role.TOOLS + '-compile') / 'manifest.safe.json').read_bytes())
    if fixed['actualExit'] != 0 or fixed['result']['actualExit'] != 0: raise ValueError('actual complete operational compile first')
    fixed = fixed['result']; raw = previous.payload('run').replace(previous.SLOT, role.INSPECT)
    line = next(line for line in raw.splitlines() if line.startswith('JAVA_B64='))
    raw = once(raw, line, 'JAVA_B64=' + repr(base64.b64encode(role.java().encode()).decode()))
    raw = once(raw, 'require(save.is_dir())', 'require(not os.path.lexists(save));save.mkdir(mode=0o700)')
    raw = once(raw, "java=save/'RootRecoveryInspect.java';annotation=save/'spotbugs-annotations-4.10.4.jar';classes=save/'classes'",
               "frozen=Path('/var/lib/pgpt-s1-preservation/" + role.TOOLS + "')\njava=frozen/'RootFailedDoneRecovery.java';annotation=frozen/'spotbugs-annotations-4.10.4.jar';classes=frozen/'classes'")
    raw = raw.replace("save/'compile.safe.json'", "frozen/'compile.safe.json'")
    if raw.count(repr(oldpins)) != 2: raise ValueError('both complete compiled-byte checks required')
    raw = raw.replace(repr(oldpins), repr(fixed['classHashes']))
    raw = once(raw, "'dev.codex.schubert.nk.batch.file.RootRecoveryInspect']", "'dev.codex.schubert.nk.batch.file.RootFailedDoneRecovery','inspect']")
    for old, new in [('ORIGINAL_PROFILE_READY', 'RECOVERY_READY'), ('ORIGINAL_PROFILE_MEASURED', 'RECOVERY_INSPECTED'),
                     ('ORIGINAL_PROFILE_CLOSED', 'RECOVERY_CLOSED'), ('ORIGINAL_PROFILE_NORMAL_RETURN', 'RECOVERY_NORMAL_RETURN oldParentNormal=false')]:
        raw = raw.replace(old, new)
    marker = "require(not os.path.lexists(save/'run-reserved.private'))"
    extra = "INPUT_HASHES=" + repr(fixed['inputFileHashes']) + "\nfor name,digest in INPUT_HASHES.items():\n p=frozen/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest and p.lstat()==s)\n"
    raw = once(raw, marker, extra + marker)
    raw = once(raw, "'recoveryAuthorityIssued':False", "'recoveryAuthorityIssued':False,'operationalArtifactInspectOnly':True")
    raw = raw.replace("'_JAVA_OPTIONS','CLASSPATH']", "'_JAVA_OPTIONS','CLASSPATH','LD_PRELOAD','LD_LIBRARY_PATH']")
    compile(raw, '<frozen operational inspect only>', 'exec')
    return raw


def main():
    namespace = {**transport.__dict__, 'payload': lambda action: payload(), 'SLOT': role.INSPECT}
    namespace['sys'] = type('InspectOnlyArguments', (), {'argv': ['inspect_stage', 'run']})
    exec(compile(inspect.getsource(transport.main), '<operational inspect only>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
