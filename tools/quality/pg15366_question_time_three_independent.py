"""Independent original UTC time-boundary3 and unbounded integer floor oracle; complete Source gap."""
import copy
import datetime
import json
import re
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

POST=('PG15364-question-time-three-post-v2','fd66524cfa291b77589113f626484ea540a6fac425a295b222b986681c1f4e0c')
RAW=('PG15362-question-time-three-pt-v1','509aab8f920fe36b73391b707ad285bc4dbc346842e97965e96e74be53808f22')
REG=('PG15352-current1777-inputs-outbox-registry-v1','e160176d7283e59615bfa7690c3d8856a7dd79babd89012a9e974df2face2c67')
OUT=data.BASE/'PG15366-question-time-three-independent-v1'
NAME='dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata'
TEST='dev/codex/schubert/nk/api/application/question/QuestionCommandTimeBoundaryTest'
TOTALS={'LINE':dict(missed=1,covered=8),'METHOD':dict(missed=1,covered=1),'CLASS':dict(missed=0,covered=1),'BRANCH':dict(missed=0,covered=4)}
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15362-ORIGINAL-QUESTION-TIME3','genuine source/current original session')
    expected={'lowerBoundPreservesFloorWithoutRounding','upperBoundAcceptsSubmicrosecondTailOnly','preEpochTruncationUsesUtcFloor'};actual=[]
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'same original XML')
        root=ET.fromstring(b);require(root.get('name')==TEST.replace('/','.') and int(root.get('tests'))==3 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole3 FES0')
        for c in root.findall('testcase'):
            require(not list(c),'actual pass');actual.append((c.get('classname'),c.get('name')))
    require(len(actual)==len(set(actual))==3 and {n for c,n in actual}==expected and not set(actual)&{(c['classname'],c['name']) for c in reg['cases']},'all new current original3')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    tpath='src/schubert-nk-api/src/test/java/'+TEST+'.java';test=(data.ROOT/tpath).read_text()
    require(data.sha((data.ROOT/tpath).read_bytes())==hashes[tpath]=='0d2b3fd7a094c51c4009b96c5dfa65081d0924810ce6aecd0dc2c6198c4e4ef0' and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',test))==expected,'exact whole Test/declared IDs')
    tokens=['new UUID(1711, 1)','new UUID(1711, 2)','0001-01-01T00:00:00Z','9999-12-31T23:59:59.999999Z','LOWER.plusNanos(999)','LOWER.minusNanos(1)','UPPER.plusNanos(999)','UPPER.plusNanos(1000)','1969-12-31T23:59:59.999999999Z','1969-12-31T23:59:59.999999Z','1970-01-01T00:00:00.000000001Z','assertEquals(Instant.EPOCH, after.at())']
    require(all(t in test for t in tokens) and '.toString()' not in test and 'QuestionCommandServiceTest' not in test and not any(t in test for t in ['@BeforeAll','ApiLogDatabaseFixture','TemporaryInfrastructureException','getConnection(']),'independent literal boundaries; no extraction/DB/graph')
    epoch=datetime.date(1970,1,1);lower=(datetime.date(1,1,1)-epoch).days*86400*10**9;upper=((datetime.date(9999,12,31)-epoch).days*86400+86399)*10**9+999999000
    inputs=[lower,lower+999,lower-1,upper,upper+999,upper+1000,-1,1]
    outputs=[lower,lower,lower-1000,upper,upper,upper+1000,-1000,0]
    require([v//1000*1000 for v in inputs]==outputs and [lower<=v<=upper for v in outputs]==[True,True,False,True,True,False,True,True],'independent proleptic Gregorian epoch nanoseconds/floor, never Production expected')
    require(p['completeSourceUnitClosure']=={NAME:[NAME]} and set(p['physicalClasses'])==set(p['executable'])=={NAME} and NAME not in reg['fullSourceUnits'],'one new complete Source Code')
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        require({n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}=={NAME},'actual full class closure')
        b=jar.read(NAME+'.class');require(data.sha(b)==p['physicalClasses'][NAME] and code.decode(b,NAME+'.class')['methods']==p['sourcePhysicalInventory'][NAME]['methods'],'actual class Code/official filtered record not excluded manually')
    require(p['executable'][NAME]['counters']==p['totals']==p['fullSourceUnits'][NAME]['totals']==TOTALS and p['missedLines']==[[NAME,'21','0','0']],'actual entire Source counters/uncalled toString line retained')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual Main baseline/TestUNKNOWN')
    require(len(p['owners'])==2 and p['owners']['src/schubert-nk-api/src/main/java/'+NAME+'.java']['canonicalOwner']=='WBS-P011-03' and p['owners'][tpath]['ownershipStatus']=='UNKNOWN','explicit pair not change group')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','missedLines','profile']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'all independent actual source/run semantics')
        require(v['tests']==3 and v['suites']==1 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'incomplete Source gate never false pass')
        require(v['newAccepted']==v['productTestsReexecutedByPost']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['actualFilesOpenedByProduct'] is v['rootMainInvoked'] is False and v['effortPercent'] is None,'no external/old/accepted/formal credit')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',4),('suites',2),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('missedLines',[]),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',[NAME]),('manualCounterExclusions',['toString']),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false time boundary proof accepted')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=3,suites=1,newUniqueMethods=3,sourcePrograms=1,physicalClasses=1,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=1,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,independentNanosecondInputs=inputs,independentNanosecondFloor=outputs,baselineMainOwnerRows=1,unknownTestOwnerRows=1,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
