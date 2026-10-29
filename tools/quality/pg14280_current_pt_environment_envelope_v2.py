"""Current4 completed owned PT environmental prefixes only; no tests/JVM/process/VM/application-log access."""
import json
import re
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG14280-current-four-pt-environment-v2'
INPUTS={
 'PG14242-delivery-metadata-whole-two-pt-v1':('053ae4ab0d09af0eb25f711d58c00d5bb54cd88343be9d50e54fcf85b7377171','2616_API配送metadata元whole二件_実行結果.md'),
 'PG14252-inbound-primary-whole-five-pt-v1':('5b49c990cb01281ea26f7860256b7a09a0ea14becf1419cfce85e33cfc4ba888','2618_API受信例外primary元whole五件_実行結果.md'),
 'PG14256-protocol-carrier-whole-eight-pt-v1':('90bb7c8ff1b76cb6ae5fc78bf4766bc6fb65702a53923c56e6ecd6b5ab83ef71','2620_Protocol例外carrier元whole八件_実行結果.md'),
 'PG14270-web-three-forms-whole-twenty-four-pt-v1':('b86d3cc5ef5309104d8dfc85e215c193ac04ae7d054deca89da61e7c2520cadd','2624_Web三form元whole二十四件_実行結果.md')}
KEYS=('runtime.version','os.name','os.arch','os.version')

def require(ok,message):
    if not ok:raise ValueError(message)

def parse_headers(lines):
    found={}
    for line in lines:
        require(isinstance(line,str) and len(line)<=512,'bounded own prefix line')
        for key in KEYS:
            if line.startswith(key+'='):
                value=line[len(key)+1:].rstrip('\n')
                require(key not in found and re.fullmatch('[A-Za-z0-9._+ -]{1,128}',value) is not None,'unique permitted environment scalar')
                found[key]=value
    require(set(found)==set(KEYS) and found['runtime.version'].startswith('25.0.4') and found['os.name']=='Linux','all original reported JDK25.0.4/Linux environmental fields')
    return found

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only environment supplement')
    entries={}
    for run,(pin,record_name) in INPUTS.items():
        parent=data.BASE/run/'manifest.json';raw=data.read_checked(parent,pin)
        require(raw['source']==SOURCE and raw['actualExit']==0 and len(raw['stages'])==2 and all(s['actualExit']==0 and not s['timedOut'] for s in raw['stages']),'original completed own PT source/terminal')
        slot=data.ROOT.parent/'pgpt-runs/PG379'/run.lower();log=slot/'selected-junit.log'
        require(log.resolve()==log and not log.is_symlink() and data.sha(log.read_bytes())==raw['stages'][1]['logSha256'],'fixed original own tool log, not application or external raw log')
        lines=[];size=0
        with log.open() as stream:
            for _ in range(32):
                line=stream.readline(513)
                if not line:break
                size+=len(line.encode());require(size<=4096,'bounded prefix maximum4096 bytes')
                lines.append(line)
        headers=parse_headers(lines)
        record=data.ROOT/'evidence/01_PT/018_NK-OPS-001'/record_name
        require('dev-foundation' in record.read_text(),'explicit contemporaneous branch result')
        deps=raw['begin']['dependencyHashes']
        versions={}
        for component,ending,version in [('junitPlatformLauncher','/junit-platform-launcher-1.13.4.jar','1.13.4'),('jacocoAgent','/org.jacoco.agent-0.8.15-runtime.jar','0.8.15')]:
            matches=[p for p in deps if p.endswith(ending)];require(len(matches)==1,'one actual fixed tool dependency')
            path=matches[0];require(data.sha(Path(path).read_bytes())==deps[path],'original SDK byte hash unchanged')
            versions[component]=dict(version=version,path=path,sha256=deps[path])
        command=raw['stages'][1]['command'];require('-Duser.timezone=Asia/Tokyo' in command,'recorded original JVM timezone')
        entries[run]=dict(source=SOURCE,parentManifest=str(parent.relative_to(data.ROOT)),parentManifestSha256=pin,qualificationHead=raw['begin']['qualificationHead'],branch='dev-foundation',branchBasis='CONTEMPORANEOUS_NUMBERED_PT_RESULT_NOT_RECONSTRUCTED_FROM_CURRENT_BRANCH',branchRecord=str(record.relative_to(data.ROOT)),branchRecordSha256=data.sha(record.read_bytes()),startUTC=raw['stages'][1]['startUTC'],endUTC=raw['stages'][1]['endUTC'],actualExit=raw['stages'][1]['actualExit'],commandReference=str(parent.relative_to(data.ROOT))+'#/stages/1/command',commandSha256=data.sha(json.dumps(command,separators=(',',':')).encode()),reportedEnvironment=headers,toolDependencies=versions,originalLogSha256=raw['stages'][1]['logSha256'],allowedPrefixKeys=list(KEYS),unknownLogLinesPublished=False,originalTestsReexecuted=0)
    require(len(entries)==4,'all four current original executions')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,entries=entries,executionEnvironmentFromOriginalJVM=True,currentEnvironmentSubstituted=False,originalParentManifestsChanged=False,productTestsExecuted=0,actualExternalOperations=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,bugs=['BUG2096'],horizontal=['YKT1843']))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
