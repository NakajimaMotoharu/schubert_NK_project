"""Pinned official public config only, no target/credential access or scanner execution."""
import datetime as dt
import json
from pathlib import Path
import re
import tomllib
import urllib.request
from host_tool_invocation import capture, verify
from public_blob_scan import sha

ROOT=Path(__file__).resolve().parents[2]
SLOT=ROOT.parent/'pgpt-runs/PG379/pg8979-gitleaks-rule-provenance-v1'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8979-gitleaks-rule-provenance-v1'
URL='https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml'


def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    SLOT.mkdir(mode=0o700)
    request=urllib.request.Request(URL,headers={'User-Agent':'Schubert-NK-PGPT-public-rule-provenance'})
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request,timeout=30) as response:
        assert response.status==200 and response.geturl()==URL
        raw=response.read(512*1024+1)
    assert 0<len(raw)<=512*1024
    config=tomllib.loads(raw.decode('utf-8'))
    selected={row['id']:row for row in config['rules'] if row['id'] in {'generic-api-key','linear-client-secret'}}
    assert len(selected)==2
    for row in selected.values():
        regex=re.compile(row['regex'],re.ASCII)
        assert regex.groups==1
    path=SLOT/'gitleaks-v8.30.1.toml'
    with path.open('xb') as stream:stream.write(raw)
    path.chmod(0o600)
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
       source='fb9fce0f91de3d9fdfa634fe277592700f915e45',url=URL,path=str(path),bytes=len(raw),
       configSha256=sha(raw),version='8.30.1',ruleCount=len(config['rules']),rules=selected,
       globalAllowlist=config['allowlist'],proxyEnvironmentInherited=False,publicArtifactDownloads=1,
       provenance='OFFICIAL_PINNED_TAG_HTTPS_CONTENT_SHA256_NOT_VENDOR_SIGNATURE_OR_BINARY_EMBEDDED_ATTESTATION',
       scannerExecuted=False,productTestsExecuted=0,targetServiceConnections=0,formalUpdated=False)
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,bytes=len(raw),configSha256=sha(raw),ruleCount=len(config['rules']),selectedRules=sorted(selected))))


if __name__=='__main__':
    main()
