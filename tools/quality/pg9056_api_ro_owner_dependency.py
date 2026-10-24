"""Thirteen public artifact dependency audit, no product initializer/JDBC/native/service action."""
import datetime as dt
import json
from pathlib import Path
import subprocess
from host_tool_invocation import capture,verify
import pg6966_chr_adapter_host as host

SOURCE='2ed81b14bb41512e1cda720a446ed7b261121605'
DESIGN='8b91944df5820535e23ba2469740f1c0aa94c447'
OUT=host.BASE/'PG9056-api-ro-owner-dependency-v1'
SS=[
 'documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md',
 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md',
 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md',
 'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md']
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'
PATHS=[*SS,API+'bootstrap/ApiJdbcPool.java',API+'bootstrap/ApiProcessMain.java',
 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/file/ServiceProcessResources.java',
 'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java',
 API+'monitoring/persistence/OutboxObservationRepository.java',API+'monitoring/ApiOutboxObservationSource.java',
 API+'monitoring/ApiServiceMetricBinding.java',
 'src/deployment/monitoring/prometheus/standard.yml.template','src/deployment/monitoring/prometheus/debug.yml.template']


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and len(PATHS)==len(set(PATHS))==13
    assert subprocess.check_output(['git','rev-parse','origin/main'],cwd=host.ROOT,text=True).strip()==DESIGN
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    rows=[];texts={}
    for path in PATHS:
        assert (host.ROOT/path).is_file() and not (host.ROOT/path).is_symlink()
        raw=(host.ROOT/path).read_bytes();texts[path]=raw.decode('utf-8')
        ref=DESIGN if path in SS else SOURCE
        assert subprocess.check_output(['git','show',ref+':'+path],cwd=host.ROOT)==raw
        rows.append(dict(path=path,sha256=host.sha(host.ROOT/path),source=ref,kind='APPROVED_DESIGN' if path in SS else 'CURRENT_PRODUCT'))
    pool=texts[API+'bootstrap/ApiJdbcPool.java'];repo=texts[API+'monitoring/persistence/OutboxObservationRepository.java']
    caller=texts[API+'bootstrap/ApiProcessMain.java'];cache=texts[API+'monitoring/ApiOutboxObservationSource.java']
    assert all(value in pool for value in ('setConnectionTimeout(3_000)','setAutoCommit(true)','setReadOnly(false)','setMaximumPoolSize(8)'))
    assert all(value in repo for value in ('connection.getAutoCommit()','!connection.isReadOnly()','Connection.TRANSACTION_READ_COMMITTED','QUERY_TIMEOUT_SECONDS = 1','try (statement)','try (rows)'))
    assert 'ApiOutboxObservationSource' not in caller and 'ApiServiceMetricBinding.prepareContext(' in caller
    assert 'current.compareAndSet(pending, new Entry(supplied))' in cache and 'getConnection(' not in cache
    for path in PATHS[-2:]:
        config=json.loads(texts[path]);assert config['global']['scrape_interval']=='15s' and config['global']['scrape_timeout']=='5s'
    findings=[
      dict(id='RODEP01',contract='Pool borrowed, default RW/autocommit; RO must be a separate checkout/transaction',status='CONFIRMED',next='No business dispatcher Connection reuse or pool mode mutation'),
      dict(id='RODEP02',contract='Read-only/read-committed/non-autocommit plus one-second statement timeout',status='CONFIRMED',next='Prepare checkout before query, rollback once and confirm close before successful observation result'),
      dict(id='RODEP03',contract='Get/missing lock-free and SDK-independent; pending identity rejects invalidated read',status='CONFIRMED',next='Future producer must publish only after its owned connection cleanup; current borrowed-read cache alone is not that owner'),
      dict(id='RODEP04',contract='Unknown release retains exact owner frame; no clean-return or downstream pool close',status='CONFIRMED',next='Finite attempt needs prebuilt retaining policy and explicit ownership before acquisition; fake finite callback may return only with same failure rethrown'),
      dict(id='RODEP05',contract='Scrape15s/timeout5s is exporter schedule, not sampler/transaction/stop total budget',status='DISTINCT_NOT_INFERRED',next='Choose/test internal sampling separately from SS/API external contracts; deadline continues existing parent/Unit contract'),
      dict(id='RODEP06',contract='Actual caller has no RO source/producer; actual SDK source default empty',status='UNSUPPLIED_HOLD',next='Finite read/cleanup attempt PG/PT can precede worker integration; actual start/native/Pool lifetime require their own held acceptance')]
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),source=SOURCE,designSource=DESIGN,
      invocation=invocation,artifacts=rows,artifactCount=13,dependencies=findings,newTests=0,newMain=0,newAccepted=0,formalUpdated=False,coverage=None,
      actualProductInitializers=0,actualJdbcCalls=0,actualVmActions=0,actualNetworkTargets=0,
      nextPermittedEngineering='Finite read-only connection attempt with cleanup-confirmed result and injected UNKNOWN-retaining policy; own doubles only, then cache publication/producer integration as separate dependent PG/PT',
      noNewApprovalRequiredForInternalDetail=True,actualProducerIntegrationAccepted=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,artifacts=13,dependencyRows=6,newTests=0,newAccepted=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
