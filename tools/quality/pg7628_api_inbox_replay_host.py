"""Current106 ordinary API cases, supplied replay events only; no DB/JMS/Root replay."""
import json
from pathlib import Path
import subprocess
import pg7476_api_outbox_connection_host as previous
import pg7006_monitoring_pure_host as runner
from inbox_protocol_harness_contract import verify_harness

SLOT=runner.host.W/'pg7628-api-inbox-replay-host-v1'
POM=previous.POM
SUITES=(*previous.SUITES,'dev.codex.schubert.nk.api.monitoring.InboxReplayMetricRecorderTest')
PREFLIGHT=runner.host.BASE/'PG7625-api-inbox-protocol-preflight-v1/manifest.json'
PREFLIGHT_SHA='90ab797ac9b439f8ac6ac072db9f81f1a59d93c315cefa7819681224831e8a9c'
PROTOCOL_PATH='/home/mini/codex/project1/work/pgpt-runs/PG379/pg7614-dlq-health-six-compile-v1/snapshot/src/schubert-nk-protocol/target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar'
PROTOCOL_SHA='32889546dd787fc2a4aae09e430c25a429ee3f214e0afb86965906644f5a84ed'
DEPENDENCIES={**previous.DEPENDENCIES,PROTOCOL_PATH:PROTOCOL_SHA}

def verify_inputs():
    if runner.host.sha(PREFLIGHT)!=PREFLIGHT_SHA:raise ValueError('exact completed read-only dependency preflight')
    proof=json.loads(PREFLIGHT.read_bytes())
    if proof['actualExit']!=0 or proof['selectedProtocolJar']!=dict(path=PROTOCOL_PATH,sha256=PROTOCOL_SHA,classCount=176):
        raise ValueError('exact selected normal Jar')
    if runner.host.sha(Path(PROTOCOL_PATH))!=PROTOCOL_SHA:raise ValueError('actual normal Jar unchanged')
    if any(runner.host.sha(runner.host.ROOT/p)!=h for p,h in proof['protocolSourceInputs'].items()):
        raise ValueError('all current protocol input bytes unchanged')
    if runner.host.sha(Path(proof['m2Retained']['path']))!=proof['m2Retained']['sha256']:
        raise ValueError('stale M2 retained unchanged, never used')
    before=subprocess.check_output(['git','show','a605c7287:'+POM],cwd=runner.host.ROOT)
    return verify_harness(before,(runner.host.ROOT/POM).read_bytes(),PROTOCOL_PATH)

if __name__=='__main__':
    verify_inputs()
    runner.POM=POM;runner.DEPENDENCY_JARS=DEPENDENCIES
    runner.main(SLOT,SUITES)
