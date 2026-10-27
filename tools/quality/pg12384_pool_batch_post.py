"""Independent actual38 XML/CRC/all-Main/physical Test and complete API-Web counter measurement; no replay."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from coverage_session_schema import parse as parse_session, selftest
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from classfile_code_metadata import decode
from pg10902_web_boundary_post import require_package_metadata
import pg9346_direct_companion_jdk_post as steps

SOURCE = '14198cb1878ec73319511ba1067133992d335e63'
NORMAL_SHA='27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75'
HOST_SHA='d12e56ad21684f4c31b690880763c69db7744be141228db54119ce0dcf71c12f'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg12380-pool-batch-host-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg12384-pool-batch-post-v1'
OUT = data.BASE/'PG12384-pool-batch-post-v1'


def valid_run(value):
    if value['source'] != SOURCE or value['actualExit'] != 0 or value['observedTestExecutions'] != 38:
        raise ValueError('one actual38-method current-source run')
    if value['oldExecUnion'] or value['whole451Accepted'] or value['newAccepted'] != 0:
        raise ValueError('no union or formal credit')


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    host_path = data.BASE/'PG12380-pool-batch-host-v1/manifest.json'
    host = data.read_checked(host_path,HOST_SHA)
    normal = data.read_checked(data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json',NORMAL_SHA)
    previous = data.read_checked(data.BASE/'PG12352-pool-capacity-six-compile-v1/manifest.json',
        '5b954538ef967b5ced149c9f0b4f3b11a15e88676e07c2ea56c22215e9a1e0b0')
    valid_run(host)
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    prepared = host['begin']
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in prepared['sourceInputHashes'].items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**prepared['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert data.sha(Path(prepared['helperPath']).read_bytes()) == prepared['helperSha256']
    resource = prepared['independentCatalogResource']
    assert data.sha(Path(resource['classPathOutput']).read_bytes()) == resource['sha256'] == prepared['sourceInputHashes'][resource['path']]
    expected = Counter((r['className'],r['method']) for r in prepared['cases'])
    observed,xmls = [],{}
    for file in (RUN/'xml').glob('TEST-*.xml'):
        root = ET.parse(file).getroot()
        assert all(root.get(k) == '0' for k in ('failures','errors','skipped'))
        assert int(root.get('tests')) == dict(DbPoolMetricCollectorTest=8,WebDbPoolMetricCollectorTest=8,TransferMetricRecorderTest=8,MonitoringRetentionConfigurationTest=8,MetricContractTest=6)[root.get('name').rpartition('.')[2]] and all(not list(c) for c in root.findall('testcase'))
        observed.extend((c.get('classname'),c.get('name')) for c in root.findall('testcase'))
        xmls[file.name] = data.sha(file.read_bytes())
    assert len(xmls) == 5 and Counter(observed) == expected and xmls == host['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=38;started=38;succeeded=38;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == host['execSha256']
    loaded_raw = (RUN/'classload-metadata.log').read_bytes()
    assert data.sha(loaded_raw) == host['classloadSha256']
    loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loaded_raw.decode()))
    permitted=tuple(p.split('/java/',1)[1][:-5].replace('/','.') for p in prepared['eligibilityClosureSourceHashes'])+tuple(r['className'] for r in prepared['cases'])+tuple(p.split('/java/',1)[1][:-5].replace('/','.') for p in prepared['supportingFixtureSourceHashes'])
    forbidden=[n for n in loaded if (n.startswith('dev.codex.schubert.nk.') and not n.startswith(permitted)) or n.startswith('org.postgresql.')]
    assert loaded and not forbidden
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test,new_test = test_classes(previous),test_classes(normal)
    assert set(old_test) == set(new_test) and len(new_test) == 1962
    changed = [k for k in new_test if new_test[k] != old_test[k]]
    assert 0 < len(changed) < len(new_test)
    assert {decode((Path(normal['jars'][module]['path']).parent/'test-classes'/entry).read_bytes(),entry)['sourceFile']
        for module,entry in changed} == {'DbPoolMetricCollectorTest.java','WebDbPoolMetricCollectorTest.java','TransferMetricRecorderTest.java','MonitoringRetentionConfigurationTest.java','MetricContractTest.java'}
    static_path = data.BASE/'PG12382-pool-batch-static-v1/manifest.json'
    static = data.read_checked(static_path,'ef847e28425796fadd1e804a7367c5f4fca93da901c84a8ea544838b0e277d5e')
    assert static['source'] == SOURCE and static['reports']['pmd']['findings'] == 26 and static['reports']['checkstyle']['findings'] == 0
    assert all(v['processingErrors'] == 0 for v in static['reports'].values())
    for label,value in static['reports'].items():
        assert data.sha((static_path.parent/(label+'.xml')).read_bytes()) == value['sha256']
    nodes = [n for n in ET.parse(static_path.parent/'pmd.xml').getroot().iter() if n.tag.rpartition('}')[2] == 'violation']
    assert len(nodes) == 26 and Counter(n.get('rule') for n in nodes) == Counter(DoNotUseThreads=22,CloseResource=1,CompareObjectsWithEquals=2,EqualsNull=1)
    SLOT.mkdir(mode=0o700)
    helper = data.ROOT/'tools/quality/architecture/PoolBatchFixtureArtifactCoverageMeasure.java'
    tc = data.ROOT.parent/'toolchain'
    libs = [tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    tool_hashes = {str(p):data.sha(p.read_bytes()) for p in [helper,*libs]}
    reader = SLOT/'reader'
    reader.mkdir()
    cp = os.pathsep.join(map(str,libs))
    steps.SLOT = SLOT
    stages = [steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    measurements = {}
    for role in ('api','web','batch'):
        classes = SLOT/('complete-'+role+'-main')
        classes.mkdir()
        with zipfile.ZipFile(prepared['moduleJars'][role]) as jar:
            main = {n:data.sha(jar.read(n)) for n in jar.namelist() if n.endswith('.class')}
            assert len(main) == {'api':467,'web':358,'batch':645}[role]
            for name in main:
                file = classes/name
                file.parent.mkdir(parents=True,exist_ok=True)
                with file.open('xb') as stream:
                    stream.write(jar.read(name))
        catalog = SLOT/('complete-'+role+'-main-catalog.txt')
        with catalog.open('x') as stream:
            stream.write(''.join(n+'\n' for n in sorted(main)))
        stages.append(steps.step('measure-'+role,[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,
            str(RUN/'jacoco.exec'),str(classes),str(catalog),host['sessionId'],role]))
        assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
        lines = (SLOT/('measure-'+role+'.stdout')).read_text().splitlines()
        session = parse_session(lines[0].split('\t'),host['sessionId'])
        assert lines[1] == 'FORBIDDEN_PROBE_HITS\t0'
        units,packages,bundle,current = {},{},None,None
        for line in lines[2:]:
            parts = line.split('\t')
            if parts[0] == 'PACKAGE_METADATA_ONLY':
                name = parts[1]+'.class'
                model = decode((classes/name).read_bytes(),name)
                require_package_metadata(name,model)
                assert name in main and name not in packages
                packages[name] = dict(sha256=main[name],model=model)
            elif parts[0] == 'CLASS':
                name = parts[1]+'.class'
                assert name in main and name not in units
                current = dict(classCrc64=parts[2],counters={})
                units[name] = current
            elif parts[0] == 'BUNDLE':
                assert parts == ['BUNDLE','COMPLETE_'+role.upper()+'_ARTIFACT'] and bundle is None
                bundle = {}
                current = dict(counters=bundle)
            else:
                assert len(parts) == 4 and parts[0] == 'COUNTER' and current is not None
                _,kind,missed,covered = parts
                assert kind not in current['counters']
                current['counters'][kind] = dict(missed=int(missed),covered=int(covered))
        assert set(units)|set(packages) == set(main) and not set(units)&set(packages)
        assert set(bundle) == {'LINE','METHOD','CLASS','BRANCH'}
        for kind in ('METHOD','CLASS','BRANCH'):
            assert all(sum(u['counters'][kind][k] for u in units.values()) == bundle[kind][k] for k in ('missed','covered'))

        target_stems={'api':{'DbPoolMetricCollector','DbPoolMetricObservation','DbPoolMetricRecorder'},'web':{'WebDbPoolMetricCollector','WebDbPoolMetricObservation','WebDbPoolMetricRecorder'},'batch':{'TransferMetricRecorder','MonitoringModePolicy','MetricContract'}}[role]
        target_units={p:v for p,v in units.items() if p.rpartition('/')[2][:-6].split('$',1)[0] in target_stems}
        assert len(target_units)=={'api':5,'web':5,'batch':9}[role]
        measurements[role] = dict(session=session,units=units,packageMetadata=packages,bundleCounters=bundle,selectedValueMain=target_units,
            completeClasses=len(main),analyzedClasses=len(units),nonExecutablePackageMetadata=len(packages),
            selectedValueFourCounters100=all(c['missed']==0 for u in target_units.values() for c in u['counters'].values()) and all(sum(u['counters'][kind]['covered'] for u in target_units.values())>0 for kind in ('LINE','METHOD','CLASS','BRANCH')),
            zeroDenominatorCountersAreNA=True,
            wholeArtifactCoverage100=all(v['missed']==0 for v in bundle.values()))
    assert len(measurements) == 3
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in tool_hashes.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in prepared['sourceInputHashes'].items())
    schema_vectors = selftest()
    negatives = 0
    for key,value in [('source','old'),('actualExit',1),('observedTestExecutions',43),('oldExecUnion',True),('whole451Accepted',True),('newAccepted',1)]:
        bad = dict(host)
        bad[key] = value
        try:
            valid_run(bad)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('invalid current run accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'measurement.json',measurements)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,originalHostManifestSha256=data.sha(host_path.read_bytes()),
        staticManifestSha256=data.sha(static_path.read_bytes()),measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),stages=stages,
        productTestsExecutedByPost=0,originalObservedTestExecutions=38,metadataNegativeVectors=negatives,sessionSchemaVectors=schema_vectors,
        artifactMeasurements={role:{k:v for k,v in value.items() if k not in ('units','packageMetadata')} for role,value in measurements.items()},
        allMainClassesUnchanged=1843,otherTestClassesUnchanged=len(new_test)-len(changed),testClassesChanged=len(changed),rawStatic=26,duplicateLiteralsRemaining=0,
        remainingRawApplicability='RAW26_FAKE_PROVIDERS_THREAD_RECORD_IDENTITY_RESOURCE_CONTEXTS_CURRENT_WHOLE_PENDING',
        whole451Accepted=False,newAccepted=0,oldExecUnion=False,externalActions=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,artifactMeasurements={role:{k:v for k,v in value.items() if k not in ('units','packageMetadata')} for role,value in measurements.items()},manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))



if __name__ == '__main__':
    main()
