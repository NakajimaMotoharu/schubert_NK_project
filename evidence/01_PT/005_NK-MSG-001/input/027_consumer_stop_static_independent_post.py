from pathlib import Path
import collections,datetime,hashlib,json,re,shutil,subprocess
import xml.etree.ElementTree as E
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
normalp=w/'pg21922-consumer-stop-six-main-compile-v1/manifest.safe.json';staticp=w/'pg21924-consumer-stop-six-static-reactor-v1/manifest.safe.json';style=w/'pg21926-consumer-stop-five-style-v1';bytecode=w/'pg21928-consumer-stop-five-bytecode-review-v1';m,s=load(normalp),load(staticp);raw=load(style/'raw-manifest.safe.json');j=load(bytecode/'manifest.safe.json');source='56720d75714f60d7e31da59c3da8c02baf05de52'
assert sha(normalp)=='e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f' and sha(staticp)=='75ce7bf4b849390545c0bfc407e20dae63028db3f9598303bc8bfcef2e180e91'
assert m['source']==s['source']==raw['source']==j['source']==source
assert m['actualExit']==m['terminal']['actualExit']==s['actualExit']==s['terminal']['actualExit']==j['actualExit']==0
assert not m['terminal']['timedOut'] and not s['terminal']['timedOut'] and not m['testsExecuted']
assert len(m['begin']['inputHashes'])==1036 and len(m['normalPhysicalClassHashes'])==1845
assert all('/src/test/' not in n and sha(r/n)==h for n,h in m['begin']['inputHashes'].items())
assert '-Dmaven.test.skip=true' in m['begin']['command'] and s['normalCompileManifestSha256']==sha(normalp)
assert s['jarsStillEqualCompile'] and s['sourceInputsUnchanged'] and not s['suppressionsAdded']
assert set(s['reports'])==set(m['jars']) and len(s['reports'])==6
for x in s['reports'].values():
 assert sha(Path(x['path']))==x['sha256'] and x['bugs']==x['missing']==x['errors']==0
 tree=E.parse(x['path']);assert not tree.findall('.//BugInstance') and not tree.findall('.//MissingClass') and not tree.findall('.//Error')
assert m['classIdentity']['physicalClasses']==1845 and m['classIdentity']['codeOrDebugDifferences']==4 and len(m['classIdentity']['addedPhysical'])==1
assert all(sha(Path(v['path']))==v['sha256'] for v in m['jars'].values())
reviewp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG20154-current-d8-context-requalification-v1/review.json';review=load(reviewp);assert sha(reviewp)=='febfa0189b50c4263ee55ecab82e6d3edf3eadd4cd2a9e5a33a2f3b3a7d6bcd2'
candidates=load(style/'prior-anchor-candidates.safe.json');assert not candidates['unmatched'] and candidates['priorReviewSha256']==sha(reviewp);byid={x['id']:x for x in review['classified']};judgments=[]
for row in candidates['rows']:
 matches=[byid[i] for i in row['priorMatches']];assert matches and all(x['classification']=='CONTEXTUAL_NONAPPLICABLE' and x['actualViolation'] is False for x in matches)
 # All reported lines remain exact equal anchors. Existing lifecycle/catch/resource/identity policy is preserved.
 judgments.append(dict(row,classification='CONTEXTUAL_NONAPPLICABLE',actualViolation=False,reasons=sorted(set(x['reason'] for x in matches)),deltaReview='Only flag-notification ordering and common owned-group type change; reported cleanup/catch/identity/resource statements remain unchanged. No new PMD finding on stopDelivery/interface/fanout.'))
