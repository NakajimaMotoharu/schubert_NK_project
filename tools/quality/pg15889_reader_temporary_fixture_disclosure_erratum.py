"""BUG2151: append a narrow effect-disclosure correction, never mutate old evidence or rerun PT."""
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15854_scenario_record_reader_four_pt as reader

REG='PG15876-current2055-maintenance-records-registry-v1'
REG_SHA='e297179a1c121c3842432940be4f8a85d35de820c379fef7cf3661af79aa4389'
READER='PG15856-scenario-record-reader-four-post-v1'
READER_SHA='d6f4922e2f6096a34a4e0dbe0a533c029960978dcf5e11c18ceb4a5fc40f8913'
OUT=data.BASE/'PG15889-reader-temporary-fixture-disclosure-erratum-v1'
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    registry=data.read_checked(data.BASE/REG/'manifest.json',REG_SHA);pairs={}
    def add(name,pin):
        require(re.fullmatch(r'PG[0-9]+-[a-z0-9-]+',name) is not None and re.fullmatch('[0-9a-f]{64}',pin) is not None,'explicit public post reference only')
        require(name not in pairs or pairs[name]==pin,'unique fixed manifest reference');pairs[name]=pin
    for r in registry['originalPostReferences']:add(r['name'],r['sha256'])
    for u in registry['fullSourceUnits'].values():add(u['post'],u['postSha256'])
    def walk(value):
        if isinstance(value,dict):
            if isinstance(value.get('name'),str) and 'sha256' in value:add(value['name'],value['sha256'])
            for v in value.values():walk(v)
        elif isinstance(value,list):
            if len(value)==2 and isinstance(value[0],str) and re.fullmatch(r'PG[0-9]+-[a-z0-9-]+',value[0]) and isinstance(value[1],str) and re.fullmatch('[0-9a-f]{64}',value[1]):add(value[0],value[1])
            else:
                for v in value:walk(v)
    for section in ['additionalQualificationReferences','additionalScopeReferences','jointQualificationReferences','resourceOnlyReferences']:walk(registry[section])
    checked=[];positive={};old=None
    for name,pin in sorted(pairs.items()):
        m=data.read_checked(data.BASE/name/'manifest.json',pin)
        require(m['actualExit']==0,'only actual successful reference, no begin/failed results')
        value=m.get('testOwnNewSlotPublicEvidenceWrites')
        checked.append(dict(name=name,sha256=pin,fieldPresent='testOwnNewSlotPublicEvidenceWrites' in m,reportedOwnSlotOutput=value,source=m['source']))
        if value is True:positive[name]=m
        if name==READER:old=m;require(pin==READER_SHA,'exact original reader post')
    require(old is not None and set(positive)=={'PG15460-public-value-eighteen-post-v1',READER,'PG15872-maintenance-records-eight-post-v1'},'all actual positive output-field references accounted')
    p=positive['PG15460-public-value-eighteen-post-v1']
    require(p['publicTestOutputs'] and len(p['publicTestOutputs'])==2 and all(v['publicFixtureOnly'] is True for v in p['publicTestOutputs'].values()),'two verified explicit own public summary outputs, nonapplicable')
    maintenance=data.read_checked(data.BASE/'PG15874-maintenance-records-eight-independent-v1/manifest.json','8f35acabc3b04a38a10f4958657fa894c3651e592e0dab5a2985756b1cc5fe4e')
    require(maintenance['actualExit']==0 and maintenance['publicTraceOracleCount']==4 and maintenance['testOwnedCwdTraceWrites'] is True,'four literal own CWD outputs, nonapplicable')
    text=reader.TESTS['ScenarioRecordReaderTest'].read_text()
    require(data.sha(text.encode())==reader.PINS['ScenarioRecordReaderTest'] and '@TempDir Path root;' in text and 'root.resolve(' in text and 'Path.of(' not in text and 'target/' not in text,'reader body owns temporary fixture, no explicit slot evidence path')
    require(old['testOwnedTemporaryFileIo'] is old['testOwnedTempFilesCleanupByJunit'] is old['testOwnNewSlotPublicEvidenceWrites'] is True and old['actualFilesOpenedByProduct'] is False,'old report/actual fixture domain and borrowed channel remain distinguished')
    effective=dict(effectiveTestOwnNewSlotPublicEvidenceWrites=False,effectiveTestOwnedTemporaryFixtureWrites=True,effectiveTestOwnedTemporaryFileIo=True,effectiveTestOwnedTempFilesCleanupByJunit=True,actualTemporaryPathRecorded=False,interpretation='ORIGINAL_TEST_BODY_TEMPORARY_FIXTURES_NOT_EXPLICIT_SLOT_EVIDENCE_OUTPUT; POST_EXECUTION_SCOPE_NOT_EACH_CLASS_EFFECT')
    verify(old['invocation']);verify(maintenance['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'reference-field-audit.json',checked)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=reader.SOURCE,invocation=invocation,bug='BUG2151',horizontal='YKT1898',registryManifestSha256=REG_SHA,originalPostManifest=READER,originalPostSha256=READER_SHA,reportedOriginalFieldValue=True,effectiveDisclosure=effective,checkedPublicReferenceCount=len(checked),positiveReferenceCount=3,affectedReferenceCount=1,nonApplicableReferences=['PG15460-public-value-eighteen-post-v1','PG15872-maintenance-records-eight-post-v1'],unreviewedPositiveReferences=[],fieldAuditSha256=data.sha((OUT/'reference-field-audit.json').read_bytes()),originalCountersSourceRunCasesAndCryptoUnchanged=True,originalManifestAndToolUnchanged=True,actualTemporaryPathInferred=False,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,checkedPublicReferences=len(checked),positive=3,affected=1,productReexecutions=0)))
if __name__=='__main__':main()
