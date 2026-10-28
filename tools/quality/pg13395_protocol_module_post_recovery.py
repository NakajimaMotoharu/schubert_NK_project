"""Independent current whole Protocol106 XML/full176 physical/JaCoCo/metadata/static/owner binding."""
import copy
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
import pg13392_protocol_module_verify as original
import pg9666_pagination_static as runner
from host_tool_invocation import capture,verify
from classfile_code_metadata import decode
from trace_owner_join import canonical

RAW = '211386098090e72e7e2ea4baf536d24a9c50d1144a6151a0f80e36e2f733a9ab'
RUN = original.SLOT
OUT = data.BASE/'PG13395-protocol-module-post-recovery-v2'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13395-protocol-module-post-recovery-v2'
PREFIX = 'dev/codex/schubert/nk/protocol/'
INTERFACES = {PREFIX+'layout/'+name for name in ['FieldValue','LayoutPayload','PayloadData','PayloadRecord']}|{PREFIX+'layout/semantic/'+name for name in ['ProtocolId','WireEnum']}
SWITCHES = {PREFIX+name:count for name,count in [('codec/PayloadCodec$1',1),('file/MediaDescriptorValidator$1',1),('layout/FieldDefinition$1',1),('layout/LayoutFieldCatalog$1',2)]}

def assess(value):
    assert value['source'] == original.SOURCE and value['actualExit'] == 0 and value['ptComplete'] is True and not value['stage']['timedOut']
    assert len(value['expectedCatalog']) == len(value['suites']) == 23 and sum(map(len,value['expectedCatalog'].values())) == len(value['cases']) == value['productTestsExecuted'] == 106
    assert {(r['classname'],r['method']) for r in value['cases']} == {(name,method) for name,methods in value['expectedCatalog'].items() for method in methods}
    assert all(r['result'] == 'PASS' and not r['nonPass'] for r in value['cases']) and all(row == dict(tests=len(value['expectedCatalog'][name]),failures=0,errors=0,skipped=0) for name,row in value['suites'].items())
    assert set(value['coverageCounters']) == {'LINE','METHOD','CLASS','BRANCH'} and all(v['missed'] == 0 and v['covered'] > 0 for v in value['coverageCounters'].values())
    assert value['mainClassHashes'] == value['normalMainClassHashes'] and len(value['mainClassHashes']) == value['mainPhysical'] == 176 and value['allProtocolMainByteIdentical']
    assert value['priorCoverageTransferred'] is False and value['newTestIds'] == value['newAccepted'] == 0 and value['formalUpdated'] is False and value['whole451Accepted'] is False

