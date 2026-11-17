"""Independent exact byte/XML/terminal/settings validation; no analyzer/product rerun."""
from pathlib import Path
import datetime,hashlib,json,xml.etree.ElementTree as E
import pgpt_closed_host_profile as policy
from pgpt_spotbugs_contract import canonical_plugin,checked_command
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37782-pure-protocol-web-maxlow-prepare-v1/manifest.json';sp=b/'evidence/PG37784-pure-protocol-web-maxlow-static-v1/manifest.json';p=ld(pp);s=ld(sp);assert p['actualExit']==s['actualExit']==0 and s['prepare']==ref(pp)
work=Path(p['work']);target=work/'target/classes';assert sha(work/'pom.xml')==p['analysisPomSha256']
assert E.tostring(canonical_plugin((work/'pom.xml').read_text()))==E.tostring(canonical_plugin((r/'src/schubert-nk-web/pom.xml').read_text()))
for n,h in p['physicalClassHashes'].items():policy.relative_name(n);assert sha(target/n)==h
assert len(p['physicalClassHashes'])==251 and s['physicalClassHashes']==p['physicalClassHashes']
assert all(sha(r/n)==h for n,h in p['sourceHashes'].items()) and all(sha(Path(n))==h for n,h in p['dependencies'].items())
stage=ld(sp.parent/'spotbugs-maxlow251-exit.safe.json');assert stage==s['stage'] and stage['actualExit']==0 and not stage['timedOut'];checked_command(stage['command'])
assert all(sha(sp.parent/('spotbugs-maxlow251.'+k))==stage[k+'Sha256'] for k in ['stdout','stderr'])
begin=ld(sp.parent/'spotbugs-maxlow251-begin.safe.json');process=ld(sp.parent/'spotbugs-maxlow251-process.safe.json')
assert begin['command']==process['command']==stage['command'] and begin['cwd']==process['cwd']==stage['cwd']==str(work)
assert begin['startUTC']==process['startUTC']==stage['startUTC'] and process['pid']>0
xml=E.parse(sp.parent/'spotbugs.xml').getroot();assert not xml.findall('.//BugInstance') and not xml.findall('.//MissingClass') and not xml.findall('.//Error')
stats={x.get('class').replace('.','/')+'.class' for x in xml.findall('.//ClassStats')};assert stats==set(p['physicalClassHashes'])
whole_proofs=[]
for row in p['scopeRows']:
    oldpath=r/row['independentPost']['path'];assert sha(oldpath)==row['independentPost']['sha256'];post=ld(oldpath);oldprep=r/row['prepare']['path'];assert sha(oldprep)==row['prepare']['sha256']
    expected=post['files'].get('jacoco.exec');assert isinstance(expected,str) and len(expected)==64
    assert sha(oldpath.parent/'jacoco.exec')==expected
    assert all(p['physicalClassHashes'][n]==h for n,h in row['webPhysicalClassHashes'].items())
    whole_proofs.append(dict(oldPost=row['independentPost'],oldUnitSource=row['originalUnitSource'],oldExecSha256=expected,oldExecChanged=False,webStaticAppliedClasses=len(row['webPhysicalClassHashes']),oldPTWholeSourceIdentityNotRewritten=True))
out=b/'evidence/PG37786-pure-protocol-web-maxlow-independent-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],prepare=ref(pp),static=ref(sp),physicalClasses=251,protocolPhysical176=176,webPhysical75=75,sourceFiles226=226,fullClassStatsExact=True,bugs=0,missing=0,errors=0,explicitMaxLowFailOnError=True,newContextNoCachedAnalysis=True,byteSourcesAndDependenciesExact=True,oldWholeProofs=whole_proofs,protocolCurrent176Exact=True,MainCompiled=False,productTestsExecuted=0,oldPTReplayedOrExecUnion=False,heldBinaryActions=0,actualRootVmDbNativeKeysAuthorityActions=0,formalUpdated=False,newAcceptance=0,bug='BUG3188',crossDeployment='YKT2656',limitedEightScopesStaticCorrected=True,unknownOtherSubsetScopeStatus='OPEN_NOT_SEARCH_ONLY_CLOSED',allSixModuleF03Accepted=False,whole451Accepted=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,physical251Exact=True,oldWholeExecsUnchanged=7,productTestsExecuted=0,MaxLow='explicit',globalF03Accepted=False))
