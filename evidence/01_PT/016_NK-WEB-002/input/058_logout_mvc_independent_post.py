"""Independent eight-case/normal-byte/source/method check; never invokes Product or Test."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as E
import zipfile

R = Path(__file__).resolve().parents[4]
RUNS = R.parent/'pgpt-runs/PG379'
OUT = R/'evidence/01_PT/016_NK-WEB-002/evidence/PG22204-logout-mvc-eight-independent-post-v1'
SOURCE = 'a654a317a99ab16d531cacd03a2f45202bb00aa2'
CORE = '7aed8eace7c844c2f79f2e39db766faf914890d5'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_bytes())
P = 'dev/codex/schubert/nk/web/'


def methods(path):
    return {node.get('name'): {(m.get('name'),m.get('desc')) for m in node.findall('method')
                             if any(int(c.get('covered')) > 0 for c in m.findall('counter'))}
            for node in E.parse(path).getroot().findall('.//package/class')
            if any(int(c.get('covered')) > 0 for m in node.findall('method') for c in m.findall('counter'))}


def main():
    assert not OUT.exists()
    u = RUNS/'pg22200-logout-business-mvc-eight-unit-v1'
    m = load(u/'manifest.json')
    assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped']) == (0,8,0,0,0)
    b = m['begin']
    assert b['source'] == SOURCE and b['normalSource'] == CORE
    assert b['newMethods'] == 2 and b['existingMethodsSourceRequalification'] == 6
    for path,h in b['inputHashes'].items():
        assert sha(R/path) == h == hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=R)).hexdigest()
    normal_path = RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json'
    assert sha(normal_path) == b['normalManifestSha256'] == 'b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27'
    normal = load(normal_path)
    assert normal['actualExit'] == 0 and normal['source'] == CORE
    for module in ['protocol','storage','web']:
        assert sha(normal['jars'][module]['path']) == normal['jars'][module]['sha256']
    for path,h in b['dependencies'].items():
        assert sha(path) == h
        assert not any(x in path for x in ['/schubert-nk-api/','/schubert-nk-bootstrap/','/schubert-nk-batch/', '/postgresql/','/artemis-','/playwright/'])
    compiled = load(RUNS/'pg22196-logout-business-mvc-eight-compile-v1/manifest.json')
    assert compiled['actualExit'] == 0 and compiled['inputHashes'] == b['inputHashes']
    for name,h in compiled['classes'].items():
        assert sha(RUNS/'pg22196-logout-business-mvc-eight-compile-v1/classes'/name) == h
    unit_command = m['stages']['unit']['command']
    assert '-Dfile.encoding=UTF-8' in unit_command and '--scan-classpath' not in unit_command
    assert unit_command.count('--select-class') == 2
    assert all(not stage['timedOut'] and stage['actualExit'] == 0 and
               sha(u/(key+'.stdout')) == stage['stdoutSha256'] and
               sha(u/(key+'.stderr')) == stage['stderrSha256'] for key,stage in m['stages'].items())
    tests = {
      'dev.codex.schubert.nk.web.config.BusinessMvcBeanPortTest': 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/config/BusinessMvcBeanPortTest.java',
      'dev.codex.schubert.nk.web.revocation.LogoutMvcBeanPortTest': 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/revocation/LogoutMvcBeanPortTest.java',
    }
    expected = {(name,method+'()') for name,path in tests.items()
                for method in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/path).read_text())}
    assert len(expected) == 8
    xml_cases = []
    xml_environment = {}
    for path in sorted((u/'xml').glob('TEST-*.xml')):
        root = E.parse(path).getroot()
        for case in root.findall('testcase'):
            assert not case.findall('failure') and not case.findall('error') and not case.findall('skipped')
            xml_cases.append((case.get('classname'),case.get('name')))
        for prop in root.findall('./properties/property'):
            if prop.get('name') in ['java.version','java.vendor','os.name','os.arch','file.encoding','user.timezone']:
                xml_environment[prop.get('name')] = prop.get('value')
    assert len(xml_cases) == len(set(xml_cases)) == 8 and set(xml_cases) == expected
    assert {(x['classname'],x['name']) for x in m['cases']} == expected
    assert sum(name.endswith('LogoutMvcBeanPortTest') for name,_ in expected) == 2
    target_names = {P+'config/'+v for v in ['NotificationBusinessMvcConfiguration', 'UserBusinessMvcConfiguration', 'QuestionAcceptanceMvcConfiguration','LogoutMvcConfiguration']}
    assert set(m['physical']) == target_names
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        assert {n[:-6] for n in jar.namelist() if n.endswith('.class') and n[:-6] in target_names} == target_names
        for name,h in m['physical'].items():
            assert hashlib.sha256(jar.read(name+'.class')).hexdigest() == h == sha(u/'component'/(name+'.class'))
    coverage_root = E.parse(u/'coverage.xml').getroot()
    counters = {x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in coverage_root.findall('counter')}
    assert {k:counters[k] for k in ['LINE','METHOD','CLASS']} == {
        'LINE':dict(covered=8,missed=0),'METHOD':dict(covered=8,missed=0),'CLASS':dict(covered=4,missed=0)}
    assert 'BRANCH' not in counters and all(v['missed'] == 0 for v in counters.values())
    per_class = {x.get('name'):{v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in x.findall('counter')} for x in coverage_root.findall('.//package/class')}
    assert set(per_class) == target_names and all('BRANCH' not in v for v in per_class.values())
    ex = (u/'execinfo.stdout').read_text()
    ids = dict((name,crc) for crc,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(u/'classinfo.stdout').read_text()))
    assert set(ids) == target_names and ex.count('Session "') == 1 and 'Session "PG22200-LOGOUT-BUSINESS-MVC8"' in ex
    raw_probes = {}
    for name,crc in ids.items():
        row = re.search(r'^'+crc+r'\s+(\d+) of\s+(\d+)\s+'+re.escape(name)+r'$',ex,re.M)
        assert row and row[1] == row[2]
        raw_probes[name] = dict(hit=int(row[1]),total=int(row[2]))
    pre = load(R/'evidence/01_PT/016_NK-WEB-002/input/057_logout_mvc_preunit_contract.json')
    assert pre['actualExit'] == 0 and pre['mainSource'] == CORE
    witness = RUNS/'pg22202-logout-mvc-main-method-witness-v1'
    for filename in ['terminal.json','format-terminal.json']:
        stage = load(witness/filename)
        assert stage['actualExit'] == 0 and not stage['timedOut']
    actual = methods(witness/'all-web-methods.xml')
    allowed = {name:{(v['name'],v['desc']) for v in rows} for name,rows in pre['priorExecutedMethods'].items()}
    def desc(*args, result='V'):
        return '('+''.join('L'+P+x+';' if not x.startswith('java/') else 'L'+x+';' for x in args)+')'+result
    prior_unit = R/'evidence/01_PT/016_NK-WEB-002/evidence/PG21658-business-mvc-six-v1'
    old_manifest = load(prior_unit/'manifest.json')
    assert sha(prior_unit/'coverage.xml') == old_manifest['files']['coverage.xml']
    prior_target_methods = methods(prior_unit/'coverage.xml')
    for simple in ['NotificationBusinessMvcConfiguration','UserBusinessMvcConfiguration','QuestionAcceptanceMvcConfiguration']:
        name=P+'config/'+simple
        assert m['physical'][name] == old_manifest['physicalHashes'][name]
        allowed[name] = prior_target_methods[name]
    # New exact signatures come from the pre-execution public API/source review, not test results.
    allowed.update({
      P+'config/LogoutMvcConfiguration': {('<init>','()V'),('logoutController',desc('security/LocalLogoutHandler',result='L'+P+'controller/LogoutController;'))},
      P+'controller/LogoutController': {('<init>',desc('security/LocalLogoutHandler'))},
      P+'security/LocalLogoutHandler': {('<init>',desc('session/SpringEncryptedSessionRepository','revocation/LocalLogoutCoordinator','logging/WebSecurityAudit'))},
      P+'revocation/LocalLogoutCoordinator': {('<init>',desc('session/EncryptedWebSessionRepository','revocation/RevocationPayloadCodec','messaging/LogoutWireClient','java/time/Clock'))},
      P+'messaging/LogoutWireClient': {('<init>',desc('messaging/JmsRequestReplyClient','messaging/JmsRequestSender','java/time/Clock','java/util/function/Supplier','java/time/Duration'))},
      P+'revocation/RevocationPayloadCodec': {('<init>','(Ljava/lang/String;[BLjava/lang/String;[BLjava/security/SecureRandom;)V'),('validateKey','([B)V'),('close','()V'),('<clinit>','()V')},
      P+'revocation/EncryptedRevocationPayload': {('validateVersion','(Ljava/lang/String;)Ljava/lang/String;')},
    })
    assert len(actual) == len(allowed) == 31 and actual == allowed
    init = set(re.findall(r"Initializing '([^']+)",(u/'class-init.log').read_text()))
    prefixes = [P+'config/BusinessMvcBeanPortTest',P+'session/BusinessMvcOwnerPortFixture',P+'revocation/LogoutMvcBeanPortTest']
    assert not {n for n in init if n.startswith('dev/codex/schubert/nk/') and n not in allowed and not any(n.startswith(v) for v in prefixes)}
    forbidden = ['dev/codex/schubert/nk/api/', 'dev/codex/schubert/nk/bootstrap/', 'dev/codex/schubert/nk/storage/', P+'bootstrap/WebStartupException', P+'config/WebMvcConfiguration','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','org/springframework/security/core/context/SecurityContextHolder','java/net/Socket','sun/nio/ch/SocketChannelImpl']
    assert not any(n.startswith(tuple(forbidden)) for n in init)
    for name in ['dev/codex/schubert/nk/api/error/TemporaryInfrastructureException',P+'bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec']:
        assert not re.search(r'^\w+\s+[1-9]\d* of\s+\d+\s+'+re.escape(name)+r'$',ex,re.M)
    classification_path = R/'evidence/01_PT/016_NK-WEB-002/evidence/PG22198-logout-business-mvc-eight-static-v1/manifest.json'
    static = load(classification_path)
    assert static['inputHashes'] == b['inputHashes'] and static['rawPmdExit'] == 4 and static['pmdRaw'] == 1
    assert static['applicableViolations'] == static['checkstyle'] == static['spotbugs'] == static['processingErrors'] == 0
    assert all(v['classification'] == 'NOT_APPLICABLE' and v['reason'] for v in static['individualClassifications'])
    assert sha(static['staticManifest']['path']) == static['staticManifest']['sha256']
    raw_static = load(static['staticManifest']['path'])
    assert all(sha(v['path']) == v['sha256'] for v in raw_static['reports'].values())
    # Same original compile/current normal; read-only method and normal hash metadata, no old exec union.
    OUT.mkdir()
    files = {}
    for path in [*u.iterdir(),*sorted((u/'xml').glob('TEST-*.xml'))]:
        if path.is_file():
            name = 'original-manifest.json' if path.name == 'manifest.json' else 'original-class-init.stdout' if path.name == 'class-init.log' else path.name
            assert name not in files
            shutil.copyfile(path,OUT/name)
            files[name] = sha(OUT/name)
    executed = {name:[dict(name=a,desc=b) for a,b in sorted(v)] for name,v in actual.items()}
    (OUT/'executed-main-methods.json').write_text(json.dumps(executed,indent=2)+'\n')
    files['executed-main-methods.json'] = sha(OUT/'executed-main-methods.json')
    result = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=SOURCE,
                  productionCoreMain=CORE,tests=8,newUniqueTests=2,requalifiedExistingTests=6,
                  failures=0,errors=0,skipped=0,sourceProofNew=1,sourceProofRetained=3,
                  normalCompileManifest=dict(path=str(normal_path),sha256=sha(normal_path)),
                  inputHashes=b['inputHashes'],physical=m['physical'],classIds=ids,coverage=per_class,
                  counters=counters,branchStatus='NATURAL_ZERO_BRANCH',branchRatio=None,
                  rawProbes=raw_probes,session='PG22200-LOGOUT-BUSINESS-MVC8',singleExecSha256=sha(u/'jacoco.exec'),
                  sourceMethods=sorted(expected),environment=xml_environment,dependencies=b['dependencies'],
                  passiveMethodReport=dict(path=str(witness/'all-web-methods.xml'),sha256=sha(witness/'all-web-methods.xml')),
                  executedMainClasses=31,supportWholeSourceCredit=0,heldFourInitialisations=0,
                  staticClassification=dict(path=str(classification_path.relative_to(R)),sha256=sha(classification_path)),
                  mainByteOrBusinessSpecificationChanged=False,realSessionOrWireOrDbOrCryptoOperation=False,
                  manualExclusions=[],oldExecCombined=False,newAcceptance=0,formalUpdated=False,
                  whole451Accepted=False,effortRate=None,files=files,
                  verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__)),
                                source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,tests=8,newUniqueTests=2,newSourceProofs=1,manifestSha256=sha(OUT/'manifest.json'))))


if __name__ == '__main__':
    main()
