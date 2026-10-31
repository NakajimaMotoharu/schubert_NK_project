"""Independent resource-five evidence join, not Production coverage or service admission."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16890_public_unit_files_original_fourteen_pt as original
SOURCE=original.SOURCE
SLOT=original.SLOT
POST=('PG16893-public-unit-files-original-fourteen-post-v2','47876c06dd3d76cfbd4a759e6da4eb1470c959d83facdde342aead8eba968a34')
RAW=('PG16890-public-unit-files-original-fourteen-pt-v1','fc790c6a89f4ff1148f8f320a2908b27c14c5540b1d195a846dddba6e2b7b52f')
OUT=data.BASE/'PG16894-public-unit-files-original-fourteen-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [POST,RAW]]
    require(raw['source']==SOURCE and raw['actualExit']==0 and all(data.sha(path.read_bytes())==original.PINS[name] for name,path in original.TESTS.items()),'same-source four original whole Tests')
    methods={name:re.findall(r'@Test\s+void\s+(\w+)\(',path.read_text()) for name,path in original.TESTS.items()}
    require({name:len(v) for name,v in methods.items()}==original.COUNTS and sum(map(len,methods.values()))==14,'all fourteen original declarations')
    actual=[]
    for name,h in raw['xmlHashes'].items():
        blob=(SLOT/'xml'/name).read_bytes();require(data.sha(blob)==h,'original actual XML');root=ET.fromstring(blob)
        require(root.get('tests')==str(original.COUNTS[root.get('name').rpartition('.')[2]]) and all(root.get(k)=='0' for k in ['failures','errors','skipped']),'actual FES0')
        for c in root.findall('testcase'):require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==14 and set(actual)=={(original.PACKAGE+name,n) for name,rows in methods.items() for n in rows},'original five exact identities')
    names=['schubert-nk-api.service.template','schubert-nk-web.service.template','artemis.service','schubert-nk-cleanup.service.template','schubert-nk-expiry-cleanup.service.template','schubert-nk-morning-controller.service.template','schubert-nk-morning.target.template']
    inputs={'src/deployment/systemd/'+n:data.sha((data.ROOT/'src/deployment/systemd'/n).read_bytes()) for n in names}
    repo=SLOT/'candidate';copies={str(repo/n):h for n,h in inputs.items()};definitions={};file_definitions={n:str(repo/n) for n in inputs}
    fields=dict(actualExit=0,source=SOURCE,originalManifestSha256=RAW[1],tests=14,suites=4,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=raw['sessionIdentity'],singleSession=True,metadataNegativeVectors=22,independentOracleVectors=14,publicResourceInputs=inputs,publicResourceCopies=copies,classpathDefinitions=definitions,publicFileDefinitions=file_definitions,repositoryProperty=str(repo),testWorkingDirectory=str(repo/'src/schubert-nk-batch'),ownSyntaxParserInvocationsDeclared=0,actualManagerServiceActions=0,allMainPhysical=1843,productionMainRecordsObserved=[],productionMainTrueProbeHits=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,mainCrcQualification='NOT_APPLICABLE_NO_MAIN_EXECUTION',passiveCounterRole='TEST_CODE_ONLY_NOT_MAIN_COVERAGE',actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualCredentialValuesUsed=False,actualSecretKeysLoaded=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    classes={(original.PACKAGE+n).replace('.','/') for n in original.COUNTS}
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
        else:bad[key]={'_invalid':True} if value=={} else {}
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
    require('-Dnk.pt.repository='+str(repo) in raw['stages'][1]['command'] and raw['stages'][1]['cwd']==str(repo/'src/schubert-nk-batch'),'one own file-resolution root and original unchanged relative paths')
    finite=[]
    for label,pair,expected_count in [('classpath-four',('PG16714-supplementary-unit-template-original-five-post-v1','da1df35232073867a24c00569710cb3644fc45c9ea5b0035bd465d42cbc6b67b'),4),('classpath-one',('PG16746-broker-public-xml-original-four-post-v1','5c37aba56045083bd233f903ce9c71da54881ddd369dd2751cc7d6c4ef15daa5'),1)]:
        old=data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
        require(old['actualExit']==0 and len(old['classpathDefinitions'])==expected_count and old['classpathDefinitions']!={},'BUG2191 finite predecessor has nonempty definitions')
        finite.append(dict(name=pair[0],sha256=pair[1],classification='NONEMPTY_CLASSPATH_DEFINITION_NEGATIVE_NONDEGENERATE',definitionCount=expected_count))
    require(p['publicFileDefinitions']!={} and p['classpathDefinitions']=={} and len(p['publicFileDefinitions'])==7,'current direct-file domain is distinct')
    require(len(raw['stages'])==2 and all(s['actualExit']==0 and s['timedOut'] is False for s in raw['stages']),'javac and own JUnit only, no syntax/Unit commands')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleGroups=14,originalMutationCanaries=0,bug2191FiniteDomainChecks=finite,tests=5,suites=1,javaSourceProgramsQualified=0,mainCoverage=None,credentialTargetsAccessed=False,originalTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print('semanticNegativeVectors',len(labels))
if __name__=='__main__':main()
