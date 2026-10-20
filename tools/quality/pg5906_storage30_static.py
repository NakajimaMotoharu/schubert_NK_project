"""Independent exact storage PG, all851/1666 Main, public ABI and unfiltered static."""
import hashlib
import inspect
import re
import subprocess
import pg5776_jms_primary_static as engine
from pg5804_rollback_static import class_key, signature

PREFIX = 'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/'
REWRITES = {
    'LinuxExecDescriptors.java': [
        ('public final class LinuxExecDescriptors {', 'public final class LinuxExecDescriptors {\n  private static final int FD_CLOEXEC = 1;\n'),
        ('if (fcntl.call(descriptor, 1, 0) != 1)', 'if (fcntl.call(descriptor, 1, 0) != FD_CLOEXEC)'),
        ('() -> set(descriptor, 1)', '() -> set(descriptor, FD_CLOEXEC)')],
    'LinuxFilesystemClassifier.java': [
        ('  private static final long SIZE = 120;', '  private static final long SIZE = 120;\n  private static final long EXT_FAMILY_MAGIC = 0xEF53L;\n  private static final long XFS_MAGIC = 0x58465342L;\n  private static final long BTRFS_MAGIC = 0x9123683EL;\n  private static final long TMPFS_MAGIC = 0x01021994L;'),
        ('if (magic == 0xEF53L)', 'if (magic == EXT_FAMILY_MAGIC)'),
        ('if (magic == 0x58465342L)', 'if (magic == XFS_MAGIC)'),
        ('if (magic == 0x9123683EL)', 'if (magic == BTRFS_MAGIC)'),
        ('if (magic == 0x01021994L)', 'if (magic == TMPFS_MAGIC)')],
    'LinuxSealedProof.java': [
        ('public final class LinuxSealedProof {', 'public final class LinuxSealedProof {\n  private static final int REQUIRED_SEALS = 15;\n'),
        ('fcntl.call(descriptor, 1033, 15)', 'fcntl.call(descriptor, 1033, REQUIRED_SEALS)'),
        ('if (fcntl.call(admittedDescriptor, 1034, 0) != 15)', 'if (fcntl.call(admittedDescriptor, 1034, 0) != REQUIRED_SEALS)')],
    'StorageAttributeGuard.java': [
        ('public final class StorageAttributeGuard {', 'public final class StorageAttributeGuard {\n  private static final long MINIMUM_FILE_SIZE = 1;\n'),
        ('if (expectedSize < 1 || expectedSize > 48_000_000L)', 'if (expectedSize < MINIMUM_FILE_SIZE || expectedSize > 48_000_000L)'),
        ('if (expectedSize < 1)', 'if (expectedSize < MINIMUM_FILE_SIZE)')],
    'StorageRootInspection.java': [
        ('public final class StorageRootInspection {', 'public final class StorageRootInspection {\n  private static final int ASSET_ROOT_INDEX = 0;\n  private static final int TRANSFER_ROOT_INDEX = 1;\n  private static final int BACKUP_ROOT_INDEX = 2;\n'),
        ('if (index == 0)', 'if (index == ASSET_ROOT_INDEX)'),
        ('else if (index == 1)', 'else if (index == TRANSFER_ROOT_INDEX)'),
        ('else if (index == 2)', 'else if (index == BACKUP_ROOT_INDEX)')],
    'OwnedTransferDirectory.java': [
        ('import java.util.UUID;', 'import java.util.UUID;\nimport java.util.concurrent.locks.ReentrantLock;'),
        ('  private final Object stateLock = new Object();', '  private final ReentrantLock stateLock = new ReentrantLock();')]}
MODIFIED = {PREFIX + p for p in REWRITES}


def expected_source(path, before):
    for old, new in REWRITES[path.removeprefix(PREFIX)]:
        if before.count(old) != 1:
            raise ValueError('one exact existing storage expression')
        before = before.replace(old, new, 1)
    if path.endswith('/OwnedTransferDirectory.java'):
        pattern = re.compile(r'^    synchronized \(stateLock\) \{\n(.*?)^    \}', re.MULTILINE | re.DOTALL)
        def substitute(match):
            return '    stateLock.lock();\n    try {\n' + match.group(1) + '    } finally {\n      stateLock.unlock();\n    }'
        before, count = pattern.subn(substitute, before)
        if count != 21 or 'synchronized (stateLock)' in before:
            raise ValueError('all21 identical bodies/critical sections and finally releases')
    return before


