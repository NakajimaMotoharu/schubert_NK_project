"""Read-only final trace and all six source-specific registers; no test replay."""
import datetime
import json
import os
import subprocess

import pg6958_recovery_catalog as first
import pg6962_jms_f02_criteria as jms
import pg6964_c03_acceptance as config
import pg6984_chr_adapter_acceptance as adapter
import pg6986_chr_comparison_acceptance as comparison
import pg6988_chr_gate_parent_acceptance as gate
import wbs_progress_audit as audit


def main():
    result=audit.verify()
    checks=[]
    for path,verifier in (
      ('488_当source個別受入_必要四依存・catalog.json',first.verify_register),
      ('489_当source個別受入_初回九項目.json',jms.verify_register),
      ('490_当source個別受入_C03追加.json',config.verify),
      ('491_当commonSource個別受入_adapter・必要F02.json',adapter.verify),
      ('492_当commonSource個別受入_比較DIF追加.json',comparison.verify),
      ('493_当commonSource個別受入_gate・親閉鎖.json',gate.verify)):
        item=first.PMO/path
        value=verifier(json.loads(item.read_bytes()))
        checks.append(dict(path=str(item.relative_to(first.ROOT)),sha256=first.sha(item),result=value))
    value=dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               command='python3 -B tools/quality/pg6994_recovery_trace_closure.py',
               head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=first.ROOT,text=True).strip(),
               toolSha256=first.sha(__import__('pathlib').Path(__file__)),
               inventorySha256=first.sha(first.PMO/'485_WBS網羅性・受入対応.json'),
               snapshotSha256=first.sha(first.PMO/'486_WBS現行実績.json'),
               fullDefaultAudit=result,sourceSpecificRegisterChecks=checks,
               managementObserved={'count':28,'actualExit':0,'evidenceLevel':'OBSERVED_TOOL_OUTPUT_NO_REPLAY_FOR_LOG_GENERATION'},
               testsExecuted=0,actualVmActions=0,original4222Repeated=False,original44Repeated=False,
               newAcceptanceDelta=0,formalUpdated=False,effortPercent=None)
    os.umask(0o077);out=first.BASE/'PG6994-recovery-trace-closure-v1';out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps(dict(actualExit=0,registers=6,historicalAcceptedTasks=result['acceptedTasks'],
                         physicalArtifacts=result['currentPhysicalCandidate']['physicalArtifacts'],
                         productionSource=result['currentPhysicalCandidate']['source'],
                         commonSource=result['currentPhysicalCandidate']['componentOverlay']['source'],
                         testsReplayed=0,manifestSha256=first.sha(out/'manifest.json'))))


if __name__=='__main__':main()
