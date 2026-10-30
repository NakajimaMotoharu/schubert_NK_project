"""Independent complete three value Source scopes; no parent Repository promotion from private record."""
import copy
import json
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

PIN='9ab072ca545059a55fa76d41be6c9268e8a44fabdfa26afbc7427e2859053813'
POST=data.BASE/'PG14912-batch-step-values-eight-post-v1'
OUT=data.BASE/'PG14914-batch-step-values-independent-v1'
PREFIX='dev/codex/schubert/nk/batch/repository/'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only step-values independent')
    p=data.read_checked(POST/'manifest.json',PIN)
    raw=data.read_checked(data.BASE/'PG14911-batch-step-values-eight-pt-v2/manifest.json','9736adfd97804fa8daddb7ba8286b9450b25895f0bc2fd24240d8b04b428d39a')
    registry=data.read_checked(data.BASE/'PG14900-current926-backup-registry-v1/manifest.json','9d7110162ba74a4d78e2d222fd0b1dc10aaf3bc7053246bbefb76d473329c6d3')
    require(p['actualExit']==raw['actualExit']==registry['actualExit']==0 and p['source']==raw['source']==registry['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG14911-ORIGINAL-BATCH-STEP-VALUES8','same actual new source/run')
    cases=[]
    for filename,h in p['xmlHashes'].items():
        value=(POST/filename).read_bytes();require(data.sha(value)==h==raw['xmlHashes'][filename],'original XML8 identity');root=ET.fromstring(value)
        require(int(root.get('tests'))==8 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole8 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual PASS');cases.append((c.get('classname'),c.get('name')))
    require(len(cases)==len(set(cases))==8 and not set(cases)&{(c['classname'],c['name']) for c in registry['cases']} and {n for c,n in cases}=={'closedStepsAndBackupPolicy','attemptIdentityAndBounds','terminalStatesAndReasonMatrix','counterAndStatusBoundaries','temporalContractAndBusinessDay','nullContractsAndRedaction','immutableValueSemantics','independentConcurrentValues'},'all original8/nonoverlap, no extracted/replayed subset')
    test_path='src/schubert-nk-batch/src/test/java/'+PREFIX+'BatchStepValuesTest.java';require(data.sha((data.ROOT/test_path).read_bytes())=='4f6c9eca1af5970e44717d214fa1ef83459c853268548f33633cf65ba0d32a81','whole fixed independent literal Test')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    expected={PREFIX+'BatchStep':[PREFIX+'BatchStep'],PREFIX+'BatchStepAttempt':[PREFIX+'BatchStepAttempt'],PREFIX+'BatchStepResult':[PREFIX+'BatchStepResult',PREFIX+'BatchStepResult$Reason',PREFIX+'BatchStepResult$Status']}
    require(p['completeSourceUnitClosure']==expected and len(p['physicalClasses'])==5 and p['metadataClasses']==[] and not expected.keys()&registry['fullSourceUnits'].keys(),'only complete3new Source/5Code, never parent Repository')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};totals={k:dict(missed=0,covered=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        for name,closure in expected.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'all actual nested Source classfiles')
            path='src/schubert-nk-batch/src/main/java/'+name+'.java';require(data.sha((data.ROOT/path).read_bytes())==normal['begin']['inputHashes'][path]==p['owners'][path]['sha256'],'fixed actual whole Source pin')
            actual=canonical(path,logical);require(all(p['owners'][path][k]==v for k,v in actual.items()) and actual['canonicalOwner']==('WBS-P017-12' if name.endswith('BatchStepAttempt') else 'WBS-P017-02'),'actual baseline parent owner distinct from cost leaf')
            local={k:{role:sum(p['executable'][n]['counters'][k][role] for n in closure) for role in ['missed','covered']} for k in totals};require(local==p['fullSourceUnits'][name]['totals'],'full Source actual counter sums')
            for k in totals:
                for role in totals[k]:totals[k][role]+=local[k][role]
            for physical_name in closure:
                content=jar.read(physical_name+'.class');parsed=code.decode(content,physical_name+'.class');require(data.sha(content)==p['physicalClasses'][physical_name] and parsed['methods']==p['sourcePhysicalInventory'][physical_name]['methods'] and any(m['hasCode'] for m in parsed['methods']),'all five executable Code inventories, no exclusions')
    require(totals==p['totals']==dict(LINE=dict(missed=0,covered=74),METHOD=dict(missed=0,covered=14),CLASS=dict(missed=0,covered=5),BRANCH=dict(missed=0,covered=68)),'actual nonempty totals from own exec, not union')
    require(sum(u['four100'] for u in p['fullSourceUnits'].values())==2 and p['fullSourceUnits'][PREFIX+'BatchStep']['branchNaturallyZero'] is p['fullSourceUnits'][PREFIX+'BatchStep']['threeCounter100'] is True and p['fullSourceUnits'][PREFIX+'BatchStep']['four100'] is False and p['targetUnitFour100'] is False and p['strictFour100GateExit']==1 and p['missedLines']==[],'two four100/one B0 N/A, no fake strict pass')
    history_name=PREFIX+'BatchRunRepository$History.class';history=snapshot/'src/schubert-nk-batch/target/classes'/history_name;parsed=code.decode(history.read_bytes(),history_name)
    require('<clinit>' not in {m['name'] for m in parsed['methods']} and parsed['sourceFile']=='BatchRunRepository.java' and PREFIX+'BatchRunRepository' not in p['fullSourceUnits'] and PREFIX+'BatchRunRepository$History' not in p['physicalClasses'],'private diagnostic only, no parent/partial qualification')
    binary_negative=[]
    for wrong in ['BatchRunRepository$History.class',PREFIX+'Other.class']:
        try:code.decode(history.read_bytes(),wrong)
        except ValueError:binary_negative.append(wrong)
        else:raise ValueError('wrong classfile binary identity accepted')
    require(not (data.BASE/'PG14910-batch-step-values-eight-pt-v1').exists() and not (data.ROOT.parent/'pgpt-runs/PG379/pg14910-batch-step-values-eight-pt-v1').exists(),'original preflight failure did not create Product run')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','profile','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners']}
    def contract(v):
        require(all(v[k]==value for k,value in fixed.items()),'actual original proof/owner immutable')
        require(v['tests']==8 and v['suites']==1 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'one complete run, honest N/A')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['currentSourceExistingExecReanalyzed'] is v['originalTestsCountedElsewhere'] is False and v['effortPercent'] is None,'no old/formal/effort transfer')
    contract(p);negative=[]
    for key,value in [('source','OLD'),('tests',7),('suites',2),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',list(p['physicalClasses'])),('manualCounterExclusions',['BatchStep']),('totals',{}),('fullSourceUnits',{}),('profile',{}),('owners',{}),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('oldCoverageTransferred',True),('currentSourceExistingExecReanalyzed',True),('originalTestsCountedElsewhere',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false step proof accepted '+key)
    for v in [p,registry]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=PIN,tests=8,suites=1,newUniqueMethods=8,sourcePrograms=3,physicalClasses=5,four100SourcePrograms=2,naturalZeroBranchSourcePrograms=1,totals=totals,semanticNegativeVectors=len(negative),negativeLabels=negative,binaryNamePositiveVectors=1,binaryNameNegativeVectors=len(binary_negative),partialHistoryNotPromotedToRepository=True,actualRepositoryOrDatabaseConstructed=False,originalMethodsReexecuted=0,bug='BUG-2117',horizontal='YKT-1864',newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
