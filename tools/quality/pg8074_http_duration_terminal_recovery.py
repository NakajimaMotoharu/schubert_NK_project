"""BUG1682: recover completed original90/11 only; no step(), subprocess or new test/job."""
import datetime
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import pg8060_http_duration_safe_host as original
from host_tool_invocation import capture,verify

host=original.host
OUT=host.BASE/'PG8074-http-duration-terminal-recovery-v1'
SUMMARY='found=90;started=90;succeeded=90;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
def require(value,message):
    if not value:raise ValueError(message)

def validate_counts(suites,cases,summary):
    expected={'dev.codex.schubert.nk.web.monitoring.'+name:dict(tests=count,failures=0,errors=0,skipped=0)
      for name,count in original.COUNTS.items()}
    require(len(expected)==11 and sum(v['tests'] for v in expected.values())==90,'declared specification11/90 and helper counts')
    require(suites==expected and len(cases)==90 and len({(r['classname'],r['name']) for r in cases})==90
      and all(r['classname'] in expected and r['name'] and r['result']=='PASS' and not r['nonPass'] for r in cases)
      and summary==SUMMARY,'exact original complete90/11/FES0, never partial results')
    actual={name:sum(r['classname']==name for r in cases) for name in expected}
    require(all(actual[name]==expected[name]['tests'] for name in expected),'every XML suite count matches actual original cases')

def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists() and not (original.SLOT/'manifest.safe.json').exists() and not original.OUT.exists(),'new-only first recovery, no existing original terminal overwrite')
    begin=json.loads((original.SLOT/'begin.safe.json').read_bytes())
    compiled=json.loads((original.COMPILE/'manifest.safe.json').read_bytes())
    require(compiled['source']=='27324ee12173955ff7bace340c99dd36a891d324'==begin['source']
      and compiled['actualExit']==compiled['terminal']['actualExit']==0 and compiled['testsExecuted']==0
      and begin['compileManifestSha256']==host.sha(original.COMPILE/'manifest.safe.json')
      and begin['archiveSha256']==compiled['begin']['archiveSha256']==host.sha(original.COMPILE/'source.tar')
      and begin['selectedSuites']==original.COUNTS and begin['expectedTests']==90,'fixed source/archive/compile and declared90')
    require(begin['helperSha256']==host.sha(original.HELPER),'original launcher helper unchanged')
    snapshot=original.COMPILE/'snapshot'
    require(all(host.sha(snapshot/p)==digest for p,digest in compiled['begin']['inputHashes'].items())
      and all(host.sha(Path(p))==digest for p,digest in begin['dependencyHashes'].items()),'all original source and executed dependencies unchanged')
    cpfile=snapshot/'src/schubert-nk-web/target/pgpt-test-classpath.txt'
    require(host.sha(cpfile)==begin['classpathFileSha256'],'exact original classpath metadata')
    verify(begin['invocation']);stages=[];stage_pins=[]
    for name in ('launcher-compile','selected-junit'):
        start=original.SLOT/(name+'-begin.safe.json');exitfile=original.SLOT/(name+'-exit.safe.json')
        processfile=original.SLOT/(name+'-process.safe.json');log=original.SLOT/(name+'.log')
        start_row=json.loads(start.read_bytes());exit_row=json.loads(exitfile.read_bytes());process=json.loads(processfile.read_bytes())
        require(exit_row['actualExit']==0 and exit_row['command']==start_row['command']==process['command']
          and exit_row['startUTC']==start_row['startUTC']==process['startUTC']
          and process['cwd']==str(snapshot) and host.sha(log)==exit_row['logSha256']
          and datetime.datetime.fromisoformat(exit_row['endUTC'])>=datetime.datetime.fromisoformat(exit_row['startUTC']),
          'genuine original owned terminal0 and exact command/log hash, no historical PID inference')
        stages.append(exit_row);stage_pins.append(dict(name=name,beginSha256=host.sha(start),exitSha256=host.sha(exitfile),processSha256=host.sha(processfile),logSha256=host.sha(log)))
    require(stages[-1]['command'][-2:]==['HttpDurationSafeJunitLauncher',str(original.SLOT/'xml')],'actual selected original JVM entrypoint')
    suites={};cases=[];hashes={}
    for file in sorted((original.SLOT/'xml').glob('TEST-*.xml')):
        root=ET.parse(file).getroot();name=root.get('name');require(name not in suites,'no repeated XML suite')
        suites[name]={k:int(root.get(k,'0')) for k in ('tests','failures','errors','skipped')};hashes[file.name]=host.sha(file)
        for case in root.findall('testcase'):
            require(case.get('classname')==name,'actual testcase owns its suite')
            cases.append(dict(classname=case.get('classname'),name=case.get('name'),result='PASS' if not list(case) else 'NOT_PASS',nonPass=[c.tag for c in case]))
    summaryfile=original.SLOT/'xml/summary.safe.txt';validate_counts(suites,cases,summaryfile.read_text())
    execfile=original.SLOT/'jacoco.exec';require(execfile.is_file() and execfile.stat().st_size>0,'actual original exec, CRC/session post still required')
    value=dict(source=compiled['source'],actualExit=0,begin=begin,stages=stages,suites=suites,cases=cases,xmlHashes=hashes,execSha256=host.sha(execfile),
      recoveredOriginalRun='PG8060-http-duration-safe-host-v1',failedOriginalPythonWrapperExitObserved=1,originalJUnitActualExit=0,
      recoveryTimeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),recoveryInvocation=invocation,originalInvocation=begin['invocation'],
      originalOwnedStagePins=stage_pins,summarySha256=host.sha(summaryfile),productTestsExecutedByRecovery=0,newJobsStarted=0,
      qualification='RECOVERED_ORIGINAL_RAW_TERMINAL_ONLY_POST_PENDING',whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    verify(invocation);verify(begin['invocation'])
    host.write(original.SLOT/'manifest.safe.json',value);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,originalJvmExit=0,originalWrapperExit=1,cases=90,suites=11,newTestsExecuted=0,source=value['source'],manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
