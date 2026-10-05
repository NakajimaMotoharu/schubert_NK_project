"""Fresh exact selected XML, static and independent policy coverage; not formal/native."""
import datetime
import hashlib
import json
import os
import pathlib
import re
import xml.etree.ElementTree as ET

os.umask(0o077)
tree = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
work = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
stem = work / 'pg472-web-health-selected-v3'
def read(suffix):
    return pathlib.Path(str(stem) + suffix).read_text().strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert read('.exit') == '0'
started = datetime.datetime.fromisoformat(read('.started')).timestamp()
log = read('.log')
assert '[INFO] BUILD SUCCESS' in log
assert log.count('BugInstance size is 0') == 5
assert log.count('No errors/warnings found') == 5
expected = {
    'protocol': {'MessageCodecTest': 7},
    'storage': {'ResourceScopeTest': 8, 'PrivateDirectoryEntryTest': 12},
    'bootstrap': {'FixedServiceIdentityTest': 10, 'ServiceCredentialSetTest': 5},
    'api': {'ApiProcessMainTest': 4},
    'web': {'WebProcessMainTest': 4, 'WebProcessLifetimeTest': 3,
            'WebNativeRuntimePartialTest': 3, 'WebRequestIdentityConsistencyTest': 1,
            'WebRuntimeHealthTest': 4},
}
modules = {}
for module, classes in expected.items():
    reports = tree / 'src' / ('schubert-nk-' + module) / 'target' / 'surefire-reports'
    selected = []
    for name, count in classes.items():
        matches = list(reports.glob('TEST-*.' + name + '.xml'))
        assert len(matches) == 1
        path = matches[0]
        assert path.stat().st_mtime >= started
        root = ET.parse(path).getroot()
        assert int(root.attrib['tests']) == count
        assert all(int(root.attrib[key]) == 0 for key in ['failures', 'errors', 'skipped'])
        cases = root.findall('testcase')
        assert len(cases) == count
        assert all(not any(case.find(tag) is not None for tag in ['failure', 'error', 'skipped']) for case in cases)
        selected.append({'class': root.attrib['name'], 'tests': count,
                         'xmlSha256': sha(path), 'methods': [case.attrib['name'] for case in cases]})
    modules[module] = {'tests': sum(classes.values()), 'suites': len(classes), 'F': 0, 'E': 0, 'S': 0, 'XML': selected}
coverage_path = tree / 'src/schubert-nk-web/target/site/jacoco/jacoco.xml'
assert coverage_path.stat().st_mtime >= started
coverage = ET.parse(coverage_path).getroot()
matches = coverage.findall(".//class[@name='dev/codex/schubert/nk/web/bootstrap/WebRuntimeHealth']")
assert len(matches) == 1
counters = {node.attrib['type']: {'missed': int(node.attrib['missed']), 'covered': int(node.attrib['covered'])}
            for node in matches[0].findall('counter')}
assert all(counters[k]['missed'] == 0 and counters[k]['covered'] > 0 for k in ['BRANCH','LINE','METHOD','CLASS'])
# Local class is asserted by four current independent tests, not by old native streams.
out = tree / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG472-web-health-selected-v3'
assert not out.exists()
out.mkdir(parents=True)
tests = list((tree / 'src/schubert-nk-web/src/test/java').rglob('Web*Test.java'))
tested_names = {'WebNativeRuntimePartialTest.java', 'WebRequestIdentityConsistencyTest.java', 'WebRuntimeHealthTest.java'}
tested = {str(path.relative_to(tree)): sha(path) for path in tests if path.name in tested_names}
assert len(tested) == 3
payload = {'id': 'PG472-web-health-selected-v3', 'programId': ['NK-OPS-001','NK-WEB-002'],
           'TestIDs': ['PT-OPS-NWEB-PART001..003', 'PT-WEB-IDENT-CONSIST001', 'PT-OPS-NWEB-HEALTH001..004'],
           'branch': 'dev-foundation', 'baseCommit': read('.source'), 'dirtySource': True,
           'sourceDiffSha256': sha(pathlib.Path(str(stem)+'.source-diff.private')),
           'selectedTestSha256': tested, 'sourceFrozenForFormal': False,
           'started': read('.started'), 'completed': read('.completed'),
           'command': 'bash tools/quality/vm/050_s1/pg472_web_health_selected_v3.sh',
           'actualExit': 0, 'modules': modules, 'tests': 61, 'suites': 11, 'F':0,'E':0,'S':0,
           'staticModules':5, 'staticFindings':0, 'NullAwayWerror':'PASS', 'format':'PASS',
           'environment': {'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','OS':'Linux host'},
           'independentOracle':'literal conditions/order/UUID/IOException identity; no production-generated expected',
           'localClassCounters':counters,'wholeCoverage100':False,'oldNativeReused':False,
           'priorV1':{'actualExit':1,'WebNewTests':'NOT_RUN','BUG':'BUG-758'},
           'priorV2':{'actualExit':0,'tests':57,'suites':10,'XML':'previously inspected; not rehashed after v3 overwrote XML',
                      'logSha256':sha(work/'pg472-web-partial-selected-v2.log')},
           'privateLogSha256':sha(pathlib.Path(str(stem)+'.log')),
           'coverageXMLSha256':sha(coverage_path),'BUG':['BUG-758'],'YKT':['YKT-538'],
           'PGD':['PG-D377'],'formalUpdated':False,'ITSTAccepted':False,'rawSecretsExported':False}
assert sum(m['tests'] for m in modules.values()) == 61
(out/'manifest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
manifest_hash = sha(out/'manifest.json')
result = tree/'evidence/01_PT/018_NK-OPS-001/355_NK-OPS-001_Web部分所有・health独立試験結果.md'
assert not result.exists()
result.write_text('# Web部分所有・health独立試験結果\n\n'
    + f"PG472-v3 actual0 / 61PT / 11suite / F/E/S=0、静的5module 0、NullAway/Werror/format PASS。実行開始 {payload['started']}、終了 {payload['completed']}。base {payload['baseCommit']} + 未commit PG-D377変更群（正式source固定前）。\n\n"
    + '354の部分所有/request独立4PT及びHEALTH001..004のliteral全10拒否・全正常・短絡順序・例外identityを確認。WebRuntimeHealthのline/method/class/branchは実report全miss0。ただしgroup reportはcleanなし・旧execも存在するため全体coverage合格へ加算しない。当classは新規で4PTにより全条件を実行し、旧nativeにも存在しない。PG471/native8結果を新source正式認定へ流用しない。\n\n'
    + 'v1 actual1(API selector欠落)・Web追加not-runを維持。BUG758/YKT538を起票後、API明示選択v2は57PT10suite/FES0/static5zero、v3も各module非零・全指定class/fresh XMLを確認。0件guardは緩めていない。\n\n'
    + f'環境 JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/Linux。command `{payload["command"]}`。safe manifest `evidence/provisional/PG472-web-health-selected-v3/manifest.json` SHA256 {manifest_hash}。private log/source/XML hashesをmanifestへ保存しraw credential/session/token/keyは出力0。\n\n'
    + '次は変更群source固定→fresh全6→同source接続/native及び残counter。正式PT-WEB-20260925-24/1964PT53scope/48.3%は据置。未実行/中断/別source/ITST合格宣言0。\n')
print(json.dumps({'tests':61,'suites':11,'staticModules':5,'healthCounters':counters,'manifestSha256':manifest_hash}))
