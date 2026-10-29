"""Independent original-own JVM envelope verification; no Product/JVM/external operations."""
import copy
import json
import re
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG14282-current-four-pt-environment-post-v1'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PIN='feb59b693a1a74ba53c88323343888c9dd13a8cf3fc90fd7c9c1a5dfbfa56260'
PARENTS={
'PG14242-delivery-metadata-whole-two-pt-v1':'053ae4ab0d09af0eb25f711d58c00d5bb54cd88343be9d50e54fcf85b7377171',
'PG14252-inbound-primary-whole-five-pt-v1':'5b49c990cb01281ea26f7860256b7a09a0ea14becf1419cfce85e33cfc4ba888',
'PG14256-protocol-carrier-whole-eight-pt-v1':'90bb7c8ff1b76cb6ae5fc78bf4766bc6fb65702a53923c56e6ecd6b5ab83ef71',
'PG14270-web-three-forms-whole-twenty-four-pt-v1':'b86d3cc5ef5309104d8dfc85e215c193ac04ae7d054deca89da61e7c2520cadd'}
KEYS=('runtime.version','os.name','os.arch','os.version')

def require(value,message):
    if not value:raise ValueError(message)

def headers(lines):
    pairs=[line.rstrip('\n').split('=',1) for line in lines if any(line.startswith(k+'=') for k in KEYS)]
    require(len(pairs)==4 and {p[0] for p in pairs}==set(KEYS),'unique original four headers')
    result=dict(pairs)
    require(all(re.fullmatch(r'[A-Za-z0-9._+ -]{1,128}',v) for v in result.values()),'bounded public environment scalars')
    require(result['runtime.version'].startswith('25.0.4') and result['os.name']=='Linux','original JDK/Linux contract')
    return result

def assess(value,expected):
    require(value['actualExit']==0 and value['source']==SOURCE,'actual source/terminal')
    require(value['productTestsExecuted']==value['actualExternalOperations']==value['newAccepted']==0,'no inflated execution')
    require(value['executionEnvironmentFromOriginalJVM'] is True and value['currentEnvironmentSubstituted'] is False,'original not current environment')
    require(value['originalParentManifestsChanged'] is False and value['formalUpdated'] is False and value['whole451Accepted'] is False,'originals/formal unchanged')
    require(value['entries']==expected,'independent complete original bindings')
    return True

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only post')
    parent=data.BASE/'PG14280-current-four-pt-environment-v2/manifest.json'
    envelope=data.read_checked(parent,PIN);expected={}
    for run,pin in PARENTS.items():
        original=data.BASE/run/'manifest.json';raw=data.read_checked(original,pin)
        require(raw['source']==SOURCE and raw['actualExit']==0 and len(raw['stages'])==2 and all(s['actualExit']==0 and not s['timedOut'] for s in raw['stages']),'original completed PT')
        stage=raw['stages'][1]
        log=data.ROOT.parent/'pgpt-runs/PG379'/run.lower()/'selected-junit.log'
        require(log.resolve()==log and not log.is_symlink() and data.sha(log.read_bytes())==stage['logSha256'],'fixed own log/hash')
        prefix=[]
        with log.open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if not line:break
                prefix.append(line)
        require(sum(len(x.encode()) for x in prefix)<=4096,'bounded prefix read')
        reported=headers(prefix)
        entry=envelope['entries'][run]
        record=data.ROOT/entry['branchRecord']
        require(record.parent==data.ROOT/'evidence/01_PT/018_NK-OPS-001' and record.name.startswith(('2616_','2618_','2620_','2624_')) and 'dev-foundation' in record.read_text(),'original result branch, not spec/current Git')
        tools={}
        for name,suffix,version in [('junitPlatformLauncher','/junit-platform-launcher-1.13.4.jar','1.13.4'),('jacocoAgent','/org.jacoco.agent-0.8.15-runtime.jar','0.8.15')]:
            deps=raw['begin']['dependencyHashes'];matches=[p for p in deps if p.endswith(suffix)]
            require(len(matches)==1,'one SDK');path=matches[0]
            require(data.sha(Path(path).read_bytes())==deps[path],'original SDK hash')
            tools[name]=dict(version=version,path=path,sha256=deps[path])
        expected[run]=dict(source=SOURCE,parentManifest=str(original.relative_to(data.ROOT)),parentManifestSha256=pin,qualificationHead=raw['begin']['qualificationHead'],branch='dev-foundation',branchBasis='CONTEMPORANEOUS_NUMBERED_PT_RESULT_NOT_RECONSTRUCTED_FROM_CURRENT_BRANCH',branchRecord=entry['branchRecord'],branchRecordSha256=data.sha(record.read_bytes()),startUTC=stage['startUTC'],endUTC=stage['endUTC'],actualExit=stage['actualExit'],commandReference=str(original.relative_to(data.ROOT))+'#/stages/1/command',commandSha256=data.sha(json.dumps(stage['command'],separators=(',',':')).encode()),reportedEnvironment=reported,toolDependencies=tools,originalLogSha256=stage['logSha256'],allowedPrefixKeys=list(KEYS),unknownLogLinesPublished=False,originalTestsReexecuted=0)
    assess(envelope,expected)
    negatives=0
    for field,bad in [('actualExit',1),('source','OLD_SOURCE'),('productTestsExecuted',39),('newAccepted',1),('currentEnvironmentSubstituted',True),('originalParentManifestsChanged',True),('whole451Accepted',True)]:
        wrong=copy.deepcopy(envelope);wrong[field]=bad
        try:assess(wrong,expected)
        except ValueError:negatives+=1
        else:raise ValueError('metadata negative accepted')
    for bad in [[],['runtime.version=25.0.4\n']*4,[k+'=x\n' for k in KEYS],[k+'=Linux\n' for k in KEYS],['runtime.version=25.0.4\n','os.name=Linux\n','os.arch=amd64\n','os.version=bad\x01\n']]:
        try:headers(bad)
        except ValueError:negatives+=1
        else:raise ValueError('prefix negative accepted')
    require(negatives==12,'all metadata negatives')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifest=str(parent.relative_to(data.ROOT)),parentManifestSha256=PIN,originalParents=PARENTS,independentEnvironmentBindings=4,negativeMetadataChecks=negatives,productTestsExecuted=0,newAccepted=0,actualExternalOperations=0,originalManifestsUnchanged=True,formalUpdated=False,whole451Accepted=False,bugs=['BUG2096','BUG2097'],horizontal=['YKT1843','YKT1844']))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()

