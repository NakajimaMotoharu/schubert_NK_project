"""Public template fmt stdout only; no overwrite, provision, keys, service or socket action."""
import datetime as dt
import json
from pathlib import Path
import subprocess
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from caddy_public_format_contract import equal

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9010-caddy-format-candidate-v1'
OUT=BASE/'PG9010-caddy-format-candidate-v1'
BINARY=ROOT.parent/'characterization-tools/root/usr/bin/caddy'
BINARY_SHA='678c1849799e6d81c7cfbe63cebb8f92400cb70a67fc9f601697cb8ce7cdfa4a'
ARTIFACT='src/deployment/caddy/Caddyfile.template'


def write(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    assert sha(BINARY.read_bytes())==BINARY_SHA
    old=(ROOT/ARTIFACT).read_bytes()
    assert subprocess.check_output(['git','show','e7d64fda2453e906ee6ccc5fe718e5c29841e4aa:'+ARTIFACT],cwd=ROOT)==old
    SLOT.mkdir(mode=0o700)
    input_path=SLOT/'public-input.Caddyfile'
    with input_path.open('xb') as stream:stream.write(old)
    env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','HOME':str(SLOT),
         'XDG_CONFIG_HOME':str(SLOT/'xdg-config'),'XDG_DATA_HOME':str(SLOT/'xdg-data')}
    command=[str(BINARY),'fmt',str(input_path)]
    start=dt.datetime.now(dt.timezone.utc).isoformat()
    write(SLOT/'begin.safe.json',dict(command=command,startUTC=start,inputSha256=sha(old),binarySha256=BINARY_SHA))
    child=subprocess.Popen(command,cwd=SLOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    ticks=(Path('/proc')/str(child.pid)/'stat').read_text().rsplit(')',1)[1].split()[19]
    write(SLOT/'process.safe.json',dict(pid=child.pid,startTicks=ticks,command=command,cwd=str(SLOT),startUTC=start))
    try:stdout,stderr=child.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        child.kill();child.communicate();raise TimeoutError('own fmt deadline') from None
    terminal=dict(actualExit=child.returncode,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),stdoutBytes=len(stdout),stderrBytes=len(stderr))
    write(SLOT/'terminal.safe.json',terminal)
    assert child.returncode==0 and 0<len(stdout)<16384 and not stderr
    equal(old.decode('utf-8'),stdout.decode('utf-8'))
    assert old!=stdout and input_path.read_bytes()==old and (ROOT/ARTIFACT).read_bytes()==old
    assert not (SLOT/'xdg-config').exists() and not (SLOT/'xdg-data').exists()
    verify(invocation);OUT.mkdir()
    for name,content in [('original.Caddyfile.template',old),('candidate.Caddyfile.template',stdout)]:
        with (OUT/name).open('xb') as stream:stream.write(content)
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
       source='fb9fce0f91de3d9fdfa634fe277592700f915e45',artifact=ARTIFACT,
       originalSha256=sha(old),candidateSha256=sha(stdout),binarySha256=BINARY_SHA,version='2.6.2',
       command=command,terminal=terminal,logicalCommentQuotedTokensPreserved=True,inputUnchanged=True,
       productionEdited=False,onlyFmtExecuted=True,validateProvisionRunStartReloadExecuted=False,
       xdgStateCreated=False,actualTargetConnections=0,vmActions=0,privateCredentialReads=0,
       bug='BUG-1728',ykt='YKT-1479',productTestsExecuted=0,coverage=None,formalUpdated=False)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,originalSha256=sha(old),candidateSha256=sha(stdout),tokensPreserved=True,productionEdited=False)))


if __name__=='__main__':main()