def pg_contract(snapshot, value, old):
    sources = {p.relative_to(snapshot).as_posix(): engine.sha(p) for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(sources) != 851 or set(sources) != set(old['allSourceHashes']) or {p for p in sources if sources[p] != old['allSourceHashes'][p]} != MODIFIED:
        raise ValueError('exact six Main source changes, all851 preserved')
    prior = engine.W / 'pg5880-terminal-serial83-v1/source'
    changed_src = subprocess.check_output(['git', 'diff', '--name-only', old['source'], value['source'], '--', 'src'], cwd=engine.ROOT, text=True).splitlines()
    if set(changed_src) != MODIFIED:
        raise ValueError('Test/oracle/resources/POM unchanged')
    for path, digest in sources.items():
        if hashlib.sha256(subprocess.check_output(['git', 'show', value['source'] + ':' + path], cwd=engine.ROOT)).hexdigest() != digest:
            raise ValueError('canonical compiled source')
    for path in MODIFIED:
        if expected_source(path, (prior / path).read_text()) != (snapshot / path).read_text() or signature(prior, path) != signature(snapshot, path):
            raise ValueError('only declared same values/critical sections; existing public ABI')
    oldmap, new = old['auxClassHashes'], value['allPhysicalMainSha256']
    outer = {class_key(p) for p in MODIFIED}
    changed = {k for k in oldmap if k in new and oldmap[k] != new[k]}
    if len(oldmap) != 1666 or len(new) != 1666 or set(oldmap) != set(new) or not outer <= changed or any(not any(k == o or k.startswith(o[:-6] + '$') for o in outer) for k in changed):
        raise ValueError('all1666 bytes; only six declared outer owners and actual nested/debug differences')
    return sources, sorted(changed)


def runner_source():
    raw = inspect.getsource(engine.main)
    changes = {
        'pg5774-jms-primary-green-v1/manifest.safe.json': 'pg5904-storage30-selected199-v1/manifest.safe.json',
        "(v['tests'],v['suites'])==(14,7)": "(v['tests'],v['suites'])==(199,33)",
        'pg5750-exception-static-v1/manifest.safe.json': 'pg5882-terminal-serial-static-v1/manifest.safe.json',
        'provisional/PG5750-exception-static-v1/manifest.json': 'provisional/PG5882-terminal-serial-static-v1/manifest.json',
        '70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9': '2b5a42b051c804000affd8b92ea51c51c4e6dcf8e21addbed975a966335b7ec8',
        '    guards=guard_coverage(snapshot)': '    guards=v["targetCounters"]',
        "expected_counts['CompareObjectsWithEquals']+=3": "expected_counts['AvoidLiteralsInIfCondition']-=9;expected_counts['AvoidSynchronizedStatement']-=21",
        "'changedSourcePaths':sorted(PATHS)": "'changedSourcePaths':sorted(MODIFIED)",
        "'physicalMain':1664": "'physicalMain':1666",
        "'unchangedPhysicalClasses':1662": "'unchangedPhysicalClasses':1666-len(classes)",
        "'allFieldAndMethodDescriptorsUnchanged':True": "'existingPublicAbiUnchanged':True,'removedPublicDescriptors':0,'addedPublicDescriptors':0,'rawDiagnosticsRemovedByPg':30",
        "'inputSourceFiles':849": "'inputSourceFiles':851", "'actualAuxClasses':1664": "'actualAuxClasses':1666",
        "'newGuardsActualCoverage':guards": "'selectedTargetActualCounters':guards",
        ",'newGuardsActualCoverage','F03Accepted'": ",'selectedTargetActualCounters','F03Accepted'",
        "provisional/PG5776-jms-primary-static-v1';target.mkdir()": "provisional/PG5906-storage30-static-v1';target.mkdir()"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one exact all851 storage static binding: ' + old)
        raw = raw.replace(old, new, 1)
    start = raw.index('    sources=')
    end = raw.index("    for name in('pmd.xml','checkstyle.xml'):", start)
    raw = raw[:start] + "    sources,classes=pg_contract(snapshot,v,old)\n    current=v['allPhysicalMainSha256'];before_snapshot=W/'pg5880-terminal-serial83-v1/source'\n" + raw[end:]
    compile(raw, '<storage all851 static>', 'exec')
    return raw


def main():
    scope = {**vars(engine), 'SLOT': 'pg5906-storage30-static-v1', 'MODIFIED': MODIFIED, 'pg_contract': pg_contract}
    exec(compile(runner_source(), '<storage all851 static>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