assert len(judgments)==101 and raw['stages']['pmd']['actualExit']==4 and raw['stages']['checkstyle']['actualExit']==0
assert not any(x.tag.rsplit('}',1)[-1] in ['error','processingerror','configerror'] for x in E.parse(style/'pmd.xml').getroot().iter())
assert not E.parse(style/'checkstyle.xml').findall('.//error')
text=(bytecode/'javap.stdout').read_text();assert sha(bytecode/'javap.stdout')==j['stage']['stdoutSha256']
classheads=list(re.finditer(r'(?m)^(?:public final class|interface) (dev\.codex\.[\w.]+).*\{$',text));assert len(classheads)==5
parts={x.group(1).rsplit('.',1)[-1]:text[x.end():classheads[i+1].start() if i+1<len(classheads) else len(text)] for i,x in enumerate(classheads)}
def method(part,name):
 a=part.index('  public void '+name+'();');match=re.search(r'\n  (?:public|private|static|protected)',part[a+1:]);return part[a:a+1+match.start()] if match else part[a:]
parent=method(parts['ApiMessagingRuntime'],'close');stop=parent.index('InboundConsumerGroup.stopDelivery:()V');close=parent.index('Method closeGroups:');assert stop<close and parent.index('goto          27')<close and 'List.size:()I' in parent and 'List.get:(I)' in parent and 'new ' not in parent[:close]
for name in ['SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers']:
 body=method(parts[name],'stopDelivery');ops=re.findall(r'^\s+\d+: (\w+)',body,re.M);assert ops==['aload_0','getfield','iconst_1','invokevirtual','return'] and 'Field halted:' in body and 'AtomicBoolean.set:(Z)V' in body
 body=method(parts[name],'close');assert 'Method stopDelivery:()V' in body and body.index('Method stopDelivery:()V')<body.index('monitorenter')
interface=parts['InboundConsumerGroup'];assert 'abstract void stopDelivery();' in interface and 'abstract void close();' in interface and 'Code:' not in interface
init=set(re.findall(r"Initializing '([^']+)",(bytecode/'class-init.stdout').read_text()));assert not any(n.startswith('dev/codex/schubert/') for n in init)
out=r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21930-consumer-stop-static-independent-post-v1';assert not out.exists();out.mkdir();files={}
for prefix,folder in [('normal-',normalp.parent),('six-static-',staticp.parent),('style-',style),('bytecode-',bytecode)]:
 for p in sorted(folder.iterdir()):
  if p.is_file() and p.suffix in ['.json','.stdout','.stderr','.xml','.txt']:
   dest=out/(prefix+p.name);shutil.copyfile(p,dest);files[dest.name]=sha(dest)
for role,x in s['reports'].items():
 p=out/('spotbugs-'+role+'.xml');shutil.copyfile(x['path'],p);files[p.name]=sha(p)
write(out/'style-applicability.json',dict(rawFindings=101,priorReview=dict(path=str(reviewp.relative_to(r)),sha256=sha(reviewp)),judgments=judgments,rawPmdExit=4,applicableViolations=0,suppressionsAdded=False,globalF03=False));files['style-applicability.json']=sha(out/'style-applicability.json')
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain=source,normalManifestSha256=sha(normalp),sixStaticManifestSha256=sha(staticp),mainInputs=1036,normalPhysicalClasses=1845,unchangedPhysicalClasses=1840,changedPhysicalClasses=m['classIdentity']['changedPhysical'],addedPhysicalClasses=m['classIdentity']['addedPhysical'],sixStaticIssues=0,rawPmdFindings=101,rawPmdExit=4,applicablePmdViolations=0,checkstyleIssues=0,changedMainSources=m['begin']['changes'],compiledParentStopBeforeFirstClose=True,compiledThreeFlagOnlyStops=True,compiledIndividualCloseStopsFirst=True,newInterfaceNoCodeMetadata=True,productInitializationByJavap=0,newProductTests=0,productTestsExecuted=0,newMethods=0,newSourceProofs=0,newAcceptance=0,coverage=None,bugsRemainOpen=['BUG-2407','YKT-2152'],dynamicRegression='PT-JMS-STOP-GROUP001..006 NOT_RUN/HOLD',oldSuccessfulRunsTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortRate=None,files=files)
write(out/'manifest.json',value);print(json.dumps(dict(actualExit=0,physicalClasses=1845,sixStaticIssues=0,rawPmdFindings=101,applicableViolations=0,bytecodeTargets=5,productTestsExecuted=0,manifestSha256=sha(out/'manifest.json'))))
