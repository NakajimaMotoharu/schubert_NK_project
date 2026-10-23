"""Bounded repository deployment/retention gap evidence; no service, VM, private log or target initialization."""
import datetime
import gzip
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7706-monitoring-retention-scope-v1'
MANUAL=Path('/usr/share/man/man5/journald.conf.5.gz')
MANUAL_SHA='bbfc3a924a5c96800969bb69f4e0a5ea258d762e95a361fdf7487875724a718a'
DOCS=(
 'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md',
 'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md',
 'documents/200_UI/250_運用・非機能/252_ログ・監視・障害復旧設計.md',
 'documents/200_UI/250_運用・非機能/253_性能・容量・可用性・セキュリティ設計.md')
POLICY='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/MonitoringModePolicy.java'

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only repository audit')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip()
    names=subprocess.check_output(['git','ls-files','-z','--','src/deployment'],cwd=host.ROOT).decode().split('\0')[:-1]
    require(names and len(names)==len(set(names)),'exact tracked deployment scope')
    inventory={};journal=[]
    for name in names:
        file=host.ROOT/name;require(file.is_file() and not file.is_symlink(),'only regular tracked public templates')
        inventory[name]=host.sha(file)
        if name.startswith('src/deployment/systemd/') and file.suffix in ('.template','.service'):
            body=file.read_text()
            if 'StandardOutput=journal\n' in body and 'StandardError=journal\n' in body:journal.append(name)
    require(len(journal)==9,'all nine declared own application/broker units route stdout/stderr to journal')
    named=[p for p in names if any(word in p.lower() for word in ('prometheus','grafana','journald','logrotate','exporter','monitoring.target'))]
    require(not named,'named-template absence limited to this exact deployment inventory, not all code/runtime')
    policy=(host.ROOT/POLICY).read_text()
    require('DEBUG(true, 15, 5_000_000_000L)' in policy and 'STANDARD(false, 0, 0)' in policy
      and 'public void verifyObserved(Map<DetailService, Boolean> observed)' in policy,
      'existing concrete mode/decimal retention getters and four-service boolean guard')
    require('verifyObservedRetention' not in policy,'specific configuration-observation verifier is not present in this policy only')
    require(host.sha(MANUAL)==MANUAL_SHA,'exact local public installed manual, not guest/runtime state')
    manual=gzip.decompress(MANUAL.read_bytes()).decode()
    require('active files will stay around' in manual and 'only archived files are deleted' in manual,
      'actual local manual explicitly distinguishes active files from archived deletion limits')
    values=dict(actualExit=0,source=source,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      inspectedDeploymentFiles=inventory,journalOutputUnits=journal,namedMonitoringRetentionTemplates=named,
      absenceScope='TRACKED_SRC_DEPLOYMENT_PATH_NAMES_ONLY_NOT_ALL_IMPLEMENTATION_OR_RUNTIME',
      approvedDocumentHashes={p:host.sha(host.ROOT/p) for p in DOCS},
      modePolicy=dict(path=POLICY,sha256=host.sha(host.ROOT/POLICY),debugRetentionDays=15,debugRetentionBytes=5000000000,
        standardRetentionDays=0,standardRetentionBytes=0,completeServiceStateGuardPresent=True,observedRetentionConfigurationGuardPresent=False),
      localManual=dict(path=str(MANUAL),sha256=MANUAL_SHA,installedHostPackage='systemd 259.9-0ubuntu0.1',
        role='LOCAL_PUBLIC_REFERENCE_ONLY_NOT_TARGET_GUEST_QUALIFICATION',
        activeFilesMayRemainBeyondConfiguredLimits=True,nominalSettingsDoNotProveHardTotalUsedBytes=True),
      existingNativeCoverageExporterIsNotPrometheus='018/509 title/source scope describes NativeCoveragePrivateFile, not a monitoring daemon; no historical exporter tests replayed',
      nextBoundedImplementation='Extend existing MonitoringModePolicy with complete Optional retention configuration observation: DEBUG15/5000000000 exact, STANDARD0/0 exact, missing never zero; own ordinary independent PT',
      held=['Actual journald/files/service-retention total and permissions','monitoring target/service state/runtime','Prometheus storage implementation/runtime','Root11/VM/DB/key/native/deployment'],
      productionChanges=0,productionPtExecuted=0,targetInitialization=False,actualVmActions=0,actualDatabaseActions=0,
      formalUpdated=False,newAccepted=0,effortPercent=None,old4222Replayed=False,old44Replayed=False)
    require(inventory=={p:host.sha(host.ROOT/p) for p in names},'all inspected public template inputs unchanged')
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',values)
    print(json.dumps(dict(actualExit=0,templates=len(inventory),journalUnits=len(journal),namedTemplates=len(named),
      productionPt=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
