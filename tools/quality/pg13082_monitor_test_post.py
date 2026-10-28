"""Independent XML/class/source/whole-artifact counters; no Product PT replay."""
from collections import Counter
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts as class_parts, selftest
import pg9346_direct_companion_jdk_post as steps

SOURCE = '42ae92a74d57a9e1d031613d5b558af3ebe2925c'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13082-monitor-test-post-v1'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13078-monitor-test-host-v1'
OUT = data.BASE/'PG13082-monitor-test-post-v1'
COUNTS = {'api':467, 'web':358, 'batch':645, 'protocol':176, 'storage':80, 'bootstrap':117}

def main():
    invocation = capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13076-monitor-test-six-compile-v1/manifest.json', '77020a553a53f8c09d498899dbb3e5844121dc67023862901fa7ad82b12c1932')
    h = data.read_checked(data.BASE/'PG13078-monitor-test-host-v1/manifest.json', '28f76d37bfd46dd38535f7418aafc31046fa3e40697956d85d9951d537cbdd6d')
    s = data.read_checked(data.BASE/'PG13080-monitor-test-static-v1/manifest.json', '8dd2ba543269195d0e4479ea48e8a55cfb846acac98c3d413dc3b56729ad8732')
    plan = data.read_checked(data.BASE/'PG13074-monitor-test-plan-v1/manifest.json', '26c3c4fd22d61e6bd8dc26ddbf4c47baee7b98c3963352123a0fac1d80f88a09')
    old = data.read_checked(data.BASE/'PG13056-time-header-six-compile-v1/manifest.json', 'fa52be739663760cd603ff1e00bdf963499c75038c6fac9504ab6caa92a007f6')
    assert n['source'] == h['source'] == s['source'] == plan['source'] == SOURCE
    assert n['actualExit'] == n['testsExecuted'] == h['actualExit'] == 0 and s['actualExit'] == 1
    assert h['observedTestExecutions'] == 81 and not h['oldExecUnion']
    assert not any(value['timedOut'] for value in s['stages'].values())
    assert s['stages']['pmd']['actualExit'] == 4
    assert all(row['actualExit'] == 0 and not row['timedOut'] for row in h['stages'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes()) == digest for p,digest in {**h['begin']['dependencyHashes'], **h['begin']['physicalTestFiles']}.items())
    actual = []; xmls = {}
    for p in (RUN/'xml').glob('TEST-*.xml'):
        node = ET.parse(p).getroot()
        assert all(node.get(k) == '0' for k in ['failures','errors','skipped'])
        assert all(not list(row) for row in node.findall('testcase'))
        actual.extend((row.get('classname'),row.get('name')) for row in node.findall('testcase'))
        xmls[p.name] = data.sha(p.read_bytes())
    assert len(xmls) == 10 and len(actual) == 81 and Counter(actual) == Counter((r['className'],r['method']) for r in plan['cases'])
    assert xmls == h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=81;started=81;succeeded=81;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == h['execSha256']
    raw = (RUN/'classload-metadata.log').read_bytes(); assert data.sha(raw) == h['classloadSha256']
    loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:', raw.decode()))
    roots = {p.split('/java/',1)[1][:-5].replace('/','.') for p in [*plan['eligibilityClosureSourceHashes'],*plan['wholeTestSourceHashes'],*plan['supportTestSourceHashes']]}
    assert len(roots) == 29
    assert not [x for x in loaded if x.startswith('dev.codex.schubert.nk.') and not any(x == root or x.startswith(root+'$') for root in roots) and not x.endswith('.package-info')]
    assert not [x for x in loaded if x.startswith(('org.postgresql.','org.apache.activemq.','jakarta.jms.'))]
    assert jar_classes(old) == jar_classes(n) and len(jar_classes(n)) == 1843
    a,b = test_classes(old),test_classes(n)
    assert len(a) == len(b) == 1972 and set(a) == set(b)
    required = {('batch',path.split('/java/',1)[1][:-5]+'.class') for path in plan['wholeTestSourceHashes']}
    changed = {key for key in a if a[key] != b[key]}; assert required <= changed
    optional = {('batch','dev/codex/schubert/nk/batch/monitoring/TransferHealthMonitorTest$Registry.class')}
    assert changed-required <= optional
    allowed_source_files = {Path(path).name for path in plan['wholeTestSourceHashes']}
    changed_metadata = {}
    for role,entry in sorted(changed):
        left = class_parts((Path(old['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        right = class_parts((Path(n['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert role == 'batch' and left['model']['sourceFile'] == right['model']['sourceFile'] and right['model']['sourceFile'] in allowed_source_files
        debug_only = False
        if (role,entry) not in required:
            assert left['model'] == right['model'] and left['rawCodeRepresentationSha256'] == right['rawCodeRepresentationSha256']
            assert left['debugTablesSha256'] != right['debugTablesSha256']; debug_only = True
        changed_metadata[entry] = dict(sourceFile=right['model']['sourceFile'],oldSha256=a[(role,entry)],newSha256=b[(role,entry)],old=left,new=right,extraSourceLineDebugOnly=debug_only)
    unchanged_tests = len(a)-len(changed)
    metadata_vectors = selftest()
    findings = []
    for label,tag,count in [('pmd','violation',20),('checkstyle','error',0)]:
        p = data.BASE/'PG13080-monitor-test-static-v1'/(label+'.xml')
        assert data.sha(p.read_bytes()) == s['reports'][label]['sha256']
        nodes = [x for x in ET.parse(p).getroot().iter() if x.tag.rpartition('}')[2] == tag]
        assert len(nodes) == count and s['reports'][label]['processingErrors'] == 0
        if label == 'pmd':
            assert {x.get('rule') for x in nodes} == {'DoNotUseThreads'}
            findings = [dict(rule=x.get('rule'),beginline=int(x.get('beginline')),endline=int(x.get('endline')),attributes=dict(x.attrib)) for x in nodes]
    assert s['spotbugsSixExit'] == 0 and all(v['actualExit'] == 0 and not v['timedOut'] for k,v in s['stages'].items() if k != 'pmd')
    SLOT.mkdir(); reader = SLOT/'reader'; reader.mkdir(); steps.SLOT = SLOT; tc = data.ROOT.parent/'toolchain'
    helper = data.ROOT/'tools/quality/architecture/MonitorTestNamesArtifactCoverageMeasure.java'
    libraries = [tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar', *[tc/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ['asm','asm-tree','asm-commons']]]
    toolhashes = {str(p):data.sha(p.read_bytes()) for p in [helper,*libraries]}
    cp = os.pathsep.join(map(str,libraries))
    stages = [steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    measurements = {}
    for role,count in COUNTS.items():
        classes = SLOT/('complete-'+role+'-main'); classes.mkdir()
        with zipfile.ZipFile(n['jars'][role]['path']) as jar:
            physical = {name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')}
            assert len(physical) == count
            for name in physical:
                target = classes/name; target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream: stream.write(jar.read(name))
        catalog = SLOT/('complete-'+role+'-main-catalog.txt')
        with catalog.open('x') as stream: stream.write(''.join(name+'\n' for name in sorted(physical)))
        stages.append(steps.step('measure-'+role,[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes),str(catalog),h['sessionId'],role]))
        assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
        lines = (SLOT/('measure-'+role+'.stdout')).read_text().splitlines()
        assert lines[0].startswith('SESSION\t'+h['sessionId']+'\t') and lines[1] == 'FORBIDDEN_PROBE_HITS\t0'
        units = {}; packages = []; bundle = None; cursor = None; methods = {}
        for line in lines[2:]:
            f = line.split('\t')
            if f[0] == 'PACKAGE_METADATA_ONLY': packages.append(f[1]+'.class')
            elif f[0] == 'CLASS':
                name = f[1]+'.class'; assert name not in units
                cursor = dict(classCrc64=f[2],counters={}); units[name] = cursor
            elif f[0] == 'METHOD_DETAIL':
                key = f[1]+f[2]; assert key not in methods
                cursor = dict(counters={}); methods[key] = cursor
            elif f[0] == 'BUNDLE':
                assert f == ['BUNDLE','COMPLETE_'+role.upper()+'_ARTIFACT'] and bundle is None
                bundle = {}; cursor = dict(counters=bundle)
            else:
                assert len(f) == 4 and f[0] == 'COUNTER' and f[1] not in cursor['counters']
                cursor['counters'][f[1]] = dict(missed=int(f[2]),covered=int(f[3]))
        assert set(units)|set(packages) == set(physical) and not set(units)&set(packages)
        assert all(sum(row['counters'][kind][k] for row in units.values()) == bundle[kind][k] for kind in ['METHOD','CLASS','BRANCH'] for k in ['missed','covered'])
        measurements[role] = dict(physicalClasses=count,physicalHashes=physical,units=units,packageMetadata=packages,completeCounters=bundle,methodDetails=methods)
    main_roots = {path.split('/java/',1)[1][:-5] for path in plan['eligibilityClosureSourceHashes']}
    selected = {name:unit for name,unit in measurements['batch']['units'].items() if any(name[:-6] == root or name[:-6].startswith(root+'$') for root in main_roots)}
    methods = measurements['batch']['methodDetails']
    clock = [value for key,value in methods.items() if 'MonitoringObservationClock#' in key]
    unused_now = [value for key,value in methods.items() if 'MonitoringPoller#observeNow(' in key]
    assert len(clock) == 2 and len(unused_now) == 1 and all(value['counters']['METHOD']['covered'] == 0 for value in [*clock,*unused_now])
    for role,value in measurements.items():
        for name,unit in value['units'].items():
            if role != 'batch' or name not in selected:
                assert unit['counters']['METHOD']['covered'] == 0
    monitor_names = [Path(path).stem[:-4] for path in plan['wholeTestSourceHashes']]
    monitor_groups = {}
    for name in monitor_names:
        root = 'dev/codex/schubert/nk/batch/monitoring/'+name
        group = {key:value for key,value in selected.items() if key[:-6] == root or key[:-6].startswith(root+'$')}
        assert root+'.class' in group
        monitor_groups[name] = dict(classes=sorted(group),coverage100=all(counter['missed'] == 0 for value in group.values() for counter in value['counters'].values()),
            counters={kind:{key:sum(value['counters'][kind][key] for value in group.values()) for key in ['covered','missed']} for kind in ['LINE','METHOD','CLASS','BRANCH']})
    full = bool(methods) and all(x['missed'] == 0 for value in selected.values() for x in value['counters'].values()) and all(x['missed'] == 0 for value in methods.values() for x in value['counters'].values())
    assert not list(Path(h['begin']['testCwd']).iterdir()) and all(data.sha(Path(p).read_bytes()) == digest for p,digest in toolhashes.items())
    verify(invocation); OUT.mkdir()
    data.write(OUT/'measurement.json',dict(source=SOURCE,session=h['sessionId'],artifacts=measurements,selectedMain=selected,selectedMainCoverage100=full,selectedMethodDetails=methods,oldExecUnion=False,manualExclusionsAdded=False))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,observedTestExecutions=81,newTestIds=0,suites=10,xmlHashes=xmls,execSha256=h['execSha256'],allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=unchanged_tests,changedTestPhysical=len(changed),newTestPhysical=0,changedTestMetadata=changed_metadata,classMetadataVectors=metadata_vectors,selectedMain=selected,selectedMainCoverage100=full,selectedMethodDetails=methods,monitorGroups=monitor_groups,unexecutedClockAndObserveNowConfirmed=True,completeArtifactCounters={r:v['completeCounters'] for r,v in measurements.items()},wholeArtifactCoverage100=False,rawStatic=len(findings),rawRuleCounts={"DoNotUseThreads":20},spotbugsSixExit=0,staticGateExit=1,rawFindings=findings,measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),toolHashes=toolhashes,stages=stages,forbiddenProbeHits=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,coverageExclusionsAdded=False,externalActions=0))
    print(dict(actualExit=0,monitorGroups=monitor_groups,selectedMainCoverage100=full,oldTestsUnchanged=unchanged_tests,changedTestPhysical=len(changed),newTestPhysical=0,manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))

if __name__ == '__main__':
    main()
