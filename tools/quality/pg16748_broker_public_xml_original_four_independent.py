"""Independent resource-five evidence join, not Production coverage or service admission."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16744_broker_public_xml_original_four_pt import SOURCE,NAME,TEST,TEST_SHA,SLOT
POST=('PG16746-broker-public-xml-original-four-post-v1','5c37aba56045083bd233f903ce9c71da54881ddd369dd2751cc7d6c4ef15daa5')
RAW=('PG16744-broker-public-xml-original-four-pt-v1','899e9b99202626863370c08f357abc7e5c340c078a17ddfedf75e96ebfb1fe74')
OUT=data.BASE/'PG16748-broker-public-xml-original-four-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [POST,RAW]]
    require(raw['source']==SOURCE and raw['actualExit']==0 and data.sha(TEST.read_bytes())==TEST_SHA,'original same-source whole Test')
    methods=['globalBrokerAndJournalSettingsMatchTheIndependentOracle','topologyAndTransportAreClosedToTheApprovedSet','addressPoliciesMatchTheIndependentCapacityMatrix','securityRolesMatchTheIndependentAclMatrix']
    text=TEST.read_text();require(set(re.findall(r'void (\w+)\(\)',text))==set(methods+['parseProductionTemplate']) and text.count('@Test')==4,'all original whole method declarations')
    actual=[]
    for name,h in raw['xmlHashes'].items():
        blob=(SLOT/'xml'/name).read_bytes();require(data.sha(blob)==h,'original actual XML');root=ET.fromstring(blob)
        require(root.get('tests')=='4' and all(root.get(k)=='0' for k in ['failures','errors','skipped']),'actual FES0')
        for c in root.findall('testcase'):require(not list(c),'actual PASS');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==4 and set(actual)=={(NAME,n) for n in methods},'original five exact identities')
    names=['broker.xml']
    inputs={'src/deployment/artemis/etc/'+n:data.sha((data.ROOT/'src/deployment/artemis/etc'/n).read_bytes()) for n in names}
    copies={str(SLOT/'fresh-test-classes/public-config'/n):inputs['src/deployment/artemis/etc/'+n] for n in names}
    definitions={'public-config/'+n:str(SLOT/'fresh-test-classes/public-config'/n) for n in names}
    fields=dict(actualExit=0,source=SOURCE,originalManifestSha256=RAW[1],tests=4,suites=1,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=raw['sessionIdentity'],singleSession=True,metadataNegativeVectors=20,parserInputPath=str(SLOT/'fresh-test-classes/public-config/broker.xml'),staticReviewBindingSha256='51fafd6bf403e1e970afb67352ed0828fdeae37ee67671dab33818881cfc24a4',vendorParserJarSha256='4bc0bb2d74e340fbb54d84121f2c52708e00bdad0a84751b9bd4f4b21e03c358',actualBrokerServerStarts=0,actualJmsConnectionsCreated=0,independentOracleVectors=4,publicResourceInputs=inputs,publicResourceCopies=copies,classpathDefinitions=definitions,ownSyntaxParserInvocationsDeclared=1,actualManagerServiceActions=0,allMainPhysical=1843,productionMainRecordsObserved=[],productionMainTrueProbeHits=0,javaSourceProgramsQualified=0,javaCounterCoverageClaimed=False,resourceCounterCoverageClaimed=False,mainCrcQualification='NOT_APPLICABLE_NO_MAIN_EXECUTION',passiveCounterRole='TEST_CODE_ONLY_NOT_MAIN_COVERAGE',actualBrowserActions=0,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualCredentialValuesUsed=False,actualSecretKeysLoaded=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    classes={'dev/codex/schubert/nk/api/messaging/config/ArtemisBrokerConfigurationTest','dev/codex/schubert/nk/api/messaging/config/ArtemisBrokerConfigurationTest$Capacity'}
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
    require(all(v in text for v in ['assertEquals(ADDRESSES, routing.keySet())','assertEquals(expected, actual)','new Capacity(128, 1_000, 896, 9_000)','assertEquals(512 * MIB, configuration.getGlobalMaxSize())']),'independent original topology/global/capacity/ACL oracles')
    plan=data.read_checked(data.BASE/'PG16743-broker-static-review-equivalence-v1/manifest.json','51fafd6bf403e1e970afb67352ed0828fdeae37ee67671dab33818881cfc24a4')
    require(plan['actualExit']==0 and plan['source']==SOURCE and plan['priorProductResultsTransferred'] is False and len(plan['changedPathsOutsideParserScope'])==3 and plan['vendorParserJarSha256']==fields['vendorParserJarSha256'],'unchanged static review only')
    require('-Dbroker.template='+fields['parserInputPath'] in raw['stages'][1]['command'],'actual own public parser input')
    verify(plan['invocation'])
    require(len(raw['stages'])==2 and all(s['actualExit']==0 and s['timedOut'] is False for s in raw['stages']),'javac and own JUnit only, no syntax/Unit commands')
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleGroups=4,originalMutationCanaries=0,tests=4,suites=1,javaSourceProgramsQualified=0,mainCoverage=None,credentialTargetsAccessed=False,originalTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print('semanticNegativeVectors',len(labels))
if __name__=='__main__':main()
