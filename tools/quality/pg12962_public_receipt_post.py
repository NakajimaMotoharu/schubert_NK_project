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

SOURCE = 'c1d9b6e4b27b236ed8b40724f0701d2a2216237b'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg12962-public-receipt-post-v1'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg12958-public-receipt-host-v1'
OUT = data.BASE/'PG12962-public-receipt-post-v1'
COUNTS = {'api':467, 'web':358, 'batch':645, 'protocol':176, 'storage':80, 'bootstrap':117}

def main():
    invocation = capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG12956-public-receipt-six-compile-v1/manifest.json', '77e300fe384740d96d4b43accfc0859384c6e65d3fd8cac2da1d55a4ce1e0bf0')
    h = data.read_checked(data.BASE/'PG12958-public-receipt-host-v1/manifest.json', '2b1b13b3484cf1bc4ec6a2a8b1b2c3b15f2156b705e64b75972f1f197e92dc02')
    s = data.read_checked(data.BASE/'PG12960-public-receipt-static-v1/manifest.json', '052425b356a762c807453874a1c2fcd87b9b8997ea0a5d0fec23de7eee909d9b')
    plan = data.read_checked(data.BASE/'PG12954-public-receipt-plan-v1/manifest.json', '2f19a802d261701e1cdf4fedc9b7bad4bb0f6c33fa8ebcdbd4066c7ec7e6ca45')
    old = data.read_checked(data.BASE/'PG12938-login-policy-six-compile-v1/manifest.json', 'f65a05a93b6a857e21602222b5a9f5287a92b185cf6b540792c5bf8d7a10cac2')
    assert n['source'] == h['source'] == s['source'] == plan['source'] == SOURCE
    assert n['actualExit'] == n['testsExecuted'] == h['actualExit'] == 0 and s['actualExit'] == 1
    assert h['observedTestExecutions'] == 12 and not h['oldExecUnion']
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
    assert len(xmls) == 2 and len(actual) == 12 and Counter(actual) == Counter((r['className'],r['method']) for r in plan['cases'])
    assert xmls == h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=12;started=12;succeeded=12;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == h['execSha256']
    raw = (RUN/'classload-metadata.log').read_bytes(); assert data.sha(raw) == h['classloadSha256']
    loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:', raw.decode()))
    roots = {p.split('/java/',1)[1][:-5].replace('/','.') for p in [*plan['eligibilityClosureSourceHashes'],*plan['wholeTestSourceHashes']]}
    assert len(roots) == 4
    assert not [x for x in loaded if x.startswith('dev.codex.schubert.nk.') and not any(x == root or x.startswith(root+'$') for root in roots)]
    assert not [x for x in loaded if x.startswith(('org.postgresql.','org.apache.activemq.','jakarta.jms.'))]
    assert jar_classes(old) == jar_classes(n) and len(jar_classes(n)) == 1843
    a,b = test_classes(old),test_classes(n)
    extra = ('api','dev/codex/schubert/nk/api/application/question/QuestionReceiptRecoveryTest.class')
    assert len(a) == 1966 and len(b) == 1967 and set(b)-set(a) == {extra} and not set(a)-set(b)
    assert all(a[key] == b[key] for key in a)
    parsed = class_parts((Path(n['jars']['api']['path']).parent/'test-classes'/extra[1]).read_bytes(), extra[1])
    assert parsed['model']['sourceFile'] == 'QuestionReceiptRecoveryTest.java'
    metadata_vectors = selftest()
    findings = []
    for label,tag,count in [('pmd','violation',6),('checkstyle','error',0)]:
        p = data.BASE/'PG12960-public-receipt-static-v1'/(label+'.xml')
        assert data.sha(p.read_bytes()) == s['reports'][label]['sha256']
        nodes = [x for x in ET.parse(p).getroot().iter() if x.tag.rpartition('}')[2] == tag]
        assert len(nodes) == count and s['reports'][label]['processingErrors'] == 0
        if label == 'pmd':
            assert Counter(x.get("rule") for x in nodes) == Counter(DoNotUseThreads=3,UseConcurrentHashMap=2,AvoidSynchronizedStatement=1)
            findings = [dict(rule=x.get('rule'),beginline=int(x.get('beginline')),endline=int(x.get('endline'))) for x in nodes]
    assert s['spotbugsSixExit'] == 0 and all(v['actualExit'] == 0 and not v['timedOut'] for k,v in s['stages'].items() if k != 'pmd')
    SLOT.mkdir(); reader = SLOT/'reader'; reader.mkdir(); steps.SLOT = SLOT; tc = data.ROOT.parent/'toolchain'
    helper = data.ROOT/'tools/quality/architecture/PublicReceiptRecoveryArtifactCoverageMeasure.java'
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
    selected = {name:measurements['api']['units']['dev/codex/schubert/nk/api/application/question/'+name+'.class'] for name in ['QuestionReceiptId','QuestionReceiptIdGenerator']}
    methods = measurements['api']['methodDetails']
    full = bool(methods) and all(x['missed'] == 0 for value in selected.values() for x in value['counters'].values()) and all(x['missed'] == 0 for value in methods.values() for x in value['counters'].values())
    cwd = Path(h['begin']['testCwd'])
    expected_file = 'target/question-receipt-traces/PT-QST-RID008.txt'
    expected_bytes = b'forward=0123456789ABCDEFGHJKMNPQRS\nreverse=ZYXWVTSRQPNMKJHGFEDCBA9876\nlength=26\nalphabetSize=32\nrandomDrawsPerId=26\nownerOrTimeInput=false\n'
    entries = list(cwd.rglob('*')); assert not any(p.is_symlink() for p in entries)
    assert sorted(str(p.relative_to(cwd)) for p in entries if p.is_dir()) == ['target','target/question-receipt-traces']
    assert [str(p.relative_to(cwd)) for p in entries if p.is_file()] == [expected_file]
    assert (cwd/expected_file).read_bytes() == expected_bytes
    assert (data.BASE/'PG12958-public-receipt-host-v1/PT-QST-RID008.txt').read_bytes() == expected_bytes
    assert h['publicTraceCheckPassed'] and h['ownedPublicTrace']['sha256'] == data.sha(expected_bytes) and len(expected_bytes) == 139
    assert all(data.sha(Path(p).read_bytes()) == digest for p,digest in toolhashes.items())
    verify(invocation); OUT.mkdir()
    data.write(OUT/'measurement.json',dict(source=SOURCE,session=h['sessionId'],artifacts=measurements,selectedTwoMain=selected,selectedTwoMainCoverage100=full,selectedMethodDetails=methods,oldExecUnion=False,manualExclusionsAdded=False))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,observedTestExecutions=12,newTestIds=4,suites=2,xmlHashes=xmls,execSha256=h['execSha256'],allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=1966,newTestPhysical=1,newTestPhysicalSha256=b[extra],classMetadataVectors=metadata_vectors,selectedTwoMain=selected,selectedTwoMainCoverage100=full,selectedMethodDetails=methods,completeArtifactCounters={r:v['completeCounters'] for r,v in measurements.items()},wholeArtifactCoverage100=False,rawStatic=len(findings),rawRuleCounts=dict(Counter(x["rule"] for x in findings)),spotbugsSixExit=0,staticGateExit=1,rawFindings=findings,measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),toolHashes=toolhashes,stages=stages,forbiddenProbeHits=0,oldExecUnion=False,newAccepted=0,whole451Accepted=False,coverageExclusionsAdded=False,businessExternalActions=0,ownedPublicTrace=dict(path=expected_file,sha256=data.sha(expected_bytes),length=139),wholeHostFilesystemAuditPerformed=False))
    print(dict(actualExit=0,selectedTwoMain=selected,selectedTwoMainCoverage100=full,oldTestsUnchanged=1966,newTestPhysical=1,manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))

if __name__ == '__main__':
    main()
