"""Public caller/context lifetime contracts only; no Main initializer or real service operation."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture, verify

SOURCE='fdc229c9a7b7759cea106d1126c8da0f27a70e09'
DESIGN='8b91944df5820535e23ba2469740f1c0aa94c447'
OUT=host.BASE/'PG9146-api-observation-assembly-dependencies-v1'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'
SS=['documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md',
    'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md']
PATHS=[*SS,API+'bootstrap/ApiProcessMain.java',API+'bootstrap/ApiProcessLifetime.java',
    API+'bootstrap/ApiManagementServer.java',API+'monitoring/ApiMetricContext.java',
    API+'monitoring/OwnedApiObservationWorker.java',API+'monitoring/ApiOutboxObservationPump.java',
    API+'monitoring/ApiReadOnlyObservationAttempt.java',API+'monitoring/ApiServiceMetricBinding.java',
    'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/file/ServiceProcessResources.java',
    'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java']

def protocol(texts):
    main=texts[API+'bootstrap/ApiProcessMain.java']
    positions=[main.index(token) for token in ('new ServiceProcessResources(','.executeRetainingUnknown(', 'ApiServiceMetricBinding.prepareContext(', 'metrics.initialize();','ApiManagementServer.bind(', 'management.start();')]
    assert positions==sorted(positions)
    assert 'OwnedApiObservationWorker' not in main and 'ApiOutboxObservationPump' not in main
    life=texts[API+'bootstrap/ApiProcessLifetime.java']
    assert 'void fail()' in life and 'failed.set(true);' in life and 'if (failed.get()) throw new IOException' in life
    assert 'LongSupplier' not in life and 'nanoTime' not in life
    manager=texts[API+'bootstrap/ApiManagementServer.java']
    assert 'Duration.ofSeconds(30)' in manager and 'void closeWithin(Duration remaining)' in manager
    assert 'ApiMetricContext<?> context' in manager and 'context.close()' not in manager
    context=texts[API+'monitoring/ApiMetricContext.java']
    assert 'setup.apply(source)' in context and 'ownedCustom.ifPresent(MeterRegistry::close)' in context
    assert 'getConnection(' not in context
    worker=texts[API+'monitoring/OwnedApiObservationWorker.java']
    assert 'awaitStopped(LongSupplier remainingNanos)' in worker and 'firstRemaining - elapsed' in worker
    retention=texts[PATHS[-2]]
    assert 'public static Consumer<Throwable> unknownReleasePolicy()' in retention
    assert 'onUnconfirmed.accept(unconfirmed);' in retention and 'throw unconfirmed;' in retention
    assert 'Web 30s/API 60s' in texts[SS[0]]

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists() and len(PATHS)==len(set(PATHS))==12
    assert subprocess.check_output(['git','rev-parse','origin/main'],cwd=host.ROOT,text=True).strip()==DESIGN
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    texts={}; rows=[]
    for path in PATHS:
        actual=host.ROOT/path; assert actual.is_file() and not actual.is_symlink()
        raw=actual.read_bytes(); ref=DESIGN if path in SS else SOURCE
        assert subprocess.check_output(['git','show',ref+':'+path],cwd=host.ROOT)==raw
        texts[path]=raw.decode(); rows.append(dict(path=path,sha256=host.sha(actual),source=ref))
    protocol(texts); rejected=[]
    for name,path,old,new in (
      ('manager-before-context',API+'bootstrap/ApiProcessMain.java','metrics.initialize();','metrics.notInitialized();'),
      ('invented-lifetime-budget',API+'bootstrap/ApiProcessLifetime.java','void fail()','LongSupplier void fail()'),
      ('manager-renewed-cap',API+'bootstrap/ApiManagementServer.java','Duration.ofSeconds(30)','Duration.ofSeconds(60)'),
      ('sdk-does-io',API+'monitoring/ApiMetricContext.java','setup.apply(source)','getConnection(setup.apply(source))'),
      ('worker-renewed-budget',API+'monitoring/OwnedApiObservationWorker.java','firstRemaining - elapsed','remainingNanos.getAsLong()'),
      ('unknown-normalized',PATHS[-2],'throw unconfirmed;','return;')):
        changed=dict(texts); changed[path]=texts[path].replace(old,new,1); assert changed[path]!=texts[path]
        try: protocol(changed)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('invalid dependency accepted')
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      source=SOURCE,designSource=DESIGN,invocation=invocation,artifacts=rows,artifactCount=len(rows),
      dependencies=[
        dict(id='ASMDEP01',status='CONFIRMED',result='Pool outer; initialized context outer to borrowing Manager. New assembly must own worker before start and drain before SDK/Pool release.'),
        dict(id='ASMDEP02',status='CALLER_PORT_NOT_YET_SUPPLIED',result='Lifetime has notification only; Unit60/Manager30/parent30min do not authorize resetting stop budget. Assembly can borrow explicit existing remaining supplier; Main integration remains pending.'),
        dict(id='ASMDEP03',status='PERMITTED_INDEPENDENT_PG_PT',result='Resource-free assembly with STD no worker/SQL; DEBUG separate readonly attempt and immutable cache, no I/O in SDK render.'),
        dict(id='ASMDEP04',status='PERMITTED_INDEPENDENT_PG_PT',result='Prebuilt failure and retaining policies; finite fixture does not prove real UNKNOWN recovery. Failed worker stop must prevent SDK close.')],
      metadataCounterexamples=rejected,newProductTests=0,newMain=0,newAccepted=0,formalUpdated=False,
      actualInitializers=0,actualJdbcCalls=0,actualVmActions=0,actualNetworkTargets=0,coverage=None,
      nextPermittedEngineering='Caller-held observation/metric assembly, explicit borrowed remaining budget, private JVM/fake ports only; real Main integration and native HOLD',
      whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,artifacts=len(rows),dependencies=4,metadataCounterexamples=len(rejected),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
