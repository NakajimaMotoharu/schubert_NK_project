"""Independent current-canonical contract/established route fixture join; no old PT replay."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7098-web-http-oracle-audit-v1'
REFERENCE='8b91944df5820535e23ba2469740f1c0aa94c447'
OLD='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
TRACE='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestTrace.java'
FIXTURE='src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'


def require(value,message):
    if not value:raise ValueError(message)


def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists(),'new-only public oracle audit')
    require(subprocess.check_output(['git','rev-parse','origin/main'],cwd=host.ROOT,text=True).strip()==REFERENCE,
            'current fetched design reference, no stale canonical assumption')
    designs={}
    for path in ('documents/100_RD/170_運用・保守要件/171_運用・監視要件.md',
      'documents/200_UI/250_運用・非機能/252_ログ・監視・障害復旧設計.md',
      'documents/300_SS/310_アプリケーション/313_画面template・controller・form設計.md',
      'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'):
        raw=subprocess.check_output(['git','show',REFERENCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(raw).hexdigest()==host.sha(host.ROOT/path),'local relevant design is actual canonical byte')
        designs[path]=dict(sha256=host.sha(host.ROOT/path),canonicalSource=REFERENCE)
    old=subprocess.check_output(['git','show',OLD+':'+TRACE],cwd=host.ROOT)
    require(hashlib.sha256(old).hexdigest()==host.sha(host.ROOT/TRACE),'established trace policy unmodified')
    text=old.decode()
    match=re.search(r'private static final Set<String> ROUTES\s*=\s*Set\.of\((.*?)\);',text,re.S)
    require(match is not None,'complete established source route declaration')
    declared=[json.loads(value) for value in re.findall(r'"(?:[^"\\]|\\.)*"',match[1])]
    golden=(host.ROOT/FIXTURE).read_text().splitlines()
    require(len(declared)==34 and len(set(declared))==34 and len(golden)==35 and len(set(golden))==35
            and golden==declared+['/**'],'independent literal golden exactly matches all established34 and fixed unknown')
    ss=(host.ROOT/'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md').read_text()
    require('| `nk_http_requests_total` | counter | service,route,method,status_class |' in ss
            and '| `nk_http_request_duration_seconds` | histogram | service,route |' in ss,
            'both exact canonical names/types/closed label keys, not a Production-generated expected')
    require('bucket .05/.1/.25/.5/1/1.5/2/2.5/5' in ss,'nine fixed independent HTTP boundaries')
    rd=(host.ROOT/'documents/100_RD/170_運用・保守要件/171_運用・監視要件.md').read_text()
    require('Micrometer' in rd,'mandatory actual backend remains a separate dependency, not replaced')
    value=dict(actualExit=0,invocation=invocation,canonicalDesigns=designs,
      establishedTrace=dict(path=TRACE,source=OLD,sha256=host.sha(host.ROOT/TRACE)),
      golden=dict(path=FIXTURE,sha256=host.sha(host.ROOT/FIXTURE),registered=34,totalWithUnknown=35),
      metrics=2,buckets=9,expectedFromProductionMethod=False,actualProductionMethodsInvoked=0,
      testsReplayed=0,actualVmActions=0,actualDatabaseActions=0,micrometerBackendAccepted=False,
      formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation)
    os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,routes=35,metrics=2,buckets=9,testsReplayed=0,
                         manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()