def counter_schema(actual,xml):
    kinds = {'LINE','METHOD','CLASS','BRANCH'};assert set(actual) == kinds and set(xml) <= kinds
    for kind,row in actual.items():
        assert set(row) == {'missed','covered'} and all(type(v) is int and v >= 0 for v in row.values())
        if kind in xml:assert row == xml[kind]
        else:assert row == dict(missed=0,covered=0)
    return sorted(kinds-set(xml))

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    value = data.read_checked(original.OUT/'manifest.json',RAW);assert data.sha((RUN/'manifest.safe.json').read_bytes()) == RAW;assess(value)
    normal = data.read_checked(data.BASE/'PG13362-api-maintenance-literal-v1/manifest.json',original.NORMAL_PIN);assert normal['source'] == original.SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    begin = json.loads((RUN/'begin.safe.json').read_bytes());assert data.sha((RUN/'begin.safe.json').read_bytes()) == value['beginSha256']
    assert begin['source'] == original.SOURCE and '-Djacoco.sessionId='+original.SESSION in begin['command'] and '-Djacoco.append=false' in begin['command']
    assert begin['expectedCatalog'] == value['expectedCatalog'] and begin['inputHashes'] == normal['begin']['inputHashes'] == value['sourceInputHashes']
    snapshot = RUN/'snapshot';target = snapshot/original.MODULE/'target';hashes = value['sourceInputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == sha for p,sha in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in begin['dependencyJarHashes'].items())
    assert all(data.sha((target/path).read_bytes()) == sha for path,sha in value['reports'].items())
    actual = []
    for filename,sha in value['xmlHashes'].items():
        file = target/'surefire-reports'/filename;assert data.sha(file.read_bytes()) == sha;node = ET.parse(file).getroot();name = node.get('name')
        assert value['suites'][name] == {key:int(node.get(key,'0')) for key in ['tests','failures','errors','skipped']}
        for case in node.findall('testcase'):
            assert not [x for x in case if x.tag not in ['system-out','system-err']];actual.append((case.get('classname'),case.get('name').removesuffix('()')))
    assert len(actual) == len(set(actual)) == 106 and set(actual) == {(r['classname'],r['method']) for r in value['cases']}
    negatives = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('exit',lambda x:x.update(actualExit=1)),('failed',lambda x:x['cases'][0].update(result='NOT_PASS')),('duplicate',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),
        ('coverage',lambda x:x['coverageCounters']['BRANCH'].update(missed=1)),('missing-physical',lambda x:x['mainClassHashes'].pop(next(iter(x['mainClassHashes'])))),('union',lambda x:x.update(priorCoverageTransferred=True)),('formal',lambda x:x.update(formalUpdated=True))]:
        bad = copy.deepcopy(value);change(bad)
        try:assess(bad)
        except AssertionError:negatives.append(label)
        else:raise AssertionError('false whole module qualification accepted')
    report = ET.parse(target/'site/jacoco/jacoco.xml').getroot();xml_rows = {c.get('name'):c for package in report.findall('package') for c in package.findall('class')};assert len(xml_rows) == 169
    total_counters = {x.get('type'):dict(missed=int(x.get('missed')),covered=int(x.get('covered'))) for x in report.findall('counter') if x.get('type') in value['coverageCounters']};assert total_counters == value['coverageCounters']
    classes = target/'classes';physical = {str(p.relative_to(classes)):data.sha(p.read_bytes()) for p in classes.rglob('*.class')};assert physical == value['mainClassHashes']
    metadata = {};executable = set();models = {};sources = set()
    for entry,sha in sorted(physical.items()):
        name = entry[:-6];model = decode((classes/entry).read_bytes(),entry);models[name] = model;path = original.MODULE+'/src/main/java/'+str(Path(entry).parent/model['sourceFile']);assert path in hashes;sources.add(path)
        node = xml_rows.get(name);counters = {} if node is None else {x.get('type'):dict(missed=int(x.get('missed')),covered=int(x.get('covered'))) for x in node.findall('counter')}
        if counters.get('CLASS',dict(missed=0,covered=0))['covered'] > 0:executable.add(name);continue
        assert not any(v['missed'] or v['covered'] for v in counters.values())
        if name.endswith('/package-info'):
            assert model['fields'] == 0 and model['methods'] == [] and model['flags'] & 0x0200;reason = 'PACKAGE_ANNOTATION_METADATA_NO_METHOD_OR_FIELD'
        elif name in INTERFACES:
            assert model['fields'] == 0 and model['flags'] & 0x0200 and all(not m['hasCode'] and m['flags'] & 0x0400 for m in model['methods']);reason = 'ABSTRACT_INTERFACE_NO_EXECUTABLE_CODE'
        else:
            assert name in SWITCHES and model['flags'] & 0x1000 and model['fields'] == SWITCHES[name] and [(m['name'],m['descriptor'],m['flags']) for m in model['methods']] == [('<clinit>','()V',8)];reason = 'JAVAC_GENERATED_ENUM_SWITCH_OFFICIAL_FILTER_NOT_HAND_EXCLUSION'
        metadata[name] = dict(reason=reason,classSha256=sha,sourcePath=path,sourceSha256=hashes[path],classModel=model,officialCounter=counters)
    package_infos = {name for name in metadata if name.endswith('/package-info')};assert len(package_infos) == 7 and set(metadata)-package_infos == INTERFACES|set(SWITCHES) and len(metadata) == 17 and len(executable) == 159
    assert set(physical) == {name+'.class' for name in executable|set(metadata)} and set(xml_rows) == executable|(set(metadata)-package_infos)
    sb = ET.parse(target/'spotbugsXml.xml').getroot();stats = [x.get('class') for x in sb.iter('ClassStats')]
    assert not list(sb.iter('BugInstance')) and not list(sb.iter('MissingClass')) and not list(sb.iter('Error')) and len(stats) == len(set(stats)) == int(sb.find('FindBugsSummary').get('total_classes')) == 176
    assert set(stats) == {entry[:-6].replace('/','.') for entry in physical}
    prior = data.read_checked(data.BASE/'PG13368-api-maintenance-literal-v1/manifest.json','ae3a6e54fc0475f388e947a533af5575e901778fd566f52d7b35b43b937b3186');registry = {r['path']:r for r in prior['sourceRows']}
    invpath = data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';invraw = invpath.read_bytes();logical = {r['path']:r for r in json.loads(invraw)['artifacts']}
    all_java = {p for p in hashes if p.startswith(original.MODULE+'/src/') and '/java/' in p and p.endswith('.java')};assert len(sources) == 165 and len(all_java) == 189;owners = {}
    for path in sorted(all_java):
        row = canonical(path,logical)
        if row['canonicalOwner'] is None:
            registered = registry[path];assert registered['sha256'] == hashes[path];row = {key:registered[key] for key in ['canonicalOwner','canonicalCostOwner']}
        assert row['canonicalOwner'] and row['canonicalCostOwner'];owners[path] = dict(sha256=hashes[path],**row,currentQualificationNotInheritedFromOwnership=True)
    runtime = data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882');tool_slot = data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit = tool_slot/'audit';compiled = runtime['reusedCompiledClasses'];tools = runtime['toolAndDependencyHashes']
    assert all(data.sha((audit/name).read_bytes()) == sha for name,sha in compiled.items()) and all(data.sha(Path(p).read_bytes()) == sha for p,sha in tools.items())
    cp_receipt = data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b');cp = cp_receipt['command'][2];entries = cp.split(os.pathsep);assert entries[0] == str(audit) and len(entries) == 5 and set(entries[1:]) == {p for p in tools if p.endswith('.jar')}
    failed = data.ROOT.parent/'pgpt-runs/PG379/pg13394-protocol-module-post-v1';component = failed/'full-protocol-physical'
    old_begin = data.read_checked(failed/'begin.safe.json','7f33a65e7f7807c8b4a44ec4e2b19afc42bc55243e232c1f6bdee0cbea44e9d8')
    assert old_begin['source'] == original.SOURCE and old_begin['originalManifestSha256'] == RAW and old_begin['physicalClasses'] == physical and old_begin['metadata'] == metadata and old_begin['owners'] == owners and old_begin['expectedExecutable'] == sorted(executable)
    assert all(data.sha((component/entry).read_bytes()) == sha for entry,sha in physical.items())
    assert not (data.BASE/'PG13394-protocol-module-post-v1').exists()
    receipt_pins = {'session-identity':'2529a5d7091b4fa78cae36a660cb10fa393f1689cbcc7aa084adfccb9ebb5d5a','coverage-audit':'6cfbdb526bf0cb8c6b6b7c41eae61d335b45e9eaa24d78a04750d5addcdded5f'}
    stages = [data.read_checked(failed/(label+'-exit.safe.json'),pin) for label,pin in receipt_pins.items()]
    expected_commands = [[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',cp,'CoverageSessionIdentity',str(target/'jacoco.exec'),original.SESSION],[str(runner.TC/'jdk-25.0.4/bin/java'),'-cp',cp,'ComponentCoverageAudit',str(target/'jacoco.exec'),str(component),*sorted(executable),*['--metadata='+name for name in sorted(set(metadata)-package_infos)]]]
    for label,stage,command in zip(receipt_pins,stages,expected_commands,strict=True):
        assert stage['actualExit'] == 0 and not stage['timedOut'] and stage['command'] == command
        assert data.sha((failed/(label+'.stdout')).read_bytes()) == stage['stdoutSha256'] and data.sha((failed/(label+'.stderr')).read_bytes()) == stage['stderrSha256']
    assert (failed/'session-identity.stdout').read_text() == 'OWNED_COVERAGE_SESSION_MATCH\t1\n'
    SLOT.mkdir();data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,originalFailedPost=dict(actualExit=1,entrySha256='3d02b71e71f275076c2d124c519f9c6de4b8f12c486385f481971e8c430dfebd',beginSha256='7f33a65e7f7807c8b4a44ec4e2b19afc42bc55243e232c1f6bdee0cbea44e9d8'),recoveredSuccessfulMetadataReceipts=receipt_pins,productTestsReexecuted=0,metadataCommandsReexecuted=0))
    coverage = {}
    for line in (failed/'coverage-audit.stdout').read_text().splitlines():
        fields = line.split('\t')
        if fields[0] == 'CLASS':coverage[fields[1]] = dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
    assert set(coverage) == executable
    totals = {kind:dict(missed=sum(r['counters'][kind]['missed'] for r in coverage.values()),covered=sum(r['counters'][kind]['covered'] for r in coverage.values())) for kind in value['coverageCounters']};assert totals == total_counters
    zero_omissions = {}
    for name,row in coverage.items():
        xml_counters = {x.get('type'):dict(missed=int(x.get('missed')),covered=int(x.get('covered'))) for x in xml_rows[name].findall('counter') if x.get('type') in totals}
        omitted = counter_schema(row['counters'],xml_counters)
        if omitted:zero_omissions[name] = omitted
    assert len(zero_omissions) == 119 and all(v == ['BRANCH'] for v in zero_omissions.values())
    example = {kind:dict(missed=0,covered=0 if kind == 'BRANCH' else 1) for kind in ['LINE','METHOD','CLASS','BRANCH']};example_xml = {k:copy.deepcopy(v) for k,v in example.items() if k != 'BRANCH'};assert counter_schema(example,example_xml) == ['BRANCH']
    schema_negatives = []
    for label,change in [('positive-omission',lambda a,x:x.pop('LINE')),('omitted-positive-branch',lambda a,x:a['BRANCH'].update(covered=1)),('wrong-present-value',lambda a,x:x['METHOD'].update(covered=2)),('unknown-kind',lambda a,x:x.update(UNKNOWN=dict(missed=0,covered=0)))]:
        a,x = copy.deepcopy(example),copy.deepcopy(example_xml);change(a,x)
        try:counter_schema(a,x)
        except AssertionError:schema_negatives.append(label)
        else:raise AssertionError('missing/non-equivalent positive counter accepted')
    assert data.sha(invpath.read_bytes()) == data.sha(invraw) and all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items()) and all(data.sha((classes/entry).read_bytes()) == sha for entry,sha in physical.items());verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=original.NORMAL_PIN,tests=106,suites=23,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,
        xmlHashes=value['xmlHashes'],cases=value['cases'],physicalMain=176,executableMain=159,naturalZeroPhysical=17,metadata=metadata,javaSourceBindings=owners,mainJavaSources=165,mainAndTestJavaSources=189,inventoryReferenceSha256=data.sha(invraw),registryReferenceSha256='ae3a6e54fc0475f388e947a533af5575e901778fd566f52d7b35b43b937b3186',registryChanged=False,
        physicalClassHashes=physical,executable=coverage,totals=totals,xmlRows=169,packageAnnotationNotEmittedByOfficialReport=sorted(package_infos),coverageSession=original.SESSION,singleSession=True,crcMismatch=0,execSha256=value['reports']['jacoco.exec'],spotbugs=dict(classes=176,bugs=0,missing=0,errors=0),stages=stages,
        independentMetadataNegativeVectors=len(negatives),negativeLabels=negatives,xmlCounterSchemaNegativeLabels=schema_negatives,zeroTotalCounterXmlOmissions=zero_omissions,recoveredSuccessfulMetadataReceipts=receipt_pins,originalPostFailure=dict(actualExit=1,entrySha256='3d02b71e71f275076c2d124c519f9c6de4b8f12c486385f481971e8c430dfebd',outputRetained=True),metadataCommandsReexecuted=0,officialFiltersUnchanged=True,manualCounterExclusions=[],sourceCoverageOrOldPtInferredFromOwner=False,priorProductCoverageTransferred=False,productTestsReexecutedByPost=0,scope='CURRENT_PROTOCOL_MODULE_ONLY_NOT_WHOLE_PROJECT',whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=106,suites=23,physical=176,executable=159,metadata=17,totals=totals,ownerUnknown=0,singleSession=True,crcMismatch=0)))

if __name__ == '__main__':main()
