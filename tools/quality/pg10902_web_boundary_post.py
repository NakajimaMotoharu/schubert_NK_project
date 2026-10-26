"""Independent current8 Scenario executions, four numeric boundary constants source inverse and complete artifact counters; no PT replay."""
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

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
WORK = data.ROOT.parent/'pgpt-runs/PG379'
RUN = WORK/'pg10898-web-boundary-line-host-v1'
SLOT = WORK/'pg10902-web-boundary-post-v1'
OUT = data.BASE/'PG10902-web-boundary-post-v1'


def require_package_metadata(name,model):
    if not name.endswith('/package-info.class') or model != dict(flags=5632,sourceFile='package-info.java',fields=0,methods=[]):
        raise ValueError('exact no-member package annotation metadata, not arbitrary missing class')



def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared_path = data.BASE/'PG10896-web-boundary-line-preflight-v1/manifest.json'
    prepared = data.read_checked(prepared_path,'9fbf2f8d8826c2917e2830cafb505eae1a5ffd0913396a2edd1f99ec156dba55')
    host_path = data.BASE/'PG10898-web-boundary-line-host-v1/manifest.json'
    host = data.read_checked(host_path,'5b0354fdf828894823e92c4dd849b8453c62b29531eff16d89ff41d96fb7d455')
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    assert host['source'] == prepared['source'] == normal['source'] == SOURCE
    assert host['actualExit'] == prepared['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert len(host['localeRuns']) == 1 and host['observedTestExecutions'] == 8 and host['uniqueMethods'] == 8
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in host['stages'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**prepared['dependencyHashes'],**prepared['physicalTestFiles']}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    prepared['completeWebMainClasses'] = prepared['mainClassCatalogs']['web']
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
        assert Counter(actual) == expected and len(xmls) == 1 and xmls == row['xmlHashes']
        assert (folder/'xml/summary.safe.txt').read_text() == 'found=8;started=8;succeeded=8;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
        assert data.sha((folder/'jacoco.exec').read_bytes()) == row['execSha256']
        log = (folder/'classload-metadata.log').read_bytes()
        assert data.sha(log) == row['loadedClassMetadataSha256']
        loaded = set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',log.decode()))
        forbidden = sorted(n for n in loaded if (n.startswith('dev.codex.schubert.nk.') and not n.startswith(('dev.codex.schubert.nk.protocol.','dev.codex.schubert.nk.web.')))
            or n.startswith(('org.postgresql.','org.apache.activemq.')))
        assert loaded and not forbidden
        assert 'dev.codex.schubert.nk.web.config.WebMvcConfiguration' in loaded
    for name,text in prepared['expectedTraceText'].items():
        path = Path(prepared['traceParent'])/name
        assert path.read_bytes() == text.encode() and not path.is_symlink()
        assert host['ownedPublicTraces'][name]['sha256'] == data.sha(path.read_bytes())
    SLOT.mkdir(mode=0o700)
    classes = SLOT/'complete-main'
    classes.mkdir()
    with zipfile.ZipFile(prepared['moduleJars']['web']) as jar:
        for name,digest in prepared['completeWebMainClasses'].items():
            raw = jar.read(name)
            assert data.sha(raw) == digest
            file = classes/name
            file.parent.mkdir(parents=True,exist_ok=True)
            with file.open('xb') as stream:
                stream.write(raw)
    catalog = SLOT/'complete-main-catalog.txt'
    with catalog.open('x') as stream:
        stream.write(''.join(name+'\n' for name in sorted(prepared['completeWebMainClasses'])))
    helper = data.ROOT/'tools/quality/architecture/WebViewArtifactCoverageMeasure.java'
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
                assert len(parts) == 2 and parts[1]+'.class' in prepared['completeWebMainClasses'] and parts[1] not in package_metadata
                package_metadata.add(parts[1])
            elif parts[0] == 'CLASS':
                assert len(parts) == 3 and parts[1]+'.class' in prepared['completeWebMainClasses'] and parts[1] not in units
                current = dict(classCrc64=parts[2],counters={})
                units[parts[1]] = current
            elif parts[0] == 'BUNDLE':
                assert parts == ['BUNDLE','COMPLETE_WEB_ARTIFACT'] and not bundle
                current = dict(counters=bundle)
            else:
                assert len(parts) == 4 and parts[0] == 'COUNTER' and current is not None
                _,kind,missed,covered = parts
                assert kind not in current['counters']
                current['counters'][kind] = dict(missed=int(missed),covered=int(covered))
        assert not set(units)&package_metadata
        assert {n+'.class' for n in set(units)|package_metadata} == set(prepared['completeWebMainClasses'])
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
        measured.append(dict(locale=row['locale'],session=session,completeWebClasses=units,nonExecutablePackageMetadata=package_models,bundleCounters=bundle,
            probeHitsOutsideWebProtocol=0,execSha256=row['execSha256'],wholeJavaCoverage100=False,oldExecUnion=False))
    previous = data.read_checked(data.BASE/'PG10874-web-boundary-complete-six-compile-v1/manifest.json',
        '79ef29ca4a6af3a8f9a866feaceaeb73d5f16906c7d9db02d85d916e8d0e509f')
    assert jar_classes(previous) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    old_test,new_test = test_classes(previous),test_classes(normal)
    assert set(old_test) == set(new_test) and len(new_test) == 1962
    changed = sorted(k for k in new_test if old_test[k] != new_test[k])
    plan = data.read_checked(data.BASE/'PG10891-web-boundary-line-source-post-v1/manifest.json',
        '2623f20868d71b0a220e26c736b7861a5099c40b0f1670c49871bc303230f55c')
    proof = data.read_checked(data.BASE/'PG10891-web-boundary-line-source-post-v1/manifest.json',
        '2623f20868d71b0a220e26c736b7861a5099c40b0f1670c49871bc303230f55c')
    assert proof['sourceChanges'] == plan['sourceChanges'] and proof['metadataNegativeVectors'] == 12
    assert all(data.sha((data.ROOT/r['path']).read_bytes()) == r['sha256'] for r in plan['sourceChanges'])
    allowed_sources = {Path(r['path']).name for r in plan['sourceChanges'] if previous['begin']['inputHashes'][r['path']] != r['sha256']}
    observed_sources = set()
    for module,entry in changed:
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/entry
        source_file = decode(file.read_bytes(),entry)['sourceFile']
        assert module == 'web' and source_file in allowed_sources
        observed_sources.add(source_file)
    assert observed_sources == allowed_sources and len(allowed_sources) == 1
    static_path = data.BASE/'PG10894-web-boundary-line-static-v1/manifest.json'
    static = data.read_checked(static_path,'7f77e05354f41debaaf0a7b767a2fc1acb55c863b54771e9a439418e7cf2d140')
    assert static['source'] == SOURCE and static['actualExit'] == 1
    assert static['reports']['pmd']['findings'] == 17 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    for label in ('pmd','checkstyle'):
        assert data.sha((static_path.parent/(label+'.xml')).read_bytes()) == static['reports'][label]['sha256']
    static_nodes = [n for n in ET.parse(static_path.parent/'pmd.xml').getroot().iter() if n.tag.rpartition('}')[2] == 'violation']
    assert len(static_nodes) == 17 and not any(n.get('rule') == 'AvoidDuplicateLiterals' for n in static_nodes)
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
    context_path = data.BASE/'PG10900-web-view-context-v1/manifest.json'
    context = data.read_checked(context_path,'6c250409c3b0f780be51558e623abe2a8c9035930ab7d6dc773c1cea361e1fc5')
    assert context['source'] == SOURCE and context['actualExit'] == 0 and context['rawManifestSha256'] == data.sha(static_path.read_bytes())
    assert context['rawPmd'] == context['concreteNotApplicable'] == 17 and context['unclassified'] == context['applicableUnresolved'] == 0
    contexts = data.read_checked(context_path.parent/'contexts.json',context['contextsSha256'])
    assert len(contexts) == len({r['originalFindingId'] for r in contexts}) == 17
    assert all(r['source'] == SOURCE and r['sourceSha256'] == normal['begin']['inputHashes'][r['path']] for r in contexts)
    historical_path = data.BASE/'PG10868-web-boundary-host-v1/manifest.json'
    historical = data.read_checked(historical_path,'d0d9d5a60c89e8c174cef2f0617da367466797eb31faff44ec83c1908e68e3c9')
    assert historical['actualExit'] == 0 and historical['source'] == 'cf58908c6494b6c61995146ca6f176ecc50c48a5' and historical['observedTestExecutions'] == 16
    historical_type = 'dev.codex.schubert.nk.web.view.LogSearchTemplateTest'
    historical_xml = WORK/'pg10868-web-boundary-host-v1/jp/xml'/('TEST-'+historical_type+'.xml')
    assert data.sha(historical_xml.read_bytes()) == historical['localeRuns'][0]['xmlHashes'][historical_xml.name]
    hx = ET.parse(historical_xml).getroot()
    assert int(hx.get('tests')) == 8 and all(int(hx.get(k)) == 0 for k in ('failures','errors','skipped'))
    assert len(hx.findall('testcase')) == 8 and all(not list(n) and n.get('classname') == historical_type for n in hx.findall('testcase'))
    log_path = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/LogSearchTemplateTest.java'
    assert historical['begin']['sourceInputHashes'][log_path] == normal['begin']['inputHashes'][log_path]
    historical_binding = dict(source=historical['source'],manifestSha256=data.sha(historical_path.read_bytes()),xmlSha256=data.sha(historical_xml.read_bytes()),
        logMethods=8,currentLogSourceBytesUnchanged=True,reassignedToCurrentSource=False,addedToCurrentExecutions=False)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'complete-web-coverage.json',measured)
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
        contextManifestSha256=data.sha(context_path.read_bytes()),historicalUnchangedLogSource=historical_binding,originalHostManifestSha256=data.sha(host_path.read_bytes()),staticManifestSha256=data.sha(static_path.read_bytes()),staticRawGate=1,remainingPmd=17,
        webFourCounters100=all(all(c['missed'] == 0 and c['covered'] > 0 for c in row['bundleCounters'].values()) for row in measured),testsPerLocale=8,localeRuns=1,testExecutions=8,uniqueMethods=8,newTestMethods=0,
        coverageSha256=data.sha((OUT/'complete-web-coverage.json').read_bytes()),coverageSessionSchemaVectors=schema_vectors,
        allWebPhysicalMainClasses=len(prepared['completeWebMainClasses']),coverageScope='COMPLETE_WEB_ARTIFACT_PER_SEPARATE_EXEC_WITH_NONEXECUTABLE_PACKAGE_METADATA',
        analyzedClassesPerLocale=len(measured[0]['completeWebClasses']),nonExecutablePackageMetadataPerLocale=len(measured[0]['nonExecutablePackageMetadata']),
        metadataRecoveryOnly=False,packageMetadataNegativeVectors=5,independentSourceNegativeVectors=12,staticFindingsCorrected=2,
        mainClassesUnchanged=1843,totalTestClasses=1962,otherTestClassesUnchanged=1962-len(changed),physicalTestClassesChanged=len(changed),
        changedTestClasses=[dict(module=m,entry=p) for m,p in changed],sourceChanges=plan['sourceChanges'],
        prohibitedLoadedProductClasses=0,probeHitsOutsideWebProtocol=0,oldExecUnion=False,wholeJavaCoverage100=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,testExecutions=8,uniqueMethods=8,completeClasses=len(prepared['completeWebMainClasses']),
        counters=[dict(locale=m['locale'],bundle=m['bundleCounters']) for m in measured],manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
