"""Independent compiler/long-arithmetic and exact-source guards; no worker/DB/Root replay."""
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import pg9134_api_observation_worker_host as selected
import scoped_prometheus_post as steps
from host_tool_invocation import capture,verify

host=selected.run.host
SLOT=host.W/'pg9137-worker-boundary-canaries-v1'
OUT=host.BASE/'PG9137-worker-boundary-canaries-v1'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java'
UNIT=MAIN.replace('/src/main/','/src/test/').replace('.java','Test.java')


def budget_contract(text):
    body=''.join(re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*','',text).split())
    sequence=['longfirstRemaining=remainingNanos.getAsLong();','if(firstRemaining<=0)thrownewIOException(UNCONFIRMED);',
      'longbegan=nanos.getAsLong();','longelapsed=nanos.getAsLong()-began;',
      'Math.min(firstRemaining-elapsed,remainingNanos.getAsLong())','if(elapsed<0||remaining<=0)thrownewIOException(UNCONFIRMED);']
    positions=[body.index(value) for value in sequence];assert positions==sorted(positions)
    assert body.count('firstRemaining=')==1 and 'unconfirmedStop.set(true);' in body


def serial_contract(text):
    start=text.index('static final class Signal extends Semaphore')
    end=text.index('    Signal()',start)
    rows=re.findall(r'^\s*((?:(?:private|static|final|volatile|transient)\s+)*)([A-Za-z]+)\s+(\w+)\s*(?:=|;)',text[start:end],re.M)
    fields={name:(kind,set(mods.split())) for mods,kind,name in rows if 'static' not in mods.split()}
    assert set(fields)=={'waiting','releases','waits','beforeWait','releaseFault','interrupt','immediateOnce'}
    expected={'waiting':'CountDownLatch','beforeWait':'Runnable','releases':'AtomicInteger','waits':'AtomicInteger','releaseFault':'Throwable','interrupt':'InterruptedException','immediateOnce':'AtomicBoolean'}
    assert all(fields[name][0]==kind for name,kind in expected.items())
    assert all('transient' in fields[name][1] for name in ('waiting','beforeWait'))
    return dict(runtimeOnlyTransient=['waiting','beforeWait'],otherSerializableTypes=['AtomicInteger','AtomicBoolean','Throwable','InterruptedException'],fieldCount=7)


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    normal=json.loads((selected.COMPILE/'manifest.safe.json').read_bytes())
    assert host.sha(selected.COMPILE/'manifest.safe.json')==selected.COMPILE_SHA and normal['actualExit']==0 and normal['source']==selected.SOURCE
    inputs=normal['begin']['inputHashes'];text=(host.ROOT/MAIN).read_text();unit=(host.ROOT/UNIT).read_text()
    assert host.sha(host.ROOT/MAIN)==inputs[MAIN] and host.sha(host.ROOT/UNIT)==inputs[UNIT]
    budget_contract(text);serial=serial_contract(unit);negative=[]
    for name,old,new in (
      ('no-initial-guard','if (firstRemaining <= 0) throw new IOException(UNCONFIRMED);',''),
      ('zero-slips','firstRemaining <= 0','firstRemaining < 0'),
      ('renewed-budget','firstRemaining - elapsed','remainingNanos.getAsLong()'),
      ('negative-elapsed-slips','elapsed < 0 || remaining <= 0','remaining <= 0')):
        changed=text.replace(old,new,1);assert changed!=text
        try:budget_contract(changed)
        except (AssertionError,ValueError):negative.append(name)
        else:raise AssertionError('budget guard drift accepted')
    for name,old,new in (
      ('latch-not-transient','final transient CountDownLatch waiting','final CountDownLatch waiting'),
      ('callback-not-transient','volatile transient Runnable beforeWait','volatile Runnable beforeWait')):
        changed=unit.replace(old,new,1);assert changed!=unit
        try:serial_contract(changed)
        except (AssertionError,ValueError):negative.append(name)
        else:raise AssertionError('serial field guard drift accepted')
    original=subprocess.check_output(['git','show','e155e239a548ed1b99cfe42710cbf6da2056e1a2:'+MAIN],cwd=host.ROOT).decode()
    try:budget_contract(original)
    except (AssertionError,ValueError):negative.append('original-negative-budget-source')
    else:raise AssertionError('original source accidentally accepted')
    paths=[f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring' for role in ('api','web','batch')]
    found=subprocess.run(['git','grep','-l','-E','extends Semaphore|implements Serializable','--',*paths],cwd=host.ROOT,text=True,capture_output=True,check=False)
    assert found.returncode==0 and found.stdout.splitlines()==[UNIT]
    SLOT.mkdir();steps.SLOT=SLOT;receipts=[];fixture_hashes={}
    javac=host.TC/'jdk-25.0.4/bin/javac';java=host.TC/'jdk-25.0.4/bin/java'
    for name,suffix,expected in [('pass','Pass',0),('reject-latch','LatchReject',1),('reject-callback','CallbackReject',1)]:
        path=host.ROOT/f'tools/quality/tests/fixtures/WorkerSignalSerializable{suffix}.java.txt';fixture_hashes[str(path)]=host.sha(path)
        work=SLOT/name;work.mkdir();classes=work/'classes';classes.mkdir();source=work/'WorkerSignalSerializableCanary.java';source.write_bytes(path.read_bytes())
        receipt,_=steps.step('serial-'+name,[str(javac),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(source)])
        assert receipt['actualExit']==expected and receipt['timedOut'] is False
        stderr=(SLOT/('serial-'+name+'.stderr.log')).read_text()
        assert ('[serial]' in stderr)==(expected==1)
        receipts.append(dict(kind='SYNTHETIC_COMPILER_CANARY_NOT_PRODUCT_PT',expectedExit=expected,receipt=receipt))
    helper=host.ROOT/'tools/quality/architecture/StopBudgetArithmeticCanary.java';fixture_hashes[str(helper)]=host.sha(helper)
    classes=SLOT/'arithmetic';classes.mkdir()
    compiled,_=steps.step('arithmetic-compile',[str(javac),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(helper)])
    assert compiled['actualExit']==0
    measured,output=steps.step('arithmetic-run',[str(java),'-cp',str(classes),'StopBudgetArithmeticCanary'])
    assert measured['actualExit']==0 and output.strip()=='WRAP_MAX=true; OLD_POSITIVE=1000; NONPOSITIVE=3; FROZEN=1,0'
    assert host.sha(host.ROOT/MAIN)==inputs[MAIN] and host.sha(host.ROOT/UNIT)==inputs[UNIT]
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      normalManifestSha256=selected.COMPILE_SHA,sourceHashes={MAIN:inputs[MAIN],UNIT:inputs[UNIT]},serialFieldProof=serial,fixtureHashes=fixture_hashes,
      compilerCanaries=receipts,independentArithmetic=dict(compile=compiled,run=measured,actualOutput=output.strip()),metadataCounterexamples=negative,
      horizontalTargets=[UNIT,MAIN,'ApiOutboxObservationPump:positive interval, sampling not stop budget'],otherMonitoringSerialFixtures=[],
      originalWorkerExecuted=False,actualSerializationWritten=False,productTestsExecuted=0,newTests=0,coverage=None,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,compilerCanaries=3,arithmeticVectors=6,metadataNegatives=len(negative),manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
