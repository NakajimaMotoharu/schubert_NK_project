"""Independent post-run sealing and identical-production-byte native diagnostic, not formal gate."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import xml.etree.ElementTree as ET
import zipfile

T = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
J = pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    run = W / 'pg585-access-reactor-v3'
    source = (run / 'source').read_text().strip()
    assert source == 'f820710d1a274530418a389e5dcb755441356dd0' and (run / 'exit').read_bytes() == b'0\n'
    assert subprocess.run(['sha256sum', '--check', '--status', str(run / 'source-files.sha256')], cwd=T).returncode == 0
    start = datetime.datetime.fromisoformat((run / 'started').read_text().strip()).timestamp()
    end = datetime.datetime.fromisoformat((run / 'completed').read_text().strip()).timestamp()
    log = (run / 'build.private.log').read_text()
    assert 'BUILD SUCCESS' in log and log.count('BugInstance size is 0') == 6 and log.count('No errors/warnings found') == 6
    modules = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
    results = {};total_classes = 0
    for module in modules:
        base = run / module
        current = T / 'src' / ('schubert-nk-' + module) / 'target'
        jar = 'schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar'
        with zipfile.ZipFile(base / jar) as fresh, zipfile.ZipFile(W / 'pg540-six-host-v1' / module / jar) as old:
            a = {n:fresh.read(n) for n in fresh.namelist() if n.endswith('.class')}
            b = {n:old.read(n) for n in old.namelist() if n.endswith('.class')}
            assert len(a) > 0 and a == b
            total_classes += len(a)
        reports = list((base / 'surefire-reports').glob('TEST-*.xml'));assert reports
        totals = {k:0 for k in ('tests', 'failures', 'errors', 'skipped')};hashes = {}
        for p in reports:
            original = current / 'surefire-reports' / p.name
            assert sha(p) == sha(original) and start <= original.stat().st_mtime <= end + 1
            suite = ET.parse(p).getroot();cases = suite.findall('testcase')
            assert len(cases) == int(suite.attrib['tests']) > 0
            assert all(not any(c.find(k) is not None for k in ('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')) for c in cases)
            for k in totals:totals[k] += int(suite.attrib[k])
            hashes[p.name] = sha(p)
        assert sum(totals[k] for k in ('failures','errors','skipped')) == 0
        static = base / 'spotbugsXml.xml';assert not ET.parse(static).getroot().findall('.//BugInstance')
        xml = base / 'jacoco.xml';assert sha(xml) == sha(current / 'site/jacoco/jacoco.xml')
        doc = ET.parse(xml).getroot()
        counters = {c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])} for c in doc.findall('counter')}
        results[module] = {'tests':totals['tests'],'suites':len(reports),'FES':0,'staticIssues':0,'hostCounters':counters,
                           'allMainClassBytesEqualProduction969':True,'xmlHashes':hashes,'execSha256':sha(base/'jacoco.exec'),
                           'jarSha256':sha(base/jar),'coverageXmlSha256':sha(xml),'staticXmlSha256':sha(static)}
    specific = ET.parse(run / 'batch/surefire-reports/TEST-dev.codex.schubert.nk.batch.repository.MorningDatabaseAccessContractTest.xml').getroot()
    assert int(specific.attrib['tests']) == 4
    cp = [str(W / 'pg571-current-ten-native-v2/classes')]
    repo = pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar',
                    'org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths = list(repo.glob(pattern));assert len(paths) == 1;cp.append(str(paths[0]))
    cohort = W / 'pg581-current-eighteen-native-v3';assert sha(cohort/'manifest.safe.json') == 'f7824086cf30e00f246deeb9cf5c3456a1408b34032a0f4f44a7a3151032f5c8'
    eighteen = json.loads((cohort/'manifest.safe.json').read_bytes())
    prior = W / 'pg561-current-native-v2';nine = json.loads((prior/'manifest.safe.json').read_bytes())
    data = [run/m/'jacoco.exec' for m in modules]
    for i,v in enumerate(nine['currentNativeFiles']):
        p=prior/(str(i)+'.exec');assert sha(p)==v['sha256'];data.append(p)
    boot=W/'pg571-current-ten-native-v2/bootstrap.exec';assert sha(boot)=='0f8869c6ef5e43f9ce858bf08a7da0cc161dc51b329b2209ef62a5092ed1ad9e';data.append(boot)
    for i,v in enumerate(eighteen['newFiles']):
        p=cohort/(str(i)+'.exec');assert sha(p)==v['sha256'];data.append(p)
    assert len(data)==24
    native={};gains={}
    for module in modules:
        r=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverage',str(run/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')),
                          *[str(p) for p in data]],capture_output=True,timeout=45)
        assert r.returncode==0 and not r.stderr
        counters=json.loads(r.stdout);assert counters['classByteMismatch']==0;native[module]=counters
        gains[module]={k:eighteen['moduleCounters'][module][k]['missed']-counters[k]['missed'] for k in ('LINE','METHOD','CLASS','BRANCH')}
    result={'run':'PG585-access-reactor-v3','actualExit':0,'operatorSource':source,'productionSource':'969d8ded10c0bf5841d9e3a5c531e922caf4a24a',
            'started':(run/'started').read_text().strip(),'completed':(run/'completed').read_text().strip(),'elapsedSeconds':end-start,
            'tests':sum(v['tests'] for v in results.values()),'suites':sum(v['suites'] for v in results.values()),'newAccessTests':4,
            'FESFlakyNotRun':0,'staticModules':6,'staticIssues':0,'allMainClassesByteEqual':total_classes,'moduleResults':results,
            'sameByteNativeStreams':18,'nativeDiagnosticCounters':native,'gainsVsPG581':gains,
            'global100':all(v[k]['missed']==0 for v in native.values() for k in ('LINE','METHOD','CLASS','BRANCH')),
            'formalAccepted':False,'logSha256':sha(run/'build.private.log'),'sourceFilesSha256':sha(run/'source-files.sha256'),
            'collectorSourceSha256':sha(pathlib.Path(__file__)),'collectorMode':'POST_RUN_INDEPENDENT_SHA_NOT_MAVEN_SOURCE','rawExported':False}
    with (run/'manifest.safe.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'tests':result['tests'],'suites':result['suites'],'staticIssues':0,'productionMainByteDiff':0,
                      'gains':{k:sum(v[k] for v in gains.values())for k in ('LINE','METHOD','CLASS','BRANCH')},
                      'remaining':{k:sum(v[k]['missed']for v in native.values())for k in ('LINE','METHOD','CLASS','BRANCH')},
                      'manifestSha256':sha(run/'manifest.safe.json'),'formalAccepted':False}))


if __name__ == '__main__':
    main()
