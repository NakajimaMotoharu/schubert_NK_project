"""Fixed public-code/authoritative-design ownership facts only, no Java loading/runtime access."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify

SOURCE='3613b2742c8bcda85a2ec889d023307fadf1875c'
DESIGN='8b91944df5820535e23ba2469740f1c0aa94c447'
ROLES={'api':'Api','web':'Web'}

if __name__=='__main__':
    invocation=capture(Path(__file__))
    out=host.BASE/'PG8734-management-metric-owner-audit-v1'
    assert not out.exists()
    assert subprocess.check_output(['git','rev-parse','origin/main'],cwd=host.ROOT,text=True).strip()==DESIGN
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    paths=[]
    callers={'api':'ApiProcessMain','web':'WebNativeRuntime'}
    for role,title in ROLES.items():
        paths.extend([f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{title}ManagementServer.java',f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{callers[role]}.java',f'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{title}NonSecretConfig.java',f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}CustomMetricPayload.java',f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/monitoring/{title}StandardMetricSource.java'])
    paths.append('src/deployment/config/common.yml.template')
    rows={}
    bodies={}
    tokens=('nk.monitoring.mode','ManagementServer.bind','ownedRelease','ManagementServer::close','management.start','control.start','value.closeWithin','private volatile','this::healthy','private final WebNonSecretConfig')
    for path in paths:
        data=(host.ROOT/path).read_bytes()
        original=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=host.ROOT)
        assert data==original
        body=data.decode();bodies[path]=body
        excerpts=[dict(line=i,text=line.strip()) for i,line in enumerate(body.splitlines(),1) if any(token in line for token in tokens)]
        assert len(excerpts)<=40
        rows[path]=dict(sha256=hashlib.sha256(data).hexdigest(),excerpts=excerpts)
    designs={}
    for path in ('documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md','documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md','documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'):
        data=subprocess.check_output(['git','show',DESIGN+':'+path],cwd=host.ROOT)
        lines=[dict(line=i,text=line) for i,line in enumerate(data.decode().splitlines(),1) if any(token in line for token in ('ResourceScope','ready gauge','Exposed actuator','DEBUG','STANDARD','初期の外部通知先','SQL本文なし','Username、IP'))]
        assert len(lines)<=35
        designs[path]=dict(sha256=hashlib.sha256(data).hexdigest(),excerpts=lines)
    findings={}
    for role,title in ROLES.items():
        server=f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{title}ManagementServer.java'
        caller=f'src/schubert-nk-{role}/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{callers[role]}.java'
        parser=f'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/{role}/bootstrap/{title}NonSecretConfig.java'
        assert 'schubert_nk_'+role+'_ready' in bodies[server] and '"/actuator/prometheus"' in bodies[server]
        assert '"nk.monitoring.mode", "STANDARD"' in bodies[parser] and '!Set.of("STANDARD", "DEBUG").contains(values.get("nk.monitoring.mode"))' in bodies[parser]
        assert bodies[caller].count('nk.monitoring.mode')==0
        assert all(title+token not in bodies[server]+bodies[caller] for token in ('CustomMetricPayload','StandardMetricSource'))
        findings[role]=dict(nonSecretModeAlreadyStrictlyParsed=True,modeReferencesInExactCaller=0,managementCurrentlyLegacyReadyOnly=True,fullPayloadConsumedInExactManagerOrCaller=False,caller=caller,server=server,configParser=parser)
    assert '"nk.monitoring.mode": "STANDARD"' in bodies['src/deployment/config/common.yml.template']
    verify(invocation)
    out.mkdir()
    host.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,designMain=DESIGN,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,sourceFiles=rows,designFiles=designs,findings=findings,nextPermittedPg='ROLE_LOCAL_CALLER_HELD_METRIC_CONTEXT: RESOURCE_FREE_CONSTRUCTOR_THEN_EXPLICIT_INITIALIZE; FIXED_CUSTOM_REGISTRY_AND_STANDARD_OWNER; STRONGLY_RETAIN_NONRESOURCE_BINDINGS; PURE_RENDER_BORROWS_TO_FULL_OVERLOAD; REVERSE_CLOSE_WITH_PARTIAL_OWNERSHIP',laterUnaccepted=['native caller inserts context before management and closes after confirmed management stop','management handler and mode/source supply','full custom observation and producer hooks without Ops credential leakage','actual endpoint/native/CHR/whole451'],sourceEdits=0,productionTestsExecuted=0,newProductionClasses=0,newAccepted=0,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,productClassInitialized=False))
    print(json.dumps(dict(actualExit=0,sourceFiles=len(rows),designFiles=len(designs),newTests=0,newAccepted=0,manifestSha256=host.sha(out/'manifest.json'))))
