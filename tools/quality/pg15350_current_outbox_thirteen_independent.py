"""Independent current eight pure Outbox Sources/original13 and integer/jitter golden vectors."""
import copy
import json
import re
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

POST=('PG15348-current-outbox-thirteen-post-v2','772cfdd88f5a604232c3aa7c184edc4bfcc9b7f42a3b408a2e130725c18d59d7')
RAW=('PG15346-current-outbox-thirteen-pt-v1','c219fed1f5ef50e0d03a8ea1f6f3496d890c65ffb2d5f27c921745d03738e29d')
REG=('PG15331-current1760-exact11-owner-registry-v3','cfb7c63e1b0761397371bf5fef625b7014aff588b992c35619c99b633374bd9f')
OUT=data.BASE/'PG15350-current-outbox-thirteen-independent-v1'
PREFIX='dev/codex/schubert/nk/api/messaging/outbound/'
NAMES=['OutboxDestination','OutboxRetrySchedule','OutboxEntry','OutboxRequest','OutboxDlqMetadata','OutboxDispatchReport','OutboxIntegrityException','OutboxSendException']
COUNTS={'OutboxPolicyTest':4,'OutboxModelTest':4,'OutboxDlqMetadataTest':2,'OutboxDispatchReportBoundaryTest':3}
NATURAL={PREFIX+n for n in ['OutboxIntegrityException','OutboxSendException']}
TOTALS={'LINE':dict(missed=0,covered=148),'METHOD':dict(missed=0,covered=50),'CLASS':dict(missed=0,covered=8),'BRANCH':dict(missed=0,covered=79)}
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def numbers(text,name):
    value=re.search(r'(?:long|int)\[\]\s+'+name+r'\s*=\s*\{([^}]+)\}',text)[1]
    return [int(v.strip().replace('_','').removesuffix('L')) for v in value.split(',') if v.strip()]
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,reg=read(POST),read(RAW),read(REG)
    require(p['actualExit']==raw['actualExit']==reg['actualExit']==0 and p['source']==raw['source']==reg['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['execSha256']==raw['execSha256'] and p['sessionIdentity']=='PG15346-CURRENT-OUTBOX-WHOLE13','genuine same source single original run')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes']
    texts={};declared=set();actual=[]
    for name,count in COUNTS.items():
        path='src/schubert-nk-api/src/test/java/'+PREFIX+name+'.java';b=(data.ROOT/path).read_bytes();require(data.sha(b)==hashes[path],'whole current original Test hash');text=b.decode();texts[name]=text
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(',text);require(len(methods)==count,'all original declarations');declared.update(((PREFIX+name).replace('/','.'),n) for n in methods)
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'actual XML same');root=ET.fromstring(b)
        require(int(root.get('tests'))==COUNTS[root.get('name').rsplit('.',1)[-1]] and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'whole13 FES0')
        for case in root.findall('testcase'):
            require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==13 and set(actual)==declared and not set(actual)&{(c['classname'],c['name']) for c in reg['cases']},'current unique13, not old source result transfer')
    policy=texts['OutboxPolicyTest'];attempts=[1,2,3,4,5,100];base=[1000,5000,30000,60000,300000,300000]
    require(numbers(policy,'attempts')==attempts and numbers(policy,'middleMillis')==base and numbers(policy,'lowerMillis')==[900,4500,27000,54000,270000,270000] and numbers(policy,'upperMillis')==[1100,5500,33000,66000,330000,330000],'independent explicit retry golden arrays')
    require(all(low==b*9//10 and high==b*11//10 for b,low,high in zip(base,numbers(policy,'lowerMillis'),numbers(policy,'upperMillis'))) and all(t in policy for t in ['"nk.async.work"','"nk.dead.letter"','failedAt, 1, -101','failedAt, 1, 101','2026-09-05T00:00:04.001Z']),'independent jitter/closed destination, not QA050 maintenance interval')
    report=texts['OutboxDispatchReportBoundaryTest'];maximum=2147483647
    sums=[4294967296,4294967296,4294967296,4294967297,4294967297,4294967297,6442450941]
    require(numbers(report,'mathematicalSums')==sums and sums==[maximum+maximum+2]*3+[maximum+maximum+3]*3+[3*maximum],'independent unbounded integer oracle rejects int wrapping')
    require(all(t in report for t in ['{0, 0, 0, 0}','{MAX, MAX - 2, 1, 1}','{MAX, 1, MAX - 2, 1}','{MAX, 1, 1, MAX - 2}','{0, MAX, MAX, 2}','{1, MAX, MAX, 3}','{0, Integer.MIN_VALUE, 0, 0}']),'explicit zero/MAX/negative/position vectors')
    model=texts['OutboxModelTest'];dlq=texts['OutboxDlqMetadataTest']
    require(all(t in model for t in ['new byte[] {1, 2, 3}','source[0] = 9','first[1] = 9','"body=<redacted>"','assertEquals(cause, wrapped.getCause())','assertEquals(cause, sendWrapped.getCause())','1_000_000_000_000L','"x".repeat(65)']) and 'getSuppressed(' not in model and 'TemporaryInfrastructureException' not in model,'defensive copy/null/bounded plain one-level JDK exception, no custom graph')
    require(all(t in dlq for t in ['"0001-01-01T00:00:00Z"','"1582-10-10T00:00:00Z"','"9999-12-31T23:59:59.999999Z"','"x".repeat(128)','"x".repeat(129)','new byte[320]','new byte[319]','Optional.empty()','"OutboxDlqMetadata[<redacted>]"']),'independent profile/ASCII/UTC/copy/redaction boundaries')
    closures={PREFIX+n:[PREFIX+n] for n in NAMES};require(p['completeSourceUnitClosure']==closures and not closures.keys()&reg['fullSourceUnits'].keys(),'all eight new whole Sources, no helper gaps hidden')
    computed={k:dict(missed=0,covered=0) for k in TOTALS}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name,closure in closures.items():
            require({n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(closure),'actual complete nested physical Jar closure')
            b=jar.read(name+'.class');require(data.sha(b)==p['physicalClasses'][name] and code.decode(b,name+'.class')['methods']==p['sourcePhysicalInventory'][name]['methods'] and any(m['hasCode'] for m in p['sourcePhysicalInventory'][name]['methods']),'actual retained executable Code')
            unit=p['fullSourceUnits'][name];c=p['executable'][name]['counters']
            require(c==unit['totals'] and unit['physical']==closure and unit['threeCounter100'] is True and unit['four100'] is (name not in NATURAL) and unit['branchNaturallyZero'] is (name in NATURAL) and all(v['missed']==0 for v in c.values()),'six nonempty four100/two natural B0-LMC100 separately')
            for k in computed:
                for role in computed[k]:computed[k][role]+=c[k][role]
    require(computed==p['totals']==TOTALS and p['missedLines']==[],'all current148L50M8C79B missed0')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(len(p['owners'])==12,'eight Main/four Test rows')
    for path,row in p['owners'].items():
        expected=canonical(path,logical);require(row['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in expected.items()),'exact source/canonical owner')
        require(expected['ownershipStatus']==('BASELINE_LOGICAL_REFERENCE' if '/src/main/' in path else 'UNKNOWN'),'no inferred Test owner')
    fixed={k:p[k] for k in ['source','cases','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','owners','profile']}
    def contract(v):
        require(all(wire(v[k])==wire(x) for k,x in fixed.items()),'every actual source/run/counter/owner contract')
        require(v['tests']==13 and v['suites']==4 and v['targetUnitFour100'] is False and v['strictFour100GateExit']==1 and v['singleSession'] is True and v['crcMismatch']==0 and v['metadataClasses']==[] and v['manualCounterExclusions']==[],'naturalB0 not false four100, no hidden counter exclusions')
        require(v['productTestsReexecutedByPost']==v['newAccepted']==0 and v['formalUpdated'] is v['whole451Accepted'] is v['wholeF03Accepted'] is v['oldCoverageTransferred'] is v['actualFilesOpenedByProduct'] is v['rootMainInvoked'] is False and v['effortPercent'] is None,'no false live/accepted/source union')
    contract(p);labels=[]
    for key,value in [('source','OLD'),('tests',14),('suites',3),('cases',[]),('totals',{}),('fullSourceUnits',{}),('physicalClasses',{}),('owners',{}),('targetUnitFour100',True),('strictFour100GateExit',0),('singleSession',False),('crcMismatch',1),('metadataClasses',list(NATURAL)),('manualCounterExclusions',['OutboxSendException']),('newAccepted',1),('productTestsReexecutedByPost',1),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('oldCoverageTransferred',True),('actualFilesOpenedByProduct',True),('rootMainInvoked',True),('effortPercent',50)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false Outbox contract accepted')
    for v in [p,reg]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=p['source'],invocation=invocation,postSha256=POST[1],tests=13,suites=4,newUniqueMethods=13,sourcePrograms=8,physicalClasses=8,four100SourcePrograms=6,naturallyBranchZeroSourcePrograms=2,incompleteSourcePrograms=0,totals=TOTALS,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOverflowSums=sums,independentAttempts=attempts,independentBaseMillis=base,baselineMainOwnerRows=8,unknownTestOwnerRows=4,candidateOwnersNotAccepted=True,originalMethodsReexecuted=0,actualLiveObservation=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
