"""Recovered original locale XML/exec and all physical Protocol class accounting; no PT replay."""
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
from pg10398_role_view_preflight import canonical
import pg9346_direct_companion_jdk_post as steps

SOURCE = '21d275a74fb7ec8bb3a5d39f168d561f03c5b9a7'
WORK = data.ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10740-protocol-locale-host-v1'
SLOT = WORK/'pg10745-protocol-locale-recovery-post-v1'
OUT = data.BASE/'PG10745-protocol-locale-recovery-post-v1'


def require_package_metadata(name,model):
    if not name.endswith('/package-info.class') or model != dict(flags=5632,sourceFile='package-info.java',fields=0,methods=[]):
        raise ValueError('exact no-member package annotation metadata, not arbitrary missing class')


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared_path = data.BASE/'PG10738-protocol-locale-preflight-v1/manifest.json'
    prepared = data.read_checked(prepared_path,'93e24bd060ad721cc5536b24cbc11d5d00cf6caf3d010d9b3a14cf4e8eb6f899')
    host_path = data.BASE/'PG10740-protocol-locale-host-v1/manifest.json'
    host = data.read_checked(host_path,'f04f5dc19003d241b411a1ede0d9b24f614758e3b0f67ccf19fa79b61c58a0b6')
    normal = data.read_checked(data.BASE/'PG10736-protocol-uppercase-six-compile-v1/manifest.json',
        '5bfb5e23af7295e2d163f7b8de21d2290c14ffb6eba8339e654ff4c56ae86492')
    assert host['source'] == prepared['source'] == normal['source'] == SOURCE
    assert host['actualExit'] == prepared['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert len(host['localeRuns']) == 2 and host['observedTestExecutions'] == 4 and host['uniqueMethods'] == 2
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
            assert int(root.get('tests')) == 2 and all(int(root.get(k)) == 0 for k in ('failures','errors','skipped'))
            assert all(not list(c) for c in root.findall('testcase'))
            actual += [(c.get('classname'),c.get('name')) for c in root.findall('testcase')]
            xmls[file.name] = data.sha(file.read_bytes())
        assert Counter(actual) == expected and len(xmls) == 1 and xmls == row['xmlHashes']
        assert (folder/'xml/summary.safe.txt').read_text() == 'found=2;started=2;succeeded=2;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
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
    helper = data.ROOT/'tools/quality/architecture/ProtocolLocaleCoverageMeasureV2.java'
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
    previous = data.read_checked(data.BASE/'PG10714-graph-constants-six-compile-v1/manifest.json',
        'b24ac5ef1f85b9ed935e0772ef04040acbd12b78f573a88aa4d9420ae4995676')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test,new_test = test_classes(previous),test_classes(normal)
    assert set(old_test) == set(new_test) and len(new_test) == 1962
    changed = sorted(k for k in new_test if old_test[k] != new_test[k])
    for module,entry in changed:
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/entry
        assert module == 'protocol' and decode(file.read_bytes(),entry)['sourceFile'] == 'SemanticFieldValueTest.java'
    plan = data.read_checked(data.BASE/'PG10732-protocol-uppercase-fixture-plan-v1/manifest.json',
        '1dbfd04379509252ed8350775d9656412c47f849511657a5421440f7f61365d0')
    target = plan['sourceChanges'][0]['path']
    text = (data.ROOT/target).read_text()
    restored = re.sub(r'\s*private\s+static\s+final\s+String\s+UUID_UPPERCASE_TEXT\s*=\s*"123E4567-E89B-12D3-A456-426614174000"\s*;','',text,count=1)
    restored = restored.replace('UUID_UPPERCASE_TEXT','UUID_TEXT.toUpperCase()')
    old_snapshot = Path(previous['jars']['protocol']['path']).parent.parent.parent.parent
    assert canonical(restored) == canonical((old_snapshot/target).read_text())
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
        originalHostManifestSha256=data.sha(host_path.read_bytes()),testsPerLocale=2,localeRuns=2,testExecutions=4,uniqueMethods=2,newTestMethods=0,
        coverageSha256=data.sha((OUT/'complete-protocol-coverage.json').read_bytes()),coverageSessionSchemaVectors=schema_vectors,
        allProtocolPhysicalMainClasses=len(prepared['completeProtocolMainClasses']),coverageScope='COMPLETE_PROTOCOL_ARTIFACT_PER_SEPARATE_EXEC_WITH_NONEXECUTABLE_PACKAGE_METADATA',
        analyzedClassesPerLocale=len(measured[0]['completeProtocolClasses']),nonExecutablePackageMetadataPerLocale=7,
        metadataRecoveryOnly=True,packageMetadataNegativeVectors=5,originalFailedPost='PG10742',diagnostic='PG10743',
        mainClassesUnchanged=1843,totalTestClasses=1962,otherTestClassesUnchanged=1962-len(changed),physicalTestClassesChanged=len(changed),
        changedTestClasses=[dict(module=m,entry=p) for m,p in changed],sourceChanges=plan['sourceChanges'],
        prohibitedLoadedProductClasses=0,probeHitsOutsideProtocol=0,oldExecUnion=False,wholeJavaCoverage100=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,testExecutions=4,uniqueMethods=2,completeClasses=len(prepared['completeProtocolMainClasses']),
        counters=[dict(locale=m['locale'],bundle=m['bundleCounters']) for m in measured],manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()

