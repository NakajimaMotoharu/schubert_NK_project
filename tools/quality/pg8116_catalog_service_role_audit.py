"""Bounded26 catalog-to-concrete-source/role audit, no class initialization or actual runtime access."""
import json
from pathlib import Path
import re
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG8116-catalog-service-role-audit-v1'
SOURCE='731d84d79fb44857dab999ef380f49d3d86ac375'
SPEC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'
BINDINGS={
 'nk_http_requests_total':[('web','HttpMetricRecorder','Counter.builder(Metric.REQUESTS.externalName())')],
 'nk_http_request_duration_seconds':[('web','HttpMetricRecorder','Timer.builder(Metric.DURATION.externalName())')],
 'nk_mq_messages_total':[('api','MqMessageMetricRecorder','nk_mq_messages_total')],
 'nk_mq_processing_duration_seconds':[('api','MqProcessingDurationMetricRecorder','nk_mq_processing_duration_seconds')],
 **{name:[('api','MqPressureMetricRecorder',name)] for name in ('nk_mq_queue_messages','nk_mq_queue_bytes','nk_mq_address_memory_bytes','nk_mq_address_paged_bytes','nk_mq_paging_active','nk_mq_page_files')},
 'nk_mq_redeliveries_total':[('api','MqRedeliveryMetricRecorder','nk_mq_redeliveries_total')],
 'nk_outbox_rows':[('api','OutboxRowsMetricRecorder','nk_outbox_rows'),('web','WebOutboxMetricRecorder','nk_outbox_rows')],
 'nk_outbox_oldest_seconds':[('api','OutboxAgeMetricRecorder','nk_outbox_oldest_seconds'),('web','WebOutboxMetricRecorder','nk_outbox_oldest_seconds')],
 'nk_inbox_replays_total':[('api','InboxReplayMetricRecorder','nk_inbox_replays_total')],
 'nk_operation_token_mismatch_total':[('api','OperationMismatchMetricRecorder','nk_operation_token_mismatch_total')],
 'nk_async_jobs':[('api','AsyncJobMetricRecorder','nk_async_jobs')],
 'nk_db_pool_connections':[('api','DbPoolMetricRecorder','nk_db_pool_connections')],
 'nk_db_query_duration_seconds':[('api','DbQueryDurationMetricRecorder','nk_db_query_duration_seconds')],
 'nk_file_transfer_files':[('batch','TransferMetricRecorder','MetricContract.FILE_TRANSFER_FILES.externalName()')],
 'nk_file_transfer_bytes':[('batch','TransferMetricRecorder','MetricContract.FILE_TRANSFER_BYTES.externalName()')],
 'nk_media_streams':[('web','MediaStreamsMetricRecorder','nk_media_streams')],
 'nk_media_bytes_total':[('web','MediaBytesMetricRecorder','nk_media_bytes_total')],
 'nk_integrity_failures_total':[('batch','IntegrityFailureMetricRecorder','nk_integrity_failures_total')],
 'nk_batch_runs_total':[('batch','BatchMetricRecorder','Counter.builder(contract.runsName())')],
 'nk_batch_last_success_timestamp_seconds':[('batch','BatchMetricRecorder','Gauge.builder(contract.lastSuccessName()')],
 'nk_process_restarts_total':[('batch','ProcessRestartMetricRecorder','nk_process_restarts_total')]
}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only bounded source/role map')
    require(subprocess.run(['git','diff','--quiet',SOURCE,'HEAD','--','src'],cwd=host.ROOT).returncode==0,'current Production source unchanged since qualification')
    spec=host.ROOT/SPEC;require(spec.read_bytes()==subprocess.check_output(['git','show','origin/main:'+SPEC],cwd=host.ROOT),'exact approved origin/main SS351')
    catalog=spec.read_text().split('## 6. Metric catalog',1)[1].split('## 7. Alert condition',1)[0];contracts=[]
    for line in catalog.splitlines():
        cells=line.split('|')
        if len(cells)<6:continue
        for name in re.findall(chr(96)+r'(nk_[a-z0-9_]+)'+chr(96),cells[1]):
            contracts.append(dict(name=name,kind=cells[2].strip(),labels=[s.strip() for s in cells[3].split(',')]))
    require(len(contracts)==26 and {r['name'] for r in contracts}==set(BINDINGS),'all26 approved names, no inferred extra scope')
    inputs={};texts={};files=[]
    for role in ('api','web','batch'):
        root=host.ROOT/f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring'
        files.extend(sorted(root.rglob('*.java')))
    for file in files:
        path=str(file.relative_to(host.ROOT));require(file.read_bytes()==subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT),'each selected committed source byte')
        inputs[path]=host.sha(file);texts[path]=file.read_text()
    rows=[]
    for contract in contracts:
        bindings=[]
        for role,name,fragment in BINDINGS[contract['name']]:
            path=f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{name}.java'
            code=texts[path];require(''.join(fragment.split()) in ''.join(code.split()),'exact concrete factory/typed-call source fragment')
            require(any(t+'.builder(' in code for t in ('Counter','Gauge','Timer','DistributionSummary')),'declared concrete SDK builder owner')
            bindings.append(dict(role=role,path=path,sha256=inputs[path],sourceFragment=fragment,
              status='STATIC_CONCRETE_OWNER_ONLY_NOT_RUNTIME_OR_PT_ACCEPTANCE'))
        rows.append(dict(**contract,concreteBindings=bindings,productionHookAccepted=False,sourceOwnerGenerationAccepted=False,
          schedulerExporterAccepted=False,heldTermination='ACTUAL_SOURCE_OWNER_ASOF_LIFETIME_SCHEDULER_EXPORTER_ROOT_HOLD'))
    pool='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebJdbcPool.java'
    code=(host.ROOT/pool).read_text();require((host.ROOT/pool).read_bytes()==subprocess.check_output(['git','show',SOURCE+':'+pool],cwd=host.ROOT),'exact existing Web pool owner source')
    require('config.setMaximumPoolSize(2);' in code and 'config.setMinimumIdle(1);' in code and 'config.setRegisterMbeans(false);' in code,'Web2/min1 and no management registration source contract')
    inputs[pool]=host.sha(host.ROOT/pool)
    api='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricRecorder.java'
    require('.tag("service", "API")' in texts[api],'existing pool facade fixed to API, not Web role')
    web={p:c for p,c in texts.items() if '/schubert-nk-web/' in p}
    require(not any('nk_db_pool_connections' in c or 'DbPoolMetric' in c for c in web.values()),'bounded current Web monitoring has no concrete pool observation facade, not global absence')
    references=[]
    for file in sorted((host.ROOT/'src').glob('*/src/main/java/**/*.java')):
        text=file.read_text()
        if 'nk_db_pool_connections' in text or 'DbPoolMetric' in text:
            references.append(dict(path=str(file.relative_to(host.ROOT)),sha256=host.sha(file),sourceKind='CATALOG' if file.name=='MetricContract.java' else 'PUBLIC_SOURCE_REFERENCE'))
    require(references and all('/schubert-nk-web/' not in r['path'] for r in references),'all current literal/type references, no Web producer inferred')
    value=dict(actualExit=0,source=SOURCE,auditHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
      invocation=invocation,specification=dict(path=SPEC,sha256=host.sha(spec)),catalog=rows,catalogNames=26,monitoringJavaFiles=len(files),
      boundedSourceInputs=inputs,allMainLiteralAndTypePoolReferences=references,
      webPoolGap=dict(existingPoolSource=pool,maximum=2,minimumIdle=1,managementRegistration=False,existingFacadeService='API',
        selectedWebMonitoringSources=len(web),webConcreteGetterRecorderCollectorPresent=False,globalRuntimeAbsenceNotInferred=True,
        nextSafeWork='Web fixed service WEB four-state Gauge plus borrowed HikariPoolMXBean/HikariConfigMXBean getter observation and owner-local complete publication; interface-proxy-only PT, no DataSource/pool open'),
      heldActualActions=['Root11','VM','DB','MQ','Backup','keys','native','network','intent-permit','deployment','unknown-refused-target'],
      standaloneFactoryIsNotRealExporterCompatibilityProof=True,sourceRoleAndMetricNamePresenceAreNotFinishedManufacture=True,
      productTestsExecuted=0,targetInitialization=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,
      formalUpdated=False,newAccepted=0,effortPercent=None,ptAlternative=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,catalogNames=26,monitoringJavaFiles=len(files),concreteBindings=sum(len(r['concreteBindings']) for r in rows),
      next='WEB_POOL_BORROWED_TYPED_GETTERS_ONLY',manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
