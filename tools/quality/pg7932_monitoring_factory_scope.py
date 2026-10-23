"""Bounded public source/catalog audit; presence is never runtime or PT acceptance."""
import json
import re
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7932-monitoring-factory-scope-v1'
SOURCE='23b74be401690ecb0f0007a66869c4ea2a699b02'
SPEC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'
def require(value,message):
    if not value:raise ValueError(message)
def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only bounded audit')
    require(subprocess.run(['git','diff','--quiet',SOURCE,'HEAD','--','src'],cwd=host.ROOT).returncode==0,'Production candidate unchanged since qualification')
    ss=host.ROOT/SPEC;text=ss.read_text();catalog=text.split('## 6. Metric catalog',1)[1].split('## 7. Alert condition',1)[0];contracts=[]
    for line in catalog.splitlines():
        cells=line.split('|')
        if len(cells)<6:continue
        for name in re.findall(chr(96)+r'(nk_[a-z0-9_]+)'+chr(96),cells[1]):
            contracts.append(dict(name=name,kind=cells[2].strip(),labels=[v.strip() for v in cells[3].split(',')]))
    require(contracts and len({r['name'] for r in contracts})==len(contracts),'all unique explicit SS catalog rows')
    files=[]
    for role in ('api','web','batch'):
        base=host.ROOT/f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring'
        files.extend(sorted(base.rglob('*.java')))
    inputs={};texts={}
    for f in files:
        path=str(f.relative_to(host.ROOT));blob=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        require(f.read_bytes()==blob,'every selected public source exact committed byte')
        inputs[path]=host.sha(f);texts[path]=f.read_text()
    rows=[]
    for contract in contracts:
        occurrences=[];literal_factories=[]
        for path,code in texts.items():
            for n,line in enumerate(code.splitlines(),1):
                if '"'+contract['name']+'"' in line:
                    occurrences.append(dict(path=path,line=n,kind='CATALOG_METADATA' if Path(path).name.endswith('MetricContract.java') else 'SOURCE_LITERAL_NOT_RUNTIME_PROOF'))
            for m in re.finditer(r'\b(Counter|Gauge|Timer|DistributionSummary)\.builder\(\s*"'+re.escape(contract['name'])+r'"',code):
                literal_factories.append(dict(path=path,line=code.count('\n',0,m.start())+1,sdkType=m.group(1),qualification='STATIC_LITERAL_FACTORY_ONLY'))
        rows.append(dict(**contract,literalOccurrences=occurrences,literalFactories=literal_factories,
          indirectFactoryMayExist=True,runtimeAccepted=False,absenceOutsideSelectedPackagesNotInferred=True))
    extra=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogOutboxRepository.java']
    for path in extra:
        f=host.ROOT/path;require(f.read_bytes()==subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT),'exact technical Web repository source')
        inputs[path]=host.sha(f)
    web_repo=(host.ROOT/extra[0]).read_text()
    require('schubert_web_session.web_log_outbox' in web_repo and all("'"+s+"'" in web_repo for s in ('PENDING','SENT','ERROR')),'Web store and three actual persisted status literals')
    web_files={p:c for p,c in texts.items() if '/schubert-nk-web/' in p}
    require(all('nk_outbox_rows' not in c and 'nk_outbox_oldest_seconds' not in c for c in web_files.values()),'no Web outbox literal factory in explicitly selected monitoring sources, not global absence')
    library_root=host.TC/'m2/repository'
    exporter_paths=sorted(str(p.relative_to(library_root)) for p in library_root.rglob('*.jar')
      if 'micrometer-registry-prometheus' in str(p) or 'prometheus-metrics' in str(p))
    value=dict(actualExit=0,source=SOURCE,auditHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
      invocation=invocation,specification=dict(path=SPEC,sha256=host.sha(ss)),boundedSourceInputs=inputs,
      catalog=rows,catalogNames=len(rows),monitoringJavaFiles=len(files),selectedWebMonitoringFiles=len(web_files),
      webTechnicalStore=dict(path=extra[0],schema='schubert_web_session',table='web_log_outbox',statuses=['PENDING','SENT','ERROR'],
        businessSchemaAuthority=False,actualDbAccess=False),
      installedExporterPathInventory=dict(root=str(library_root),nameFilter=['micrometer-registry-prometheus','prometheus-metrics'],jarPaths=exporter_paths,
        missingGloballyNotInferred=True,downloadOrInstallAttempted=False),
      nextCandidate='Web fixed-store outbox count/oldest observation kernel and JDBC proxy-only read/publication; actual DB/scheduler/exporter held',
      productTestsExecuted=0,targetInitialization=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,
      formalUpdated=False,newAccepted=0,effortPercent=None,ptAlternative=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,catalogNames=len(rows),monitoringJavaFiles=len(files),webMonitoringFiles=len(web_files),
      literalFactoryNames=sum(bool(r['literalFactories']) for r in rows),exporterMatchingJars=len(exporter_paths),manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
