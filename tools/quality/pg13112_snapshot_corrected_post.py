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
from pg13101_snapshot_oracle_inverse import inverse, negative

SOURCE = '5c378e064f0f8a7366316d4afa28fbb2cd9cec81'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13112-snapshot-corrected-post-v1'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13108-snapshot-corrected-host-v1'
OUT = data.BASE/'PG13112-snapshot-corrected-post-v1'
COUNTS = {'api':467, 'web':358, 'batch':645, 'protocol':176, 'storage':80, 'bootstrap':117}

def main():
    invocation = capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13106-snapshot-corrected-six-compile-v1/manifest.json', '0d052046bbfe7586c491f1cb398566301fae8d958c0e2ae3e660d477961c12c7')
    h = data.read_checked(data.BASE/'PG13108-snapshot-corrected-host-v1/manifest.json', '776be8fff9f5c812c557a02f2198313adf8f506f2f88fea1c809e200911b525a')
    s = data.read_checked(data.BASE/'PG13110-snapshot-corrected-static-v1/manifest.json', '882dbee6518ab17fe8410add62aa8d228b7acd9181f0ab6f65f69a795a777f0e')
    plan = data.read_checked(data.BASE/'PG13104-snapshot-corrected-plan-v1/manifest.json', '03bc1cd8dc48f66167728284be8e5a5d04f32aea515ff3d07119dec4c66f9cd8')
    old = data.read_checked(data.BASE/'PG13076-monitor-test-six-compile-v1/manifest.json', '77020a553a53f8c09d498899dbb3e5844121dc67023862901fa7ad82b12c1932')
    assert n['source'] == h['source'] == s['source'] == plan['source'] == SOURCE
    assert n['actualExit'] == n['testsExecuted'] == h['actualExit'] == 0 and s['actualExit'] == 0
    assert h['observedTestExecutions'] == 3 and not h['oldExecUnion']
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
    assert len(xmls) == 1 and len(actual) == 3 and Counter(actual) == Counter((r['className'],r['method']) for r in plan['cases'])
    assert xmls == h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=3;started=3;succeeded=3;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == h['execSha256']
    raw = (RUN/'classload-metadata.log').read_bytes(); assert data.sha(raw) == h['classloadSha256']
    loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:', raw.decode()))
    roots = {p.split('/java/',1)[1][:-5].replace('/','.') for p in [*plan['eligibilityClosureSourceHashes'],*plan['wholeTestSourceHashes'],*plan['supportTestSourceHashes']]}
    assert len(roots) == 2
    assert not [x for x in loaded if x.startswith('dev.codex.schubert.nk.') and not x.startswith('dev.codex.schubert.nk.protocol.') and not any(x == root or x.startswith(root+'$') for root in roots)]
    assert not [x for x in loaded if x.startswith(('org.postgresql.','org.apache.activemq.','jakarta.jms.'))]
    assert jar_classes(old) == jar_classes(n) and len(jar_classes(n)) == 1843
    a,b = test_classes(old),test_classes(n)
    extras = {('api','dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshotBoundaryTest.class')}
    assert len(a) == 1972 and len(b) == 1973 and set(b)-set(a) == extras and not set(a)-set(b)
    assert all(a[key] == b[key] for key in a)
    for role,entry in extras:
        parsed = class_parts((Path(n['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        assert parsed['model']['sourceFile'] == Path(entry).stem+'.java'
    preserved = data.read_checked(data.BASE/'PG13100-snapshot-oracle-originals-v1/manifest.json','4c9db4bb5ddf53982ac6778a801a57a12ec84ce1ce55d37765ec1328f733a861')
    original = data.read_checked(data.BASE/'PG13100-snapshot-oracle-originals-v1/original.json',preserved['originalSha256'])
    assert not preserved['oldActualCauseClassExported'] and preserved['oldActualExit'] == 1
    changes = inverse(original['text'],(data.ROOT/original['test']).read_text())
    assert changes == plan['oracleCorrectionInverse'] and negative(original['text'],(data.ROOT/original['test']).read_text()) == 7
    metadata_vectors = selftest()
    findings = []
    for label,tag,count in [('pmd','violation',0),('checkstyle','error',0)]:
        p = data.BASE/'PG13110-snapshot-corrected-static-v1'/(label+'.xml')
        assert data.sha(p.read_bytes()) == s['reports'][label]['sha256']
        nodes = [x for x in ET.parse(p).getroot().iter() if x.tag.rpartition('}')[2] == tag]
        assert len(nodes) == count and s['reports'][label]['processingErrors'] == 0
        if label == 'pmd':
            assert not nodes
            findings = [dict(rule=x.get('rule'),beginline=int(x.get('beginline')),endline=int(x.get('endline'))) for x in nodes]
    assert s['spotbugsSixExit'] == 0 and all(v['actualExit'] == 0 and not v['timedOut'] for k,v in s['stages'].items() if k != 'pmd')
    SLOT.mkdir(); reader = SLOT/'reader'; reader.mkdir(); steps.SLOT = SLOT; tc = data.ROOT.parent/'toolchain'
    helper = data.ROOT/'tools/quality/architecture/SnapshotMaximumArtifactCoverageMeasure.java'
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
    selected = {'ScenarioDetailSnapshot':measurements['api']['units']['dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshot.class']}
    methods = measurements['api']['methodDetails']
    for role,value in measurements.items():
        for name,unit in value['units'].items():
            if role not in ['api','protocol'] or (role == 'api' and name != 'dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshot.class'):
                assert unit['counters']['METHOD']['covered'] == 0
    full = bool(methods) and all(x['missed'] == 0 for value in selected.values() for x in value['counters'].values()) and all(x['missed'] == 0 for value in methods.values() for x in value['counters'].values())
    assert not list(Path(h['begin']['testCwd']).iterdir()) and all(data.sha(Path(p).read_bytes()) == digest for p,digest in toolhashes.items())
    verify(invocation); OUT.mkdir()
    data.write(OUT/'measurement.json',dict(source=SOURCE,session=h['sessionId'],artifacts=measurements,selectedMain=selected,selectedMainCoverage100=full,selectedMethodDetails=methods,oldExecUnion=False,manualExclusionsAdded=False,oracleCorrectionInverse=changes))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,observedTestExecutions=3,newTestIds=3,suites=1,xmlHashes=xmls,execSha256=h['execSha256'],allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1972,newTestPhysical=1,newTestPhysicalSha256={entry:b[(role,entry)] for role,entry in sorted(extras)},classMetadataVectors=metadata_vectors,selectedMain=selected,selectedMainCoverage100=full,selectedMethodDetails=methods,completeArtifactCounters={r:v['completeCounters'] for r,v in measurements.items()},wholeArtifactCoverage100=False,rawStatic=len(findings),rawRuleCounts={},spotbugsSixExit=0,staticGateExit=0,rawFindings=findings,measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),toolHashes=toolhashes,stages=stages,forbiddenProbeHits=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,coverageExclusionsAdded=False,oracleCorrectionInverse=changes,oracleCorrectionNegativeVectors=7,oldCandidateActualExit=1,oldCandidateSuccessTransferred=False,externalActions=0))
    print(dict(actualExit=0,selectedMain=selected,selectedMainCoverage100=full,oldTestsUnchanged=1972,newTestPhysical=1,manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))

if __name__ == '__main__':
    main()
