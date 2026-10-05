"""SSC193 selected diagnostics only. No full/native/formal reuse or raw log export."""
import datetime, hashlib, json, pathlib, subprocess, xml.etree.ElementTree as ET
T = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE = W / 'pg470-profile-selected-v4'
OUT = T / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG470-profile-selected-v4'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    assert not OUT.exists() and BASE.with_suffix('.exit').read_text().strip() == '0'
    start = datetime.datetime.fromisoformat(BASE.with_suffix('.started').read_text().strip()).timestamp()
    end = datetime.datetime.fromisoformat(BASE.with_suffix('.completed').read_text().strip()).timestamp()
    classes = {'protocol': ['MessageCodecTest'], 'storage': ['ResourceScopeTest', 'PrivateDirectoryEntryTest'],
               'bootstrap': ['FixedServiceIdentityTest', 'FixedServiceExecArgumentsTest', 'FixedNativeCoverageProfileTest']}
    xml = {}; count = 0
    for module, names in classes.items():
        root = T / 'src' / ('schubert-nk-' + module) / 'target/surefire-reports'
        for name in names:
            matches = list(root.glob('TEST-*.' + name + '.xml')); assert len(matches) == 1
            # Shell markers are whole seconds; end denotes [end,end+1), not a rounded nanosecond.
            path = matches[0]; assert start <= path.stat().st_mtime < end + 1
            suite = ET.parse(path).getroot()
            assert all(int(suite.get(key, '-1')) == 0 for key in ['failures', 'errors', 'skipped'])
            assert len(suite.findall('testcase')) == int(suite.get('tests'))
            assert not any(case.find(tag) is not None for case in suite.findall('testcase') for tag in ['failure', 'error', 'skipped', 'flakyFailure', 'rerunFailure'])
            count += int(suite.get('tests')); xml[name] = {'tests': int(suite.get('tests')), 'sha256': sha(path)}
        static = T / 'src' / ('schubert-nk-' + module) / 'target/spotbugsXml.xml'
        assert start <= static.stat().st_mtime < end + 1 and not ET.parse(static).getroot().findall('BugInstance')
    assert count == 47
    log = BASE.with_suffix('.log').read_text(); assert '[INFO] BUILD SUCCESS' in log
    assert log.count('BugInstance size is 0') == 3
    files = ['src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/OwnedTransferDirectory.java',
             'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/PrivateDirectoryEntryTest.java']
    files += ['src/schubert-nk-bootstrap/src/' + part + '/java/dev/codex/schubert/nk/bootstrap/' + name + '.java'
              for part, names in [('main', ['FixedNativeCoverageProfile', 'FixedServiceExecArguments']),
                                  ('test', ['FixedNativeCoverageProfileTest', 'FixedServiceExecArgumentsTest'])] for name in names]
    manifest = {'classification': 'PROVISIONAL_SELECTED_NOT_FORMAL', 'headAtCollection': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip(),
                'dirtySource': True, 'command': 'bash tools/quality/vm/050_s1/pg470_profile_selected_v4.sh',
                'started': BASE.with_suffix('.started').read_text().strip(), 'completed': BASE.with_suffix('.completed').read_text().strip(),
                'actualExit': 0, 'PT': count, 'suites': len(xml), 'failed': 0, 'errors': 0, 'skipped': 0,
                'staticModulesZero': 3, 'JDK': '25.0.4', 'Maven': '3.9.12', 'OS': 'Ubuntu26.04',
                'sourceSha256': {p: sha(T / p) for p in files}, 'xml': xml, 'privateLogSha256': sha(BASE.with_suffix('.log')),
                'BUG': ['BUG-751'], 'YKT': ['YKT-531'], 'SSC': ['SSC-193'], 'coverage100': False,
                'execIsDevelopmentCumulative': True, 'formal': False, 'fullRegression': False, 'nativeConnection': False,
                'earlierNotAccepted': {'v1': 'no-tests exit1', 'v3': 'umask mismatch 1F exit1'},
                'rawSecretsExported': False}
    OUT.mkdir(parents=True)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'manifestSha256': sha(OUT / 'manifest.json'), 'PT': count, 'formal': False}))
if __name__ == '__main__':
    main()
