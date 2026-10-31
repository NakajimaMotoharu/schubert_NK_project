"""Independent resource-five evidence join, not Production coverage or service admission."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16712_supplementary_unit_template_original_five_pt import SOURCE,NAME,TEST,TEST_SHA,SLOT
POST=('PG16714-supplementary-unit-template-original-five-post-v1','da1df35232073867a24c00569710cb3644fc45c9ea5b0035bd465d42cbc6b67b')
RAW=('PG16712-supplementary-unit-template-original-five-pt-v1','77d80b8fa7b515c3ae2b7993a26bf769aa7f0801e486c6dcf7067c4afd97db52')
OUT=data.BASE/'PG16716-supplementary-unit-template-original-five-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [POST,RAW]]
    require(raw['source']==SOURCE and raw['actualExit']==0 and data.sha(TEST.read_bytes())==TEST_SHA,'original same-source whole Test')
    methods=['unitSup001BackupAllDeclaredContracts','unitSup002AdminDisabledAndDedicatedAllDeclaredContracts','unitSup003CaddyStartupResetsAndFixedDaemonAbi','unitSup004CaddyStopOnlyDeclaredOverrides','unitSup005IndependentOracleMutationCanaries']
    text=TEST.read_text();require(set(re.findall(r'@Test\s+void\s+(\w+)\(',text))==set(methods),'all original whole method declarations')
    actual=[]
    for name,h in raw['xmlHashes'].items():
        blob=(SLOT/'xml'/name).read_bytes();require(data.sha(blob)==h,'original actual XML');root=ET.fromstring(blob)
        require(root.get('tests')=='5' and all(root.get(k)=='0' for k in ['failures','errors','skipped']),'actual FES0')
        for c in root.findall('testcase'):require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==5 and set(actual)=={(NAME,n) for n in methods},'original five exact identities')
    names=['schubert-nk-backup.service.template','schubert-nk-bootstrap-admin.service.template','caddy.service.d/schubert-nk-startup-policy.conf','caddy.service.d/schubert-nk-stop-policy.conf']
    inputs={'src/deployment/systemd/'+n:data.sha((data.ROOT/'src/deployment/systemd'/n).read_bytes()) for n in names}
    copies={str(SLOT/'fresh-test-classes/systemd'/n):inputs['src/deployment/systemd/'+n] for n in names}
    definitions={'systemd/'+n:str(SLOT/'fresh-test-classes/systemd'/n) for n in names}
    fields=dict(actualExit=0,source=SOURCE,originalManifestSha256=RAW[1],tests=5,suites=1,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=raw['sessionIdentity'],singleSession=True,metadataNegativeVectors=20,independentOracleVectors=5,publicResourceInputs=inputs,publicResourceCopies=copies,classpathDefinitions=definitions,ownSyntaxParserInvocationsDeclared=0,actualManagerServiceActions=0,allMainPhysical=1843,productionMainRecordsObserved=[],productionMainTrueProbeHits=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,mainCrcQualification='NOT_APPLICABLE_NO_MAIN_EXECUTION',passiveCounterRole='TEST_CODE_ONLY_NOT_MAIN_COVERAGE',actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualCredentialValuesUsed=False,actualSecretKeysLoaded=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    classes={'dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest','dev/codex/schubert/nk/batch/platform/SupplementaryUnitTemplateTest$Template'}
    def contract(value):
        require(all(k in value and type(value[k]) is type(v) and wire(value[k])==wire(v) for k,v in fields.items()),'exact typed independent resource/effect/no-coverage contract')
        require(set(value['testPhysicalHashes'])==set(value['testCrcIdentityClasses'])==classes and value['passiveTestIdentityStage']['actualExit']==0 and value['passiveTestIdentityStage']['timedOut'] is False,'two Test CRCs and actual passive terminal')
    contract(p);labels=[]
    for key,value in fields.items():
        bad=copy.deepcopy(p)
        if type(value) is bool:bad[key]=not value
        elif type(value) is int:bad[key]=value+1
        elif isinstance(value,str):bad[key]='BAD'
        elif value is None:bad[key]=100
        elif isinstance(value,list):bad[key]=['BAD']
        else:bad[key]={}
        require(wire(bad)!=wire(p),'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false resource evidence accepted')
    require(all(data.sha(__import__('pathlib').Path(n).read_bytes())==h for n,h in copies.items()),'same owned public resource bytes')
    for key in ['testPhysicalHashes','testCrcIdentityClasses']:
        bad=copy.deepcopy(p);bad[key]={}
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('missing Test identities')
    for n,h in p['testPhysicalHashes'].items():require(data.sha((SLOT/'fresh-test-classes'/(n+'.class')).read_bytes())==h,'exact actual Test physical bytes')
    inv=data.read_checked(data.BASE/POST[0]/'main-physical-inventory.safe.json',p['mainPhysicalInventorySha256']);require(len(inv)==1843 and all(v['sha256'] for v in inv.values()),'closed no-executed Main inventory')
    require(text.count('rejected(')==13 and all(s in text for s in ['assertFalse(original.equals(mutated), "nonvacuous oracle canary")','assertThrows(AssertionError.class, () -> verify(name, mutated))','assertThrows(NullPointerException.class, () -> parse(null))']),'twelve original independent mutation canaries and null oracle')
    require(len(raw['stages'])==2 and all(s['actualExit']==0 and s['timedOut'] is False for s in raw['stages']),'javac and own JUnit only, no syntax/Unit commands')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleGroups=5,originalMutationCanaries=12,tests=5,suites=1,javaSourceProgramsQualified=0,mainCoverage=None,credentialTargetsAccessed=False,originalTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print('semanticNegativeVectors',len(labels))
if __name__=='__main__':main()
