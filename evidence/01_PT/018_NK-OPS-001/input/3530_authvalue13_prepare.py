"""Reuse exact qualified Main and whole11 Test bytes; compile only new meaningful Value2."""
from pathlib import Path
import hashlib,json,re,shutil,xml.etree.ElementTree as ET
import pg9666_pagination_static as capture
import pgpt_closed_host_profile as policy
from pmo_forecast_bridge import reconcile_current_bridge
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';runs=r.parent/'pgpt-runs/PG379';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33824-ssc422-auth11-prepare-v1/manifest.json';qp=b/'evidence/PG33828-ssc422-auth11-preflight-v1/manifest.json';postp=b/'evidence/PG33832-ssc422-auth11-independent-v1/manifest.json';old=ld(pp);quality=ld(qp);post=ld(postp);origin=runs/'pg33824-ssc422-auth11-v1';work=runs/'pg33844-authvalue13-prepare-v1';out=b/'evidence/PG33844-authvalue13-prepare-v1';assert not work.exists() and not out.exists()
assert old['actualExit']==quality['actualExit']==post['actualExit']==0 and old['expectedTests']==11 and quality['staticApplicable']==quality['unclassified']==0
assert all(sha(r/n)==h for n,h in old['inputHashes'].items())
for n in list(old['physicalClassHashes'])+list(old['testClassHashes']):policy.relative_name(n)
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:assert {n:sha(origin/folder/n) for n in old[key]}==old[key]
assert len(old['physicalClassHashes'])==183 and all(sha(Path(n))==h for n,h in old['dependencies'].items())
new='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthContextValueContractTest.java';text=(r/new).read_text();assert all(marker not in text for marker in ['Class.forName','java.lang.reflect','setAccessible','ProcessBuilder','DataSource','@TempDir','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
methods=re.findall(r'@Test\s*void (\w+)\s*\(',text);assert len(methods)==2;expected=old['expectedCases']+[dict(classname='dev.codex.schubert.nk.api.security.AuthContextValueContractTest',name=n+'()') for n in methods];assert len(expected)==13
startpath=next((r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106').glob('2140*'));start=ld(startpath);assert reconcile_current_bridge(start)==start['currentFullForecastBudgetBridge']
legacy=next((r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106').glob('2137*'));prior=ld(legacy);corrected=reconcile_current_bridge(prior);assert corrected['currentRevisedRemainingPp']==dict(low=397.324,base=837.386,high=1643.415) and prior['currentFullForecastBudgetBridge']['currentRevisedRemainingPp']==dict(low=398.324,base=840.386,high=1651.415)
work.mkdir();out.mkdir();(work/'component').mkdir();(work/'test-classes').mkdir()
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name,h in old[key].items():
  dest=work/folder/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin/folder/name,dest);assert sha(dest)==h
capture.SLOT=out;jdk=tc/'jdk-25.0.4/bin';gates=tc/'static-gates-20261015';cp=':'.join([str(work/'component'),*old['dependencies']]);stages={}
stages['value-test-compile']=capture.step('value-test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',cp,'-d',str(work/'test-classes'),str(r/new)],r);assert stages['value-test-compile']['actualExit']==0 and not stages['value-test-compile']['timedOut']
listing=out/'new-sources.txt';listing.write_text(str(r/new)+'\n');stages['format']=capture.step('format',[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--dry-run','--set-exit-if-changed','--skip-reflowing-long-strings',str(r/new)],r);stages['checkstyle']=capture.step('checkstyle',[str(jdk/'java'),'-jar',str(gates/'checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],r)
pmd=[gates/'record-fix-v1/pmd-record-1298.jar',*sorted((gates/'pmd-bin-7.28.0/lib').glob('*.jar'))];stages['pmd']=capture.step('pmd',[str(jdk/'java'),'-cp',':'.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--use-version','java-25','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+cp,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')],r)
assert stages['format']['actualExit']==stages['checkstyle']['actualExit']==0 and stages['pmd']['actualExit'] in [0,4] and all(not v['timedOut'] for v in stages.values())
parsed=ET.parse(out/'pmd.xml').getroot();errors=[dict(n.attrib) for n in parsed.iter() if n.tag.rpartition('}')[2] in ['error','configerror']];findings=[dict(path=n.get('name'),rule=v.get('rule'),line=v.get('beginline'),message=(v.text or '').strip()) for n in parsed if n.tag.rpartition('}')[2]=='file' for v in n if v.tag.rpartition('}')[2]=='violation'];assert errors==[] and not ET.parse(out/'checkstyle.xml').findall('.//error')
testhash={}
for path in (work/'test-classes').rglob('*.class'):
 name=str(path.relative_to(work/'test-classes'));policy.relative_name(name);testhash[name]=sha(path)
assert all(testhash[n]==h for n,h in old['testClassHashes'].items());inputs=dict(old['inputHashes']);inputs[new]=sha(r/new)
v=dict(actualExit=0,inputHashes=inputs,dependencies=old['dependencies'],apiMainSources=old['apiMainSources'],apiTestSources=old['apiTestSources']+[new],physicalClassHashes=old['physicalClassHashes'],mainClassHashes=old['mainClassHashes'],testClassHashes=testhash,expectedCases=expected,expectedTests=13,newDefinitions=2,necessaryPriorDefinitions=11,stages=stages,rawFindings=findings,processingErrors=errors,checkstyleFindings=0,exactMainCompile=ref(pp),exactMainStatic=ref(qp),exactPriorWhole11Post=ref(postp),rootCompileAndSpotBugsReusedOnlyExactUnchanged5Main=True,MainCompilationRepeated=False,old11TestCompilationRepeated=False,onlyNewValueTestCompiled=True,startForecastBridgeVerifiedByHelper=ref(startpath),historicalBridgeCorrectedWithoutHistoryRewrite=ref(legacy),tool8=ref(b/'evidence/PG33840-forecast-bridge-tool8-v1/manifest.json'),applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedTests=13,newDefinitions=2,mainRebuilds=0,old11Recompiles=0,newStaticRaw=findings)))
