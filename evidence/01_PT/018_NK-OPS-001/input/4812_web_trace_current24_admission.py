"""Current same-source whole24, exact per-site original anchors and explicit Max/Low settings."""
from pathlib import Path
import datetime,hashlib,json,zipfile,xml.etree.ElementTree as E
import pgpt_closed_host_stages as policy
from pgpt_spotbugs_contract import canonical_plugin,checked_command
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379/pg37758-web-trace-current24-v1'
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37758-web-trace-current24-prepare-v1/manifest.json';sp=b/'evidence/PG37760-web-trace-current24-static-v1/manifest.json';p=ld(pp);s=ld(sp)
assert p['actualExit']==s['actualExit']==0 and p['expectedTests']==24 and len(p['mainClassHashes'])==23 and len(p['physicalClassHashes'])==199
assert p['inputHashes']==s['inputHashes'] and all(sha(r/n)==h for n,h in p['inputHashes'].items())
assert all(v['actualExit']==0 and not v['timedOut'] for v in p['stages'].values())
assert all(v['actualExit']==(4 if n=='pmd' else 0) and not v['timedOut'] for n,v in s['stages'].items())
assert s['spotbugsSettingsExplicitMaxLow'] and s['spotbugsFailOnError'] and s['originalWebPluginConfigExact'];checked_command(s['stages']['spotbugs']['command'])
assert E.tostring(canonical_plugin((w/'pom.xml').read_text()))==E.tostring(canonical_plugin((r/'src/schubert-nk-web/pom.xml').read_text()))
assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
assert {n.replace('.','/')+'.class' for n in s['spotbugs']['classStats']}==set(p['mainClassHashes'])
assert all(sha(w/'component'/n)==h for n,h in p['physicalClassHashes'].items())
assert all(sha(w/'test-classes'/n)==h for n,h in p['testClassHashes'].items())
old=ld(b/'evidence/PG27632-caddy-context24-independent-v1/manifest.json');paths=p['apiMainSources']+p['apiTestSources'];anchors=[];refs=[]
for name in ('PG27608-trace-menu24-preflight-v1','PG27628-caddy-context24-preflight-v1'):
    file=b/'evidence'/name/'manifest.json';prior=ld(file);assert prior['actualExit']==0;refs.append(ref(file))
    for row in prior['classified']:
        path=str(Path(row['path']).relative_to(r))
        if path not in paths:continue
        assert sha(r/path)==old['inputHashes'][path]
        line=int(row['line']);text=(r/path).read_text().splitlines()[line-1].strip()
        anchors.append(dict(path=path,rule=row['rule'],sourceAnchor=text,sourceLine=line,occurrences=1,message=row['message'],reason=row['reason'],disposition='NOT_APPLICABLE'))
classified=policy.classify_source_findings(paths,anchors,s['rawFindings'],lambda n:(r/n).read_text());assert len(classified)==len(s['rawFindings'])==25
providers={}
for n,h in p['dependencies'].items():
    assert sha(Path(n))==h
    with zipfile.ZipFile(n) as archive:providers[n]='META-INF/services/java.sql.Driver' in archive.namelist()
assert not any(providers.values())
counts={n:sum(x['classname']==n.split('/src/test/java/')[1][:-5].replace('/','.') for x in p['expectedCases']) for n in p['apiTestSources']};assert sorted(counts.values())==[1,3,5,5,10]
targets=[name.replace('.','/') for name in ['dev.codex.schubert.nk.web.logging.WebRequestTrace','dev.codex.schubert.nk.web.logging.WebRequestTrace$Scope','dev.codex.schubert.nk.web.logging.WebRequestRouteInterceptor','dev.codex.schubert.nk.web.config.RequestLogMvcConfiguration','dev.codex.schubert.nk.web.security.WebRequestContext','dev.codex.schubert.nk.web.security.CaddyTransportContextFilter','dev.codex.schubert.nk.web.security.CaddyClientAddressResolver']]
assert all(n+'.class' in p['mainClassHashes'] for n in targets)
out=b/'evidence/PG37766-web-trace-current24-admission-v1';assert not out.exists();out.mkdir()
normal=dict(actualExit=0,sourceCore='a013a6d676454082de3c59bc199e87f37fefe159',work=str(w),mainInputHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' not in n},testSourceHashes={n:h for n,h in p['inputHashes'].items() if '/src/test/java/' in n},physicalClassHashes=p['physicalClassHashes'],testPhysicalHashes=p['testClassHashes'],toolDependencyHashes=p['dependencies'],classpath=':'.join([str(w/'component'),*p['dependencies']]),wholeTestSourceCounts=counts,expectedTests=24,originalPrepare=ref(pp),static=ref(sp),expectedCases=p['expectedCases'])
np=out/'normalized-prepare.json';np.write_text(json.dumps(normal,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepare=ref(np),originalPrepare=ref(pp),static=ref(sp),applicable=0,unclassified=0,processingErrors=0,classified=classified,priorPerSiteReasons=refs,sourceExactAll5OriginalFixtures=True,all199PhysicalNamesVerified=True,spotbugsSettingsExplicitMaxLow=True,originalWebPluginExact=True,declaredTargets=targets,classpathSqlDriverDescriptors=providers,sources24WholeCases=counts,actualRootVmDbNativeKeysAuthorityActions=0,newTestsExecuted=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,Main20Static23All0=True,classified=25,expectedTests=24,targets=7,physical=199))
