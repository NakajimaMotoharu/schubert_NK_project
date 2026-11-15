"""Permitted SOURCE-only review. Never imports/compiles/loads/executes SDK or production classes."""
from pathlib import Path
import json,re,hashlib,datetime,subprocess,xml.etree.ElementTree as ET
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33710-pgcopy-source-pt-unrun-review-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));main=r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/PostgresMigrationCopyPort.java';test=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/PostgresMigrationCopyPortTest.java';s=main.read_text();t=test.read_text();oracle=load(e/'corrected-independent-six-copy-command-vectors.json');wire=load(e/'independent-future-pt-row-wire-vectors.json');quoted=r'"(?:[^"\\]|\\.)*"'
def declaration(text,name,call):
 match=re.search(r'\b'+name+r'\s*=\s*'+re.escape(call)+r'\(([\s\S]*?)\);',text);assert match,name;return [json.loads(x) for x in re.findall(quoted,match.group(1))]
a=declaration(s,'COLUMNS','Map.of');assert len(a)==12;columns=dict(zip(a[::2],a[1::2]));assert len(columns)==6
opts=json.loads(re.search(r'\bOPTIONS\s*=\s*('+quoted+r');',s).group(1));actual={k:'COPY '+k+' ('+v+')'+opts for k,v in columns.items()};assert actual==oracle['commands'];assert [len(x.split(',')) for x in columns.values()]==[7,11,12,12,17,6]
# Independent PG E-string subset semantic decoder: only the documented needed escapes.
def decode_e(payload):
 result=[];index=0
 while index<len(payload):
  value=payload[index]
  if value!='\\':result.append(value);index+=1;continue
  assert index+1<len(payload);nextchar=payload[index+1];assert nextchar in ['\\','t'];result.append('\\' if nextchar=='\\' else '\t');index+=2
 return ''.join(result).encode('ascii').hex()
def semantic(command):return {label:decode_e(re.search(label+" E'([^']*)'",command).group(1)) for label in ['DELIMITER','NULL']}
semantic_expected={'DELIMITER':'09','NULL':'5c4e'};assert all(semantic(x)==semantic_expected for x in actual.values())
old=load(e/'original-six-copy-command-vectors-before-escape-fix.json');old_semantics={k:semantic(v) for k,v in old['commands'].items()};assert old['commands']==oracle['commands'] and all(x==semantic_expected for x in old_semantics.values())
# Explicit synthetic negative; never alter the valid original expectation to fit an assumed bug.
synthetic_bad={}
for k,command in actual.items():
 delimiter=re.search("DELIMITER E'([^']*)'",command).group(1);nullmark=re.search("NULL E'([^']*)'",command).group(1)
 bad=command.replace("DELIMITER E'"+delimiter+"'","DELIMITER E'"+delimiter.replace(chr(92),chr(92)*2)+"'").replace("NULL E'"+nullmark+"'","NULL E'"+nullmark.replace(chr(92),chr(92)*2)+"'")
 synthetic_bad[k]=semantic(bad)
