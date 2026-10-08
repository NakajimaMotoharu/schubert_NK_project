"""Fresh six-module PG593 full source; selected/old full results never credited as new."""
import hashlib
import pathlib


def policy():
    source = pathlib.Path(__file__).with_name('pg585_collect_full.py').read_text()
    policy_sha = hashlib.sha256(source.encode()).hexdigest()
    replacements = {
        'pg585-access-reactor-v3': ('pg593-grouped-six-host-v1', 1),
        'PG585-access-reactor-v3': ('PG593-grouped-six-host-v1', 1),
        'f820710d1a274530418a389e5dcb755441356dd0': ('afc470b47a422fb8029c23a96f647889d47a2e9e', 1),
        "assert int(specific.attrib['tests']) == 4": ("assert int(specific.attrib['tests']) == 9\n    session = ET.parse(run / 'batch/surefire-reports/TEST-dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest.xml').getroot()\n    assert int(session.attrib['tests']) == 27", 1),
        "'newAccessTests':4": ("'newAccessTests':5,'totalAccessCases':9,'totalSessionCases':27,'additionalCasesVsPG585':12", 1),
        "'collectorSourceSha256':sha(pathlib.Path(__file__))": ("'collectorSourceSha256':sha(pathlib.Path(__file__)),'collectorPolicySha256':" + repr(policy_sha), 1),
        "with (run/'manifest.safe.json').open('x')": ("assert result['tests']==3447 and result['suites']==511 and result['FESFlakyNotRun']==0\n    with (run/'manifest.safe.json').open('x')", 1),
    }
    for old, (new, count) in replacements.items():
        assert source.count(old) == count, old
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    exec(compile(policy(), '<sealed PG593 full collector>', 'exec'),
         {'__name__': '__main__', '__file__': __file__})
