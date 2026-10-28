"""Independent eight-case XML, one exec CRC, all six artifact counters and physical inputs."""
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
from pg11929_storage_fixture_class_metadata import parts
from quality_scope_dimensions import bind
import pg9346_direct_companion_jdk_post as steps

SOURCE = 'b11fe71bd20e244dd10c83bd339f8345a0c1f085'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13164-nfc-golden-post-v2'
RUN = data.ROOT.parent/'pgpt-runs/PG379/pg13158-nfc-golden-host-v1'
OUT = data.BASE/'PG13164-nfc-golden-post-v2'
COUNTS = {'api':467,'web':358,'batch':645,'protocol':176,'storage':80,'bootstrap':117}

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13156-nfc-golden-six-compile-v1/manifest.json','4c1f5352b5d048cda761851d3482fd74983b3ec885ed839d91f987bca60be0d9')
    h = data.read_checked(data.BASE/'PG13158-nfc-golden-host-v1/manifest.json','90af523f25fd27284d2fc5de6e2205ab1bfe0fcb4f77db7ae94f0d7e142fcabd')
    s = data.read_checked(data.BASE/'PG13160-nfc-golden-static-v1/manifest.json','d5421c9de06fd99be43811f7f7faf32a9f963d4ae0b31d1bea24449c36c71ffd')
    plan = data.read_checked(data.BASE/'PG13154-nfc-golden-plan-v1/manifest.json','7695d1297c842faf24096b623194ff74903b849d58f2b4355f002ae9b5a5748f')
    old = data.read_checked(data.BASE/'PG13134-main-literal-six-compile-v1/manifest.json','ef0c374ffb76d88402c3a19c70999c9f644bdbdecb0252c747b7f1544521d823')
    pre = data.read_checked(data.BASE/'PG13152-nfc-golden-preflight-v1/manifest.json','c7a2ac738655f537cc227ee88b16d89e163ef618c6698ba03ac0d5487f25c34e')
    assert all(x['source'] == SOURCE and x['actualExit'] == 0 for x in (n,h,s,plan)) and n['testsExecuted'] == 0
    assert all(row['actualExit'] == 0 and not row['timedOut'] for row in [*h['stages'],*s['stages']])
    assert s['rawStatic'] == s['staticGateExit'] == s['spotbugsSixExit'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**h['begin']['dependencyHashes'],**h['begin']['physicalTestFiles']}.items())
    xmls = {};actual = []
    for path in sorted((RUN/'xml').glob('TEST-*.xml')):
        node = ET.parse(path).getroot();assert all(node.get(k) == '0' for k in ['failures','errors','skipped'])
        assert all(not list(row) for row in node.findall('testcase'))
        xmls[path.name] = data.sha(path.read_bytes());actual.extend((row.get('classname'),row.get('name')) for row in node.findall('testcase'))
    assert len(xmls) == 2 and len(actual) == 8 and Counter(actual) == Counter((r['className'],r['method']) for r in plan['cases']) and xmls == h['xmlHashes']
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=8;started=8;succeeded=8;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    assert data.sha((RUN/'jacoco.exec').read_bytes()) == h['execSha256']
    raw = (RUN/'classload-metadata.log').read_bytes();assert data.sha(raw) == h['classloadSha256']
    loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',raw.decode()))
    roots = {p.split('/java/',1)[1][:-5].replace('/','.') for p in [*plan['eligibilityClosureSourceHashes'],*plan['wholeTestSourceHashes']]}
    assert len(roots) == 5 and not [x for x in loaded if x.startswith('dev.codex.schubert.nk.') and not any(x == root or x.startswith(root+'$') for root in roots)]
    assert not [x for x in loaded if x.startswith(('org.postgresql.','org.apache.activemq.','jakarta.jms.'))]
    assert jar_classes(old) == jar_classes(n) and len(jar_classes(n)) == 1843
    a,b = test_classes(old),test_classes(n);extra = {('protocol','dev/codex/schubert/nk/protocol/codec/FieldCodecNfcGoldenTest.class')}
    assert len(a) == 1973 and set(b)-set(a) == extra and not set(a)-set(b) and all(a[k] == b[k] for k in a)
    for role,entry in extra:
        value = (Path(n['jars'][role]['path']).parent/'test-classes'/entry).read_bytes()
        assert parts(value,entry)['model']['sourceFile'] == 'FieldCodecNfcGoldenTest.java'
    for name,tag in [('pmd','violation'),('checkstyle','error')]:
        path = data.BASE/'PG13152-nfc-golden-preflight-v1'/(name+'.xml')
        assert data.sha(path.read_bytes()) == pre['reports'][name]['sha256'] and pre['reports'][name]['processingErrors'] == 0
        assert not [x for x in ET.parse(path).getroot().iter() if x.tag.rpartition('}')[2] == tag]
    SLOT.mkdir();reader = SLOT/'reader';reader.mkdir();steps.SLOT = SLOT;tc = data.ROOT.parent/'toolchain'
    helper = data.ROOT/'tools/quality/architecture/NfcGoldenArtifactCoverageMeasure.java'
    libraries = [tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*[tc/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ['asm','asm-tree','asm-commons']]]
    tools = {str(p):data.sha(p.read_bytes()) for p in [helper,*libraries]};cp = os.pathsep.join(map(str,libraries))
    stages = [steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut'];measurements = {}
    for role,count in COUNTS.items():
        classes = SLOT/('complete-'+role+'-main');classes.mkdir()
        with zipfile.ZipFile(n['jars'][role]['path']) as jar:
            physical = {name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')};assert len(physical) == count
            for name in physical:
                target = classes/name;target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as f:f.write(jar.read(name))
        catalog = SLOT/('complete-'+role+'-catalog.txt')
        with catalog.open('x') as f:f.write(''.join(name+'\n' for name in sorted(physical)))
        stages.append(steps.step('measure-'+role,[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,str(RUN/'jacoco.exec'),str(classes),str(catalog),h['sessionId'],role]))
        assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
        lines = (SLOT/('measure-'+role+'.stdout')).read_text().splitlines();assert lines[0].startswith('SESSION\t'+h['sessionId']+'\t') and lines[1] == 'FORBIDDEN_PROBE_HITS\t0'
        units = {};packages = [];bundle = None;cursor = None;methods = {}
        for line in lines[2:]:
            fields = line.split('\t')
            if fields[0] == 'PACKAGE_METADATA_ONLY':packages.append(fields[1]+'.class')
            elif fields[0] == 'CLASS':
                name = fields[1]+'.class';assert name not in units;cursor = dict(classCrc64=fields[2],counters={});units[name] = cursor
            elif fields[0] == 'METHOD_DETAIL':
                key = fields[1]+fields[2];assert key not in methods;cursor = dict(counters={});methods[key] = cursor
            elif fields[0] == 'BUNDLE':
                assert fields == ['BUNDLE','COMPLETE_'+role.upper()+'_ARTIFACT'] and bundle is None;bundle = {};cursor = dict(counters=bundle)
            else:
                assert len(fields) == 4 and fields[0] == 'COUNTER' and fields[1] not in cursor['counters'];cursor['counters'][fields[1]] = dict(missed=int(fields[2]),covered=int(fields[3]))
        assert set(units)|set(packages) == set(physical) and not set(units)&set(packages)
        assert all(sum(row['counters'][kind][k] for row in units.values()) == bundle[kind][k] for kind in ['METHOD','CLASS','BRANCH'] for k in ['missed','covered'])
        measurements[role] = dict(physicalClasses=count,physicalHashes=physical,units=units,packageMetadata=packages,completeCounters=bundle,methodDetails=methods)
    names = ['FieldCodec','FieldEncodingException','PermanentProtocolException']
    selected = {name:measurements['protocol']['units']['dev/codex/schubert/nk/protocol/codec/'+name+'.class'] for name in names}
    selected_entries = {'dev/codex/schubert/nk/protocol/codec/'+name+'.class' for name in names}
    for role,value in measurements.items():
        for name,unit in value['units'].items():
            if role != 'protocol' or name not in selected_entries:assert unit['counters']['METHOD']['covered'] == 0
    methods = measurements['protocol']['methodDetails'];full = bool(methods) and all(x['missed'] == 0 for row in selected.values() for x in row['counters'].values()) and all(x['missed'] == 0 for row in methods.values() for x in row['counters'].values())
    proof = dict(actualExit=0,source=SOURCE,observedTestExecutions=len(actual),newTestIds=3,suites=len(xmls),allMainClassesUnchanged=1843,oldTestPhysicalUnchanged=len(a),newTestPhysical=len(extra),oldExecUnion=False)
    dimensions = bind(plan,h,proof)
    assert not list(Path(h['begin']['testCwd']).iterdir()) and all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'measurement.json',dict(source=SOURCE,session=h['sessionId'],artifacts=measurements,selectedMain=selected,selectedMethodDetails=methods,oldExecUnion=False,manualExclusionsAdded=False))
    data.write(OUT/'manifest.json',dict(**proof,invocation=invocation,dimensions=dimensions.public(),xmlHashes=xmls,execSha256=h['execSha256'],
        selectedMain=selected,selectedMainCoverage100=full,selectedMethodDetails=methods,completeArtifactCounters={r:v['completeCounters'] for r,v in measurements.items()},
        wholeArtifactCoverage100=False,rawStatic=0,staticGateExit=0,spotbugsSixExit=0,forbiddenProbeHits=0,measurementSha256=data.sha((OUT/'measurement.json').read_bytes()),
        toolHashes=tools,stages=stages,newAccepted=0,whole451Accepted=False,coverageExclusionsAdded=False,externalActions=0))
    print(dict(actualExit=0,selectedMain=selected,selectedMainCoverage100=full,manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))

if __name__ == '__main__':main()
