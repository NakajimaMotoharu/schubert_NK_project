"""BUG918 explicit nested-byte admission; frozen PT recollection, not a rerun."""
from pathlib import Path

R = Path(__file__).resolve().parent


def source():
    raw = (R/'pg679_parent_collect.py').read_text()
    old = "    assert changed == ['dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame.class']"
    assert raw.count(old) == 1
    fixed = '''    assert changed == ['dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Guard.class', 'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame$Parent.class', 'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame.class']
    executable_hashes = {}
    for nested in ('Guard', 'Parent'):
        name = 'dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame$'+nested
        jars = [W/'pg672-entry-six-host-v2/bootstrap/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar', RUN/'schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar']
        views = [subprocess.check_output(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javap', '-p', '-c', '-classpath', str(jar), name]) for jar in jars]
        assert views[0] == views[1]
        executable_hashes[nested] = hashlib.sha256(views[0]).hexdigest()
'''
    raw = raw.replace(old, fixed.rstrip())
    raw = raw.replace("'changedMainClasses': changed,", "'changedMainClasses': changed, 'nestedExecutableIdenticalSha256': executable_hashes, 'qualificationRevision': 'PG679-v2',")
    assert raw.count('nestedExecutableIdenticalSha256') == 1
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R/'pg679_parent_collect_v2.py'), '__name__': 'frozen_parent_v2'}
    exec(compile(source(), '<explicit qualified nested class bytes>', 'exec'), env)
    env['main']()
