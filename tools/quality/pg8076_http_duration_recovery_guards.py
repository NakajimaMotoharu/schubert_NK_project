"""Seven new count-recovery negative checks on retained public90 evidence; no product PT/JVM."""
import copy
import json
from pathlib import Path
import pg8074_http_duration_terminal_recovery as recovery
from host_tool_invocation import capture,verify
OUT=recovery.host.BASE/'PG8076-http-duration-recovery-guards-v1'
def main():
    invocation=capture(Path(__file__))
    if OUT.exists():raise ValueError('new-only metadata guards')
    file=recovery.OUT/'manifest.json'
    if recovery.host.sha(file)!='73b279fcf921926243036c496de7704f7ef1cbdfb4d16a282f2026a8e7dfb1fc':raise ValueError('exact original recovered witness')
    report=json.loads(file.read_bytes());negative=[]
    recovery.validate_counts(report['suites'],report['cases'],recovery.SUMMARY)
    for kind in ('missing-suite','duplicate-case','partial-count','non-pass','unknown-owner','summary-incomplete','wrong-suite-count'):
        suites=copy.deepcopy(report['suites']);cases=copy.deepcopy(report['cases']);summary=recovery.SUMMARY
        if kind=='missing-suite':suites.pop(next(iter(suites)))
        elif kind=='duplicate-case':cases[-1]=copy.deepcopy(cases[0])
        elif kind=='partial-count':cases.pop()
        elif kind=='non-pass':cases[0]['result']='NOT_PASS';cases[0]['nonPass']=['skipped']
        elif kind=='unknown-owner':cases[0]['classname']='unknown.safe.fixture'
        elif kind=='summary-incomplete':summary=summary.replace('succeeded=90','succeeded=89')
        else:suites[next(iter(suites))]['tests']+=1
        try:recovery.validate_counts(suites,cases,summary)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('incomplete or forged ordinary result accepted')
    value=dict(actualExit=0,source=report['source'],invocation=invocation,witness=dict(path=str(file.relative_to(recovery.host.ROOT)),sha256=recovery.host.sha(file)),
      negativeGuards=negative,testsExecuted=0,newJvmStarted=0,actualVmActions=0,actualDatabaseActions=0,formalUpdated=False,newAccepted=0)
    verify(invocation);OUT.mkdir();recovery.host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,negativeGuards=7,productTestsExecuted=0,manifestSha256=recovery.host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
