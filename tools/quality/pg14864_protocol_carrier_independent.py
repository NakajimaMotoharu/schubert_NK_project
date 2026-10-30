"""Independent saved-exec carrier scope and literal-generation horizontal verification; Product0."""
import ast
import copy
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

PIN='33a0eaa5881826498d6b9b22d4b6436e50445dedbc713ffc5c056092611b1738'
POST=data.BASE/'PG14862-protocol-carrier-seven-existing-post-v1'
OUT=data.BASE/'PG14864-protocol-carrier-independent-v1'
PREFIX='dev/codex/schubert/nk/protocol/layout/'
REL=['FieldValue','FieldValueSet','LayoutPayload','PayloadData','PayloadRecord','semantic/ProtocolId','semantic/WireEnum']
WITNESSES=[
 ('reviewed_resource_dom_post_v1.py',14808,'2cda1ad26c53b5c20a9772c1dfd9a8a7b2b241ee65dc682a6da6c7573c90eeb5'),
 ('reviewed_resource_dom_post_v2.py',14820,'aca238ae4558482138cbf3ea284a16952d33e3ca5361d93af37fa9f5fc26b516'),
 ('pg14818_resource_dom_post_v2_qualification.py',14818,'8b030bbf959802a473d167b8782da191c66648c21feea77a3d23e64766a34966'),
 ('pg14822_resource_dom_post_v2_independent.py',14822,'3a4495e18b0f585da83bfcd584ed58739148cd92382f125341a53416f9b765fe'),
 ('pg14840_current908_wbs.py',14840,'4529f950fd21ce89370193bc67bade47bf96a3feda93f4028e335ca5a9df692a'),
 ('pg14842_current908_wbs_post.py',14842,'8cabd47ac6f9202f55ad134fd854e1c466bc76ed2f3dfc7caafad0da046cca92'),
 ('pg14846_named_dto_existing_exec_post.py',14846,'cdb2e9a507db0c0199ae199bab7c4ffa3aaa3045a699901ba00e25b493846cd8'),
 ('pg14856_current908_named69_wbs.py',14856,'5453dcd0f178b7a73395e05a9012d5c34b6c9d35617efdc3ee0fc2b3eb0e8107'),
 ('pg14858_current908_named69_wbs_post.py',14858,'f3870e3bae05f7f03a6133cc2351d45a7470f8ad1a217dd3746a5e153dc34524')]

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent carrier post')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14360-protocol-semantic-whole-thirty-one-pt-v1/manifest.json','4123691e8775684b13142b4b9c319bca82956c008163c63793dedb5b4de7ebd2')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(p['actualExit']==0 and p['source']==raw['source']==normal['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c','actual same-source evidence')
    require(p['execSha256']==raw['execSha256']=='318cbad012d5eeb33361270c23e4a95851bd82e4ec2693cf72b4094c990acfd7' and p['sessionIdentity']=='PG14360-ORIGINAL-PROTOCOL-SEMANTIC31','original single exec/session')
    cases=[]
    for name,digest in p['xmlHashes'].items():
        value=(POST/name).read_bytes();require(data.sha(value)==digest==raw['xmlHashes'][name],'original XML hash')
        root=ET.fromstring(value);require(all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'XML FES0')
        for c in root.findall('testcase'):
            require(not list(c),'all genuine PASS');cases.append((c.get('classname'),c.get('name')))
    require(len(cases)==len(set(cases))==31 and len({c for c,n in cases})==7 and set(cases)=={(c['classname'],c['name']) for c in p['cases']},'31 existing cases/7 suites')
    closures={PREFIX+r:sorted([PREFIX+r]+([PREFIX+r+'$'+n for n in ['Text','Numeric','Flag','Unset']] if r=='FieldValue' else [])) for r in REL}
    names=set().union(*(set(v) for v in closures.values()))
    meta={PREFIX+r for r in REL if r!='FieldValueSet'}
    require(p['completeSourceUnitClosure']==closures and len(names)==11 and set(p['physicalClasses'])==names and set(p['metadataClasses'])==meta,'7 complete Source/11 physical/6 true interface')
    snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    for name in names:
        path=snapshot/'src/schubert-nk-protocol/target/classes'/(name+'.class');value=path.read_bytes();parsed=code.decode(value,name+'.class')
        require(data.sha(value)==p['physicalClasses'][name]==p['sourcePhysicalInventory'][name]['sha256'],'whole physical class pin')
        require(parsed['methods']==p['sourcePhysicalInventory'][name]['methods'] and parsed['sourceFile']==name.split('$',1)[0].rsplit('/',1)[1]+'.java','independent Code/SourceFile inventory')
        require((not any(m['hasCode'] for m in parsed['methods']))==(name in meta),'NO_CODE only actual no Code')
        if name in meta:require(p['metadataKinds'][name]=='NO_CODE' and all(v==dict(missed=0,covered=0) for v in p['counterInventory'][name]['counters'].values()),'interface N/A not generated-record exclusion')
        else:require(p['executable'][name]['counters']==p['counterInventory'][name]['counters'] and p['executable'][name]['crc64']==p['counterInventory'][name]['crc64'],'independent inventory/diagnostic counter and CRC agreement')
    expected={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    for name,closure in closures.items():
        path='src/schubert-nk-protocol/src/main/java/'+name+'.java';require(data.sha((data.ROOT/path).read_bytes())==normal['begin']['inputHashes'][path],'frozen actual Source')
        counters={k:{role:sum(p['counterInventory'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in expected}
        require(counters==p['fullSourceUnits'][name]['totals'],'full Source counter sum')
        for k in expected:
            for role in expected[k]:expected[k][role]+=counters[k][role]
    require(expected==p['totals']==dict(LINE=dict(missed=4,covered=24),METHOD=dict(missed=3,covered=10),CLASS=dict(missed=0,covered=5),BRANCH=dict(missed=4,covered=6)),'actual deficiencies preserved')
    require(sum(v['metadataOnly'] for v in p['fullSourceUnits'].values())==5 and sum(not v['metadataOnly'] for v in p['fullSourceUnits'].values())==2 and not any(v['four100'] or v['threeCounter100'] for v in p['fullSourceUnits'].values()),'five N/A and two incomplete, zero qualified executable Sources')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','completeSourceUnitClosure','physicalClasses','metadataClasses','metadataKinds','counterInventory','executable','fullSourceUnits','totals','owners','missedLines']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'actual proof and missed counters immutable')
        require(v['newProductExecutions']==v['newUniqueMethods']==v['newAccepted']==0 and v['originalTestsCountedElsewhere'] is v['currentSourceExistingExecReanalyzed'] is True,'no new Product/test credit')
        require(v['targetSourceUnits']==7 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['crcMismatch']==0 and v['singleSession'] is True,'same exec/CRC, not false four100')
        require(v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is False and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True and v['effortPercent'] is None,'formal/quality unchanged')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('newProductExecutions',1),('newUniqueMethods',31),('newAccepted',1),('originalTestsCountedElsewhere',False),('targetSourceUnits',6),('targetUnitFour100',True),('strictFour100GateExit',0),('crcMismatch',1),('singleSession',False),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('manualCounterExclusions',['FieldValue$Text']),('officialGeneratedFiltersUnchanged',False),('effortPercent',75),('metadataClasses',sorted(names)),('totals',{}),('fullSourceUnits',{}),('owners',{}),('missedLines',[])]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false carrier proof accepted '+key)
    witnesses=[]
    for filename,number,pin in WITNESSES:
        paths=list(data.BASE.glob('PG'+str(number)+'-*/manifest.json'));require(len(paths)==1,'one exact public witness')
        w=data.read_checked(paths[0],pin);require(w['actualExit']==0,'genuine saved success not begin')
        path=data.ROOT/'tools/quality'/filename;digest=data.sha(path.read_bytes());tree=ast.parse(path.read_text());functions=[v.name for v in tree.body if isinstance(v,(ast.FunctionDef,ast.AsyncFunctionDef))]
        require(len(functions)==len(set(functions)),'no duplicated generated top-level function')
        require(w['invocation']['loadedProjectPythonSources'].get(str(path.relative_to(data.ROOT)))==digest,'actual generated source matches original qualified witness')
        witnesses.append(dict(path=str(path.relative_to(data.ROOT)),sha256=digest,witness=str(paths[0].relative_to(data.ROOT)),witnessSha256=pin,topLevelFunctions=functions,disposition='NON_APPLICABLE_LITERAL_VALUES_NO_DOLLAR_REPLACEMENT_TOKEN_SAVED_AST_AND_ORIGINAL_WITNESS_MATCH'))
    tool=data.read_checked(data.BASE/'PG14863-literal-replacement-tool-v1/manifest.json',data.sha((data.BASE/'PG14863-literal-replacement-tool-v1/manifest.json').read_bytes()))
    for filename,key in [('literal_template_replace_v1.mjs','helperSha256'),('pg14863_literal_template_replace_test.mjs','testSha256'),('pg14862_prepare_carrier_post.mjs','generatorSha256'),('pg14862_protocol_carrier_seven_existing_post.py','generatedPythonSha256')]:require(data.sha((data.ROOT/'tools/quality'/filename).read_bytes())==tool[key],'fixed generated tool hash')
    require(tool['actualExit']==0 and tool['toolPositiveVectors']==tool['toolNegativeVectors']==11 and tool['nativeFailureOwnerOccurrences']==2 and tool['correctedOwnerOccurrences']==1 and tool['productTestsExecuted']==0,'fixed literal recurrence vectors not Product PT')
    for v in [p,raw['begin']]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,originalXmlMethodsAlreadyCounted=31,newUniqueMethods=0,productTestsExecuted=0,newSourcePrograms=7,fullPhysicalClasses=11,trueNoCodePhysical=6,noCodeSourcePrograms=5,incompleteSourcePrograms=2,four100SourcePrograms=0,totals=expected,semanticNegativeVectors=len(negative),negativeLabels=negative,horizontalWitnesses=witnesses,literalToolVectors=22,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False,actualExternalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
