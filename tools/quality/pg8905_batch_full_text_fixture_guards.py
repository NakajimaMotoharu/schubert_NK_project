"""BUG1722 actual host fixture contract + original two TWR counterexamples; Product PT0."""
import datetime
import json
from pathlib import Path
import re
import subprocess
import pg8900_batch_full_text_fixed_host as current
from host_tool_invocation import capture,verify

host=current.run.host
BEFORE='287eba60232970110a626bc2187cc9fcad2fe27f'
UNIT='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricTextTest.java'

def main():
    invocation=capture(Path(__file__))
    out=host.BASE/'PG8905-batch-full-text-fixture-guards-v1'
    assert not out.exists()
    before=subprocess.check_output(['git','show',BEFORE+':'+UNIT],cwd=host.ROOT,text=True)
    after=(host.ROOT/UNIT).read_text();current.fixture_contract(after)
    delta=subprocess.check_output(['git','diff','--name-only',BEFORE,current.SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines()
    assert delta==[UNIT]
    rejected=[];assertions={}
    for number in ('002','003'):
        marker='  @Test\n  void batchfull'+number
        a=after.index(marker);b=after.index('  @Test',a+len(marker))
        x=before.index(marker);y=before.index('  @Test',x+len(marker))
        original=''.join(before[x:y].split());fixed=''.join(after[a:b].split())
        pattern=r'(?:assertEquals|assertThrows|assertFalse|standard\.close)\([^;]*;'
        first=re.findall(pattern,original);second=re.findall(pattern,fixed)
        # An extra finally cleanup is added; all original observations/explicit-close remain.
        assert first and second==first+['standard.close();']
        assertions[number]=dict(originalObservations=first,additionalFinallyCleanup=1,allOriginalExpectationsRetained=True)
        changed=after[:a]+before[x:y]+after[b:]
        try: current.fixture_contract(changed)
        except (AssertionError,ValueError): rejected.append('restore-TWR-'+number)
        else: raise AssertionError('each original compiler-failing fixture must reject')
    verify(invocation);out.mkdir()
    host.write(out/'manifest.json',dict(actualExit=0,source=current.SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,bug='BUG-1722',ykt='YKT-1473',actualHostGuardSha256=host.sha(Path(current.__file__)),sourceSha256=host.sha(host.ROOT/UNIT),onlyUnitChanged=True,originalAssertions=assertions,metadataCounterexamples=rejected,productPtExecuted=0,coverage=None,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,originalAssertionsRetained=True,metadataCounterexamples=len(rejected),manifestSha256=host.sha(out/'manifest.json'))))

if __name__=='__main__':
    main()
