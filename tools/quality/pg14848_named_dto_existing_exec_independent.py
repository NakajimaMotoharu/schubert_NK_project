"""Independent69-DTO scope/oracle/counter check, existing original31 only, no Product execution."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

PIN='cdb2e9a507db0c0199ae199bab7c4ffa3aaa3045a699901ba00e25b493846cd8'
POST=data.BASE/'PG14846-named-dto-existing-exec-post-v1'
OUT=data.BASE/'PG14848-named-dto-existing-exec-independent-v1'
FIXTURES={
 'fields-ui234-236.tsv':'b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b',
 'named-types-ss323.tsv':'9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76',
 'named-accessors-independent.tsv':'27b9a458374f5b9edda50d78fae42ee76dabf15d8d1ecd9c94e56dbab63162d5'}

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(v):return json.dumps(v,sort_keys=True)

def fixture(name):
    path=data.ROOT/'src/schubert-nk-protocol/src/test/resources/protocol'/name
    require(data.sha(path.read_bytes())==FIXTURES[name],'independent fixed SS fixture pin')
    return [line.split('\t') for line in path.read_text().splitlines() if line and not line.startswith('#')]

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only69 independent qualification')
    p=data.read_checked(POST/'manifest.json',PIN)
    old=data.read_checked(data.BASE/'PG14362-protocol-semantic-whole-thirty-one-post-v1/manifest.json','f03bb6730c2491b463c9400972de775f65a389c54a4e65d24c8a6aa1d3fef177')
    raw=data.read_checked(data.BASE/'PG14360-protocol-semantic-whole-thirty-one-pt-v1/manifest.json','4123691e8775684b13142b4b9c319bca82956c008163c63793dedb5b4de7ebd2')
    registry=data.read_checked(data.BASE/'PG14836-current908-resource-registry-v1/manifest.json','af91672ea724386906cce9ad70ae6e85e33f68455fcc14db020715da5b0033dd')
    require(all(v['actualExit']==0 and v['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' for v in [p,old,raw,registry]),'genuine same-source qualified original receipts')
    require(p['execSha256']==old['execSha256']==raw['execSha256']=='318cbad012d5eeb33361270c23e4a95851bd82e4ec2693cf72b4094c990acfd7' and p['sessionIdentity']==old['sessionIdentity']=='PG14360-ORIGINAL-PROTOCOL-SEMANTIC31','same single actual exec, not another success')
    actual=[]
    for name,digest in p['xmlHashes'].items():
        value=(POST/name).read_bytes();require(data.sha(value)==digest==old['xmlHashes'][name]==raw['xmlHashes'][name],'original31 XML hash')
        tree=ET.fromstring(value);require(int(tree.get('tests'))==len(tree.findall('testcase')) and all(int(tree.get(k))==0 for k in ['failures','errors','skipped']),'all original XML FES0')
        for case in tree.findall('testcase'):
            require(not list(case),'no non-PASS case');actual.append((case.get('classname'),case.get('name')))
    current={(v['classname'],v['name']) for v in registry['cases']}
    require(len(actual)==len(set(actual))==31 and len({c for c,n in actual})==7 and set(actual)<=current and set(actual)=={(v['classname'],v['name']) for v in p['cases']},'already counted31, never new credit')
    areas={}
    for row in fixture('fields-ui234-236.tsv'):
        require(len(row)==8,'independent field columns')
        if row[6]!='F':areas.setdefault((row[0],row[1]),[]).append((row[2],row[4],row[5],row[6]))
    mappings=fixture('named-types-ss323.tsv');require(len(mappings)==64 and all(len(row)==3 for row in mappings),'explicit64 mapping rows')
    shapes={}
    for layout,data_type,record_type in mappings:
        for name,area in [(data_type,'DATA'),(record_type,'RECORD')]:
            if name=='-':continue
            shape=areas.get((layout,area),[])
            require(name not in shapes or shapes[name]==shape,'shared named types have exactly the same independent field shape');shapes[name]=shape
    accessors=fixture('named-accessors-independent.tsv')
    require(len(accessors)==len({row[0] for row in accessors}) and all(len(row)==2 for row in accessors),'independent public accessor mapping unique')
    require(len(shapes)==69 and sum(len(v) for v in shapes.values())==295 and sum(w=='X' and presence in ['C','O'] for shape in shapes.values() for name,length,w,presence in shape)==79 and sum(not v for v in shapes.values())==4,'69 types/295 fields/79optionals/4empty independently counted')
    require({field[0] for shape in shapes.values() for field in shape}=={row[0] for row in accessors},'no missing or extra independent accessor binding')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    hashes=normal['begin']['inputHashes'];names={};expected_totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    for simple in shapes:
        paths=[path for path in hashes if path.startswith('src/schubert-nk-protocol/src/main/java/') and path.endswith('/'+simple+'.java')]
        require(len(paths)==1,'one exact module Source per independent name');path=paths[0];name=path.split('/src/main/java/',1)[1][:-5];names[name]=path
        require(data.sha((data.ROOT/path).read_bytes())==hashes[path] and name not in registry['fullSourceUnits'],'new scope only, not changed/replaced Source')
        require(p['completeSourceUnitClosure'][name]==p['fullSourceUnits'][name]['physical']==[name],'entire one-class Source closure')
        info=p['sourcePhysicalInventory'][name]
        require(info['sourceFile']==simple+'.java' and info['sha256']==p['physicalClasses'][name] and any(m['hasCode'] for m in info['methods']) and {'from','fields','toString'}<={m['name'] for m in info['methods']},'actual executable DTO Source, not filtered noCode metadata')
        row=p['executable'][name]['counters'];require(row==p['fullSourceUnits'][name]['totals'],'exact actual one-class Source totals')
        require(row['BRANCH']==dict(missed=0,covered=0) and all(row[k]['missed']==0 and row[k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and p['fullSourceUnits'][name]['four100'] is False and p['fullSourceUnits'][name]['branchNaturallyZero'] is p['fullSourceUnits'][name]['threeCounter100'] is True,'natural branch0 plus actual nonempty LMC100, notfour100')
        owned=p['owners'][path];require(owned['sha256']==hashes[path] and owned['canonicalOwner']==owned['canonicalCostOwner']=='WBS-P001-03' and owned['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','canonical source owner unchanged')
        for k,v in row.items():
            for role,value in v.items():expected_totals[k][role]+=value
    require(set(names)==set(p['fullSourceUnits'])==set(p['physicalClasses'])==set(p['executable'])==set(p['sourcePhysicalInventory']) and len(names)==69 and p['metadataClasses']==[],'all and only69 full Source closures, no hidden exclusion')
    require(expected_totals==p['totals']==dict(LINE=dict(missed=0,covered=1259),METHOD=dict(missed=0,covered=276),CLASS=dict(missed=0,covered=69),BRANCH=dict(missed=0,covered=0)),'actual nonempty69 DTO totals')
    oracle=data.ROOT/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/IndependentNamedFieldOracle.java'
    require(data.sha(oracle.read_bytes())==raw['begin']['testSourceHashes'][str(oracle)]=='7fefc742055add410ebcb49991a8f30fb5a71e29d3d9c2908a053b8f17109a7d','original independent oracle frozen')
    fixed={k:p[k] for k in ['source','cases','xmlHashes','execSha256','sessionIdentity','completeSourceUnitClosure','sourcePhysicalInventory','physicalClasses','executable','fullSourceUnits','totals','owners','reportedEnvironment','originalPostReference','namedTypeFixtureSha256']}
    def contract(v):
        require(all(wire(v[k])==wire(value) for k,value in fixed.items()),'all actual scope/counter/oracle/proof roles immutable')
        require(v['tests']==31 and v['suites']==7 and v['targetSourceUnits']==69 and v['currentSourceExistingExecReanalyzed'] is v['originalTestsCountedElsewhere'] is True and v['newProductExecutions']==v['newUniqueMethods']==0,'reanalysis roles, not new tests/execs')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[] and v['officialGeneratedFiltersUnchanged'] is True,'one exec/CRC/full unexcluded Source')
        require(v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['oldCoverageTransferred'] is v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is False and v['newAccepted']==0 and v['effortPercent'] is None,'no naturalB0/old/formal/effort promotion')
    contract(p);labels=[]
    for label,key,value in [('source','source','OLD'),('all31-as-new','newUniqueMethods',31),('newJVM','newProductExecutions',1),('counted-role','originalTestsCountedElsewhere',False),('Source-subset','targetSourceUnits',68),('noCode-fake','metadataClasses',list(names)),('four-fake','targetUnitFour100',True),('strict-fake','strictFour100GateExit',0),('scope','completeSourceUnitClosure',{}),('counter','totals',{}),('UNKNOWN-owner','owners',{}),('oracle-pin','namedTypeFixtureSha256','0'*64),('CRC','crcMismatch',1),('session','singleSession',False),('oldsource','oldCoverageTransferred',True),('filter','officialGeneratedFiltersUnchanged',False),('exclude','manualCounterExclusions',['other']),('formal','formalUpdated',True),('acceptance','newAccepted',1),('effort','effortPercent',75)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false saved69 qualification accepted '+label)
    held={'tools/quality/architecture/SnapshotKeyCloseWitness.java','tools/quality/pg9892_snapshot_key_close_witness.py'}
    for v in [p,old,registry]:
        require(not held&v['invocation']['loadedProjectPythonSources'].keys(),'held paths not included in provenance verification');verify(v['invocation'])
    require('invocation' not in raw and not held&raw['begin']['invocation']['loadedProjectPythonSources'].keys(),'raw begin invocation/held exclusion');verify(raw['begin']['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,existingOriginalPostSha256='f03bb6730c2491b463c9400972de775f65a389c54a4e65d24c8a6aa1d3fef177',originalXmlMethodsAlreadyCounted=31,originalXmlSuites=7,newUniqueMethods=0,productTestsExecuted=0,newSourcePrograms=69,fullPhysicalClasses=69,independentOracle=dict(namedTypes=69,layouts=64,components=295,optionals=79,emptyTypes=4,fixtures=FIXTURES),allNonemptyLmc100NaturalBranchZero=True,four100SourcePrograms=0,naturalZeroBranchSourcePrograms=69,totals=expected_totals,semanticNegativeVectors=len(labels),negativeLabels=labels,coverageExecUnion=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