assert all(x=={'DELIMITER':'5c74','NULL':'5c5c4e'} and x!=semantic_expected for x in synthetic_bad.values())
assert declaration(t,'TABLES','List.of')==list(oracle['commands']);assert declaration(t,'SQL','List.of')==list(oracle['commands'].values());expected_wires=declaration(t,'WIRE','List.of');assert [x.encode('utf-8').hex() for x in expected_wires]==wire['wireUtf8Hex']
# Source literal semantics in future Test023 independently checked too (no future Test execution).
options_literals=[json.loads(x) for x in re.findall(quoted,t) if json.loads(x).startswith(' FROM STDIN')];assert options_literals==[opts]
assert len(re.findall(r'@Test\s+void\s+pgcopy\d{3}',t))==24 and '@Disabled' not in t
assert s.index('COLUMNS.get(stagingTable)')<s.index('target.getAutoCommit()')<s.index('target.unwrap(PGConnection.class)')<s.index('manager.copyIn(')
assert s.index('var fields = new ArrayList<@Nullable String>(row);')<s.index('if (fields.size() != width)')<s.index('Collections.unmodifiableList(fields)')
assert 'row.size() != width' not in s and s.count('copy.endCopy()')==s.count('copy.cancelCopy()')==1
assert all(x not in s for x in ['.commit(','.rollback(','.close(','.setAutoCommit(','.setReadOnly(','.flushCopy(','.getConnection(','ProcessBuilder','java.nio.file','Class.forName','catch (NullPointerException'])
assert 'if (count != snapshot.size() || copy.isActive()) throw unavailable();' in s and 'cancelOwned(copy, primary);\n      throw primary;' in s
assert 'if (cleanup != primary) primary.addSuppressed(cleanup);' in s and 'if (copy.isActive()) throw unavailable();' in s
assert '@Nullable CopyManager manager;' in t and 'final CopyManager manager;' not in t and 'CaptureChangingRow' in t and 'changed.portCalls' in t
# Only existing driver scope changes, not version or other dependency bytes.
pom=r/'src/schubert-nk-bootstrap/pom.xml';before=(e/'original-bootstrap-pom.xml.txt').read_text();line='    <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><version>42.7.13</version><scope>runtime</scope></dependency>';assert before.count(line)==1 and before.replace(line,line.replace('<scope>runtime</scope>',''))==pom.read_text();ET.parse(pom)
cs=load(e/'source-only-checkstyle-exit.json');assert cs['actualExit']==0 and all(sha(r/path)==h for path,h in cs['inputHashes'].items());findings=ET.parse(e/'source-only-checkstyle.xml').findall('.//error');assert len(findings)==0
oldpost=load(b/'evidence/PG33682-copyverify1050-post-v1/manifest.json');pf=load(b/'input/3388_copyverify1050_profile.json');unchanged={}
for path in pf['mainSources']+[x['path'] for x in pf['testSources']]:assert sha(r/path)==oldpost['inputHashes'][path];unchanged[path]=oldpost['inputHashes'][path]
assert len(unchanged)==105 and oldpost['inputHashes']['src/schubert-nk-bootstrap/pom.xml']!=sha(pom)
policies=['tools/quality/pgpt_closed_host_profile.py','tools/quality/pgpt_closed_host_post.py'];policy_pins={}
for path in policies:
 h=hashlib.sha256(subprocess.check_output(['git','show','7b2f17f40bfff283913a30a6fe4ab8329d9d8031:'+path])).hexdigest();assert sha(r/path)==h;policy_pins[path]=h
review=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),kind='SOURCE_ONLY_STRONG_REVIEW_NOT_PT_OR_SEMANTIC_COMPILATION',main=ref(main),test=ref(test),pom=ref(pom),sourceOracle=ref(e/'corrected-independent-six-copy-command-vectors.json'),wireOracle=ref(e/'independent-future-pt-row-wire-vectors.json'),references=oracle['references'],driverVersion42_7_13Unchanged=True,sourceDependencyRuntimeRetainedDefaultCompile=True,wholeBuildOrDependencyResolutionAttempted=False,sixSqlSourceLiteralAndSemanticChecks=True,semanticExpected=semantic_expected,originalOracleSemantic=old_semantics,originalOracleProvedCorrect=True,bug3001WithdrawnFalsePositive=True,syntheticOverEscapeNegative=synthetic_bad,syntheticInvalidVectorsRejected=True,futureTestExpectedSqlAndWireLiteralsChecked=True,plannedTestDefinitions=24,actualTestExecution=0,all24Status='NOT_RUN_HOLD',sourceCheckstyleFindings=0,sourceOnlyCheckstyle=ref(e/'source-only-checkstyle-exit.json'),nullabilityStatic='NOT_RUN_HOLD',semanticPmd='NOT_RUN_HOLD',spotbugs='NOT_RUN_HOLD',sdkAbiCompilation='NOT_RUN_HOLD',runtimeAndDbAndDriver='NOT_RUN_HOLD',lineMethodClassBranchCoverage=None,unfilteredCodeCoverage=None,expectedOwnedWidthAfterCapture=True,firstPrimaryAndCancelSelfIdentitySourceChecked=True,callerOwnsConnectionTransactionAndAuthentication=True,oldQualified105JavaBytesUnchanged=unchanged,old1050BeforePomChangeOnly=True,newSourceNotPromotedIntoOldRun=True,guardSourceHashesUnchanged=policy_pins,sdkJarOrClassReadCompileDefineInitOrExecution=0,applicationDbVmRootNativeKeyBackupOriginalDataOperations=0,noStubSdkOrAlternativeExecution=True,newAcceptance=0,whole451Accepted=False,formalUpdated=False,effortRate=None)
(e/'source-only-review.json').open('x').write(json.dumps(review,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,sourceOnly=True,sqlSemantic6=True,originalValidAndSyntheticBadVerified=True,checkstyle=0,oldJava105Unchanged=True,plannedPt=24,executedPt=0,coverage=None,sdkActions=0))
