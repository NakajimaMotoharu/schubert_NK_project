"""Independent current102 Protocol executions, fixed59fixture source inverse and complete artifact counters; no PT replay."""
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
import pg9346_direct_companion_jdk_post as steps

SOURCE = '5cc74a2e437d19b22b07eb9a57c8d04414109e9b'
WORK = data.ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10782-protocol-fixture-batch-host-v1'
SLOT = WORK/'pg10786-protocol-fixture-batch-post-v1'
OUT = data.BASE/'PG10786-protocol-fixture-batch-post-v1'


def require_package_metadata(name,model):
    if not name.endswith('/package-info.class') or model != dict(flags=5632,sourceFile='package-info.java',fields=0,methods=[]):
        raise ValueError('exact no-member package annotation metadata, not arbitrary missing class')



def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared_path = data.BASE/'PG10780-protocol-fixture-batch-preflight-v1/manifest.json'
    prepared = data.read_checked(prepared_path,'13470c5ac83be631a73f3e7caf506ce88dfe29b3d5ecd5695a7af8c53e20a97f')
    host_path = data.BASE/'PG10782-protocol-fixture-batch-host-v1/manifest.json'
    host = data.read_checked(host_path,'c4b328b524e3ebb362d4398e9b430df5ea7890474ea169ce94deda4aab16ca5d')
    normal = data.read_checked(data.BASE/'PG10778-protocol-fixture-batch-six-compile-v1/manifest.json',
        'f0b3a2df7892710085ec00739c49c8d0a6d0a7da8d3dc9d4ccee8d75b6214462')
    assert host['source'] == prepared['source'] == normal['source'] == SOURCE
    assert host['actualExit'] == prepared['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert len(host['localeRuns']) == 1 and host['observedTestExecutions'] == 102 and host['uniqueMethods'] == 102
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**prepared['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    cases = data.read_checked(prepared_path.parent/'cases.json',prepared['casesSha256'])
    expected = Counter((r['className'],r['method']) for r in cases)
    for row in host['localeRuns']:
        label = row['locale'].rpartition('-')[2].lower()
        folder = RUN/label
        actual,xmls = [],{}
        for file in sorted((folder/'xml').glob('TEST-*.xml')):
            root = ET.parse(file).getroot()
            assert int(root.get('tests')) == sum(r['className'] == root.get('name') for r in cases) and all(int(root.get(k)) == 0 for k in ('failures','errors','skipped'))
            assert all(not list(c) for c in root.findall('testcase'))
            actual += [(c.get('classname'),c.get('name')) for c in root.findall('testcase')]
            xmls[file.name] = data.sha(file.read_bytes())
        assert Counter(actual) == expected and len(xmls) == 22 and xmls == row['xmlHashes']
        assert (folder/'xml/summary.safe.txt').read_text() == 'found=102;started=102;succeeded=102;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
        assert data.sha((folder/'jacoco.exec').read_bytes()) == row['execSha256']
        log = (folder/'classload-metadata.log').read_bytes()
        assert data.sha(log) == row['loadedClassMetadataSha256']
        loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',log.decode()))
        forbidden = sorted(n for n in loaded if (n.startswith('dev.codex.schubert.nk.') and not n.startswith('dev.codex.schubert.nk.protocol.'))
            or n.startswith(('org.postgresql.','org.apache.activemq.')))
        assert loaded and not forbidden
        assert 'dev.codex.schubert.nk.protocol.layout.TypedFieldValues' in loaded
    SLOT.mkdir(mode=0o700)
    classes = SLOT/'complete-main'
    classes.mkdir()
    with zipfile.ZipFile(prepared['protocolJar']) as jar:
        for name,digest in prepared['completeProtocolMainClasses'].items():
            raw = jar.read(name)
            assert data.sha(raw) == digest
            file = classes/name
            file.parent.mkdir(parents=True,exist_ok=True)
            with file.open('xb') as stream:
                stream.write(raw)
    catalog = SLOT/'complete-main-catalog.txt'
    with catalog.open('x') as stream:
        stream.write(''.join(name+'\n' for name in sorted(prepared['completeProtocolMainClasses'])))
    helper = data.ROOT/'tools/quality/architecture/ProtocolFixtureBatchCoverageMeasure.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = data.ROOT.parent/'toolchain'
    libs = [tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    dependencies = {str(p):data.sha(p.read_bytes()) for p in libs}
    reader = SLOT/'reader'
    reader.mkdir()
    cp = os.pathsep.join(map(str,libs))
    steps.SLOT = SLOT
    stages = [steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    measured = []
    schema_vectors = selftest()
    for row in host['localeRuns']:
        label = row['locale'].rpartition('-')[2].lower()
        command = [str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,helper.stem,
            str(RUN/label/'jacoco.exec'),str(classes),str(catalog),row['sessionId']]
        result = steps.step('measure-'+label,command)
        stages.append(result)
        assert result['actualExit'] == 0 and not result['timedOut']
        lines = (SLOT/('measure-'+label+'.stdout')).read_text().splitlines()
        session = parse_session(lines[0].split('\t'),row['sessionId'])
        assert lines[1] == 'FORBIDDEN_PROBE_HITS\t0'
        units,bundle,current = {},{},None
        package_metadata = set()
        for line in lines[2:]:
            parts = line.split('\t')
            if parts[0] == 'PACKAGE_METADATA_ONLY':
                assert len(parts) == 2 and parts[1]+'.class' in prepared['completeProtocolMainClasses'] and parts[1] not in package_metadata
                package_metadata.add(parts[1])
            elif parts[0] == 'CLASS':
                assert len(parts) == 3 and parts[1]+'.class' in prepared['completeProtocolMainClasses'] and parts[1] not in units
                current = dict(classCrc64=parts[2],counters={})
                units[parts[1]] = current
            elif parts[0] == 'BUNDLE':
                assert parts == ['BUNDLE','COMPLETE_PROTOCOL_ARTIFACT'] and not bundle
                current = dict(counters=bundle)
            else:
                assert len(parts) == 4 and parts[0] == 'COUNTER' and current is not None
                _,kind,missed,covered = parts
                assert kind not in current['counters']
                current['counters'][kind] = dict(missed=int(missed),covered=int(covered))
        assert len(package_metadata) == 7 and not set(units)&package_metadata
        assert {n+'.class' for n in set(units)|package_metadata} == set(prepared['completeProtocolMainClasses'])
        package_models = {}
        for name in sorted(package_metadata):
            raw = (classes/(name+'.class')).read_bytes()
            model = decode(raw,name+'.class')
            require_package_metadata(name+'.class',model)
            package_models[name] = dict(sha256=data.sha(raw),model=model,counterStatus='NOT_APPLICABLE_NO_EXECUTABLE_MEMBER_PACKAGE_ANNOTATION')
        for kind in ('METHOD','CLASS','BRANCH'):
            for key in ('missed','covered'):
                assert sum(v['counters'][kind][key] for v in units.values()) == bundle[kind][key]
        # LINE is source-line union in the bundle, not a sum of overlapping inner-class lines.
        assert set(bundle) == {'LINE','METHOD','CLASS','BRANCH'}
        measured.append(dict(locale=row['locale'],session=session,completeProtocolClasses=units,nonExecutablePackageMetadata=package_models,bundleCounters=bundle,
            probeHitsOutsideProtocol=0,execSha256=row['execSha256'],wholeJavaCoverage100=False,oldExecUnion=False))
    previous = data.read_checked(data.BASE/'PG10756-protocol-semantic-six-compile-v1/manifest.json',
        '5273ae8b8a1bc9bb275793444b298801943eb5dba30f027be706913c7056fbc9')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test,new_test = test_classes(previous),test_classes(normal)
    assert set(old_test) == set(new_test) and len(new_test) == 1962
    changed = sorted(k for k in new_test if old_test[k] != new_test[k])
    plan = data.read_checked(data.BASE/'PG10773-protocol-duplicate-batch-plan-v1/manifest.json',
        '08aa28e9d97072c21bd14b3181605165349b6be04dfe8f577fb1c5883ff39751')
    proof = data.read_checked(data.BASE/'PG10774-protocol-duplicate-batch-source-post-v1/manifest.json',
        'b2e54df0e380e0afbd37e2bcfeba1cd752940ccf1d869cef60c322ef5271f5f4')
    assert proof['sourceChanges'] == plan['sourceChanges'] and proof['metadataNegativeVectors'] == 33
    assert all(data.sha((data.ROOT/r['path']).read_bytes()) == r['sha256'] for r in plan['sourceChanges'])
    allowed_sources = {Path(r['path']).name for r in plan['sourceChanges']}
    observed_sources = set()
    for module,entry in changed:
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/entry
        source_file = decode(file.read_bytes(),entry)['sourceFile']
        assert module == 'protocol' and source_file in allowed_sources
        observed_sources.add(source_file)
    assert observed_sources == allowed_sources and len(allowed_sources) == 11
    static_path = data.BASE/'PG10784-protocol-fixture-module-static-v1/manifest.json'
    static = data.read_checked(static_path,'cf78f966e0e8d185dc00049a52172c45d01c8c3bbd362017291551ce5473c2e1')
    assert static['source'] == SOURCE and static['actualExit'] == 1
    assert static['reports']['pmd']['findings'] == 38 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    for label in ('pmd','checkstyle'):
        assert data.sha((static_path.parent/(label+'.xml')).read_bytes()) == static['reports'][label]['sha256']
    static_nodes = [n for n in ET.parse(static_path.parent/'pmd.xml').getroot().iter() if n.tag.rpartition('}')[2] == 'violation']
    assert len(static_nodes) == 38 and not any(n.get('rule') == 'AvoidDuplicateLiterals' for n in static_nodes)
    assert data.sha(helper.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p,h in dependencies.items())
    original_model = dict(flags=5632,sourceFile='package-info.java',fields=0,methods=[])
    for name,model in [
        ('dev/codex/schubert/nk/protocol/X.class',original_model),
        ('dev/codex/schubert/nk/protocol/package-info.class',dict(original_model,fields=1)),
        ('dev/codex/schubert/nk/protocol/package-info.class',dict(original_model,methods=[{'name':'x'}])),
        ('dev/codex/schubert/nk/protocol/package-info.class',dict(original_model,flags=0)),
        ('dev/codex/schubert/nk/protocol/package-info.class',dict(original_model,sourceFile='X.java'))]:
        try:
            require_package_metadata(name,model)
        except ValueError:
            pass
        else:
            raise AssertionError('unknown/executable metadata class cannot be removed')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'complete-protocol-coverage.json',measured)
    xml_root = OUT/'xml'
    xml_root.mkdir()
    for row in host['localeRuns']:
        label = row['locale'].rpartition('-')[2].lower()
        folder = xml_root/label
        folder.mkdir()
        for file in sorted((RUN/label/'xml').iterdir()):
            assert file.is_file() and (file.name in row['xmlHashes'] or file.name == 'summary.safe.txt')
            with (folder/file.name).open('xb') as stream:
                stream.write(file.read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,stages=stages,
        originalHostManifestSha256=data.sha(host_path.read_bytes()),staticManifestSha256=data.sha(static_path.read_bytes()),staticRawGate=1,remainingPmd=38,
        protocolFourCounters100=all(all(c['missed'] == 0 and c['covered'] > 0 for c in row['bundleCounters'].values()) for row in measured),testsPerLocale=102,localeRuns=1,testExecutions=102,uniqueMethods=102,newTestMethods=0,
        coverageSha256=data.sha((OUT/'complete-protocol-coverage.json').read_bytes()),coverageSessionSchemaVectors=schema_vectors,
        allProtocolPhysicalMainClasses=len(prepared['completeProtocolMainClasses']),coverageScope='COMPLETE_PROTOCOL_ARTIFACT_PER_SEPARATE_EXEC_WITH_NONEXECUTABLE_PACKAGE_METADATA',
        analyzedClassesPerLocale=len(measured[0]['completeProtocolClasses']),nonExecutablePackageMetadataPerLocale=7,
        metadataRecoveryOnly=False,packageMetadataNegativeVectors=5,independentSourceNegativeVectors=33,fixtureConstantsAdded=59,
        mainClassesUnchanged=1843,totalTestClasses=1962,otherTestClassesUnchanged=1962-len(changed),physicalTestClassesChanged=len(changed),
        changedTestClasses=[dict(module=m,entry=p) for m,p in changed],sourceChanges=plan['sourceChanges'],
        prohibitedLoadedProductClasses=0,probeHitsOutsideProtocol=0,oldExecUnion=False,wholeJavaCoverage100=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,testExecutions=102,uniqueMethods=102,completeClasses=len(prepared['completeProtocolMainClasses']),
        counters=[dict(locale=m['locale'],bundle=m['bundleCounters']) for m in measured],manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
