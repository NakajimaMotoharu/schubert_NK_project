"""Independent six new fixed-oracle cases and complete two value Source qualification, no exec union."""
import copy
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14871_protocol_carrier_boundary_post_v2 import owner_role

PIN='87d29dc4e02b03e422270d4f9ebfc5a8b68456804f837c1c338ba1d8b8986696'
POST=data.BASE/'PG14871-protocol-carrier-boundary-six-post-v2'
OUT=data.BASE/'PG14872-protocol-carrier-boundary-independent-v1'
PREFIX='dev/codex/schubert/nk/protocol/layout/'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only six independent post')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14868-protocol-carrier-boundary-six-pt-v1/manifest.json','7dce0ee6ffd042a498ae7bfcbf20d9f2d5a0ce0f82d3e9e8ed716e6211a0bd55')
    old=data.read_checked(data.BASE/'PG14862-protocol-carrier-seven-existing-post-v1/manifest.json','33a0eaa5881826498d6b9b22d4b6436e50445dedbc713ffc5c056092611b1738')
    registry=data.read_checked(data.BASE/'PG14852-current908-named69-registry-v1/manifest.json','46d6f90a7c719ef536105cd9233c5653c834291255e04f10dbdf58334d41345a')
    require(all(v['actualExit']==0 and v['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' for v in [p,raw,old,registry]),'same genuine production Source')
    require(p['execSha256']==raw['execSha256']!=old['execSha256'] and p['sessionIdentity']=='PG14868-PROTOCOL-CARRIER-BOUNDARY6','new single exec only, never unioned')
    cases=[]
    for name,digest in p['xmlHashes'].items():
        content=(POST/name).read_bytes();require(data.sha(content)==digest==raw['xmlHashes'][name],'own original6 XML bytes')
        tree=ET.fromstring(content);require(int(tree.get('tests'))==6 and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'whole six FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'no non-PASS case');cases.append((case.get('classname'),case.get('name')))
    expected_names={'textRedactionAndPrimitiveBoundaries','emptyAndAbsentHaveExplicitUnsetContract','immutableOrderedDefensiveCopy','invalidMapsAndNullEntriesAreRejected','equalityAndHashFollowIndependentMapContract','independentReadersObserveSameImmutableSnapshot'}
    require(len(cases)==len(set(cases))==6 and {n for c,n in cases}==expected_names and {c for c,n in cases}=={'dev.codex.schubert.nk.protocol.layout.ProtocolCarrierBoundaryTest'} and not set(cases)&{(c['classname'],c['name']) for c in registry['cases']},'six unique new actual methods, no original31 replay')
    require(p['completeSourceUnitClosure']==old['completeSourceUnitClosure'] and p['physicalClasses']==old['physicalClasses'] and len(p['physicalClasses'])==11 and p['metadataKinds']==old['metadataKinds'] and len(p['metadataClasses'])==6,'all seven Source/eleven identical Main class bytes; only six interfaces N/A')
    snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    for name,digest in p['physicalClasses'].items():
        value=(snapshot/'src/schubert-nk-protocol/target/classes'/(name+'.class')).read_bytes();parsed=code.decode(value,name+'.class')
        require(data.sha(value)==digest and parsed['methods']==p['sourcePhysicalInventory'][name]['methods'] and parsed['sourceFile']==name.split('$',1)[0].rsplit('/',1)[1]+'.java','independent actual whole Code inventory')
        require((not any(m['hasCode'] for m in parsed['methods']))==(name in p['metadataClasses']),'actual NoCode only, no generated record omission')
    sums={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    for name,u in p['fullSourceUnits'].items():
        expected={k:{role:sum(p['counterInventory'][n]['counters'][k][role] for n in u['physical']) for role in ['missed','covered']} for k in sums}
        require(expected==u['totals'],'entire Source closure actual counter sum')
        for k in sums:
            for role in sums[k]:sums[k][role]+=expected[k][role]
    require(sums==p['totals']==dict(LINE=dict(missed=0,covered=28),METHOD=dict(missed=0,covered=13),CLASS=dict(missed=0,covered=5),BRANCH=dict(missed=0,covered=10)),'actual six counters, no old union')
    require(p['fullSourceUnits'][PREFIX+'FieldValueSet']['four100'] is True and p['fullSourceUnits'][PREFIX+'FieldValue']['threeCounter100'] is p['fullSourceUnits'][PREFIX+'FieldValue']['branchNaturallyZero'] is True and p['fullSourceUnits'][PREFIX+'FieldValue']['four100'] is False and sum(v['metadataOnly'] for v in p['fullSourceUnits'].values())==5,'one four100, one naturalB0 LMC100, five N/A; no false four')
    require(p['missedLines']==[] and p['ownerNamespaceNegativeVectors']==2,'zero actual missing and unknown/alias ownership guards')
    tool_path='tools/quality/architecture/ProtocolCarrierBoundaryTest.java'
    require(p['owners'][tool_path]['canonicalOwner'] is None and p['owners'][tool_path]['ownershipStatus']=='UNKNOWN' and p['owners'][tool_path]['sha256']==data.sha((data.ROOT/tool_path).read_bytes())=='bd1da8b0168836610a5d7a28ec4b3af127dfca86d15c0a7bbabb98282f841003','new PT source pinned, unknown owner not inferred')
    require(owner_role(tool_path,{})['canonicalOwner'] is None and owner_role('src/example.java',{'src/example.java':dict(path='src/example.java',owner='WBS-P001-02',costOwner='WBS-P001-02')})['canonicalOwner']=='WBS-P001-02','exact tool UNKNOWN/source baseline positive')
    owner_neg=[]
    for path in ['tools/quality/architecture/OtherTest.java','tools/quality/architecture/../ProtocolCarrierBoundaryTest.java']:
        try:owner_role(path,{})
        except ValueError:owner_neg.append(path)
        else:raise ValueError('owner alias or arbitrary tool accepted')
    require(not (data.BASE/'PG14870-protocol-carrier-boundary-six-post-v1').exists() and not (data.ROOT.parent/'pgpt-runs/PG379/pg14870-protocol-carrier-boundary-six-post-v1').exists(),'failed original post never reached own run/output')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','fullSourceUnits','physicalClasses','metadataClasses','totals','owners','missedLines']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'actual Source/whole case/counter values immutable')
        require(v['tests']==v['newUniqueMethods']==v['newTestIds']==6 and v['suites']==v['newProductExecutions']==1 and v['originalTestsCountedElsewhere'] is v['currentSourceExistingExecReanalyzed'] is False,'six new methods/one own JVM distinct roles')
        require(v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['targetSourceUnits']==7 and v['singleSession'] is True and v['crcMismatch']==0 and v['manualCounterExclusions']==[],'no NoCode/B0 fake strict four100')
        require(v['newAccepted']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is False and v['effortPercent'] is None,'no formal/effort/oldsource promotion')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('tests',31),('newUniqueMethods',31),('newProductExecutions',2),('newTestIds',0),('originalTestsCountedElsewhere',True),('currentSourceExistingExecReanalyzed',True),('fullSourceUnits',{}),('physicalClasses',{}),('metadataClasses',[]),('totals',{}),('owners',{}),('targetUnitFour100',True),('strictFour100GateExit',0),('targetSourceUnits',2),('singleSession',False),('crcMismatch',1),('manualCounterExclusions',['Text']),('newAccepted',1),('formalUpdated',True),('oldCoverageTransferred',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false qualification accepted '+key)
    for v in [p,old,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,originalManifestSha256='7dce0ee6ffd042a498ae7bfcbf20d9f2d5a0ce0f82d3e9e8ed716e6211a0bd55',newUniqueMethods=6,productTestsExecutedByPost=0,originalOwnProductExecutions=1,sourcePrograms=7,physicalClasses=11,four100SourcePrograms=1,naturalZeroBranchSourcePrograms=1,noCodeSourcePrograms=5,incompleteSourcePrograms=0,totals=sums,semanticNegativeVectors=len(negative),negativeLabels=negative,ownerNamespacePositiveVectors=2,ownerNamespaceNegativeVectors=len(owner_neg),coverageExecUnion=False,bug='BUG-2114',horizontal='YKT-1861',newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
