import collections,hashlib,json,re
from pathlib import Path
root=Path.cwd(); live=root.parent/'PMO/pgpt-completion-stage-20261102'
data=json.loads((live/'ordinary-reuse-matrix.json').read_bytes())
groups=collections.defaultdict(list)
for row in data['rows']:
 if row['decision'].startswith('CURRENT_'):groups[row['id'].split('#')[0]].append(row)
flags={'DB_REFERENCE':r'TestDatabase|DataSource|DriverManager|prepareStatement|createStatement','PROCESS_REFERENCE':r'ProcessBuilder|ProcessHandle|Runtime.getRuntime|Systemctl|NativeIo','FILESYSTEM_REFERENCE':r'Files\.|@TempDir','NETWORK_OR_JMS_REFERENCE':r'new Socket|HttpClient|createConnection|createContext|JMSContext','CRYPTO_REFERENCE':r'FingerprintKeyRing|Cipher|KeyStore|SecretKey','HELD_PORT_REFERENCE':r'TemporaryInfrastructureException|WebStartupException|RootStartupContext|SourceStartupAdmissionNativeGate','ASYNC_REFERENCE':r'Executor|new Thread|CompletableFuture','ENVIRONMENT_REFERENCE':r'System\.getenv|System\.getProperty'}
for pattern in list(flags.values())+[r'@(BeforeAll|BeforeEach|AfterAll|AfterEach|TempDir)\b',r'\bPT-[A-Z0-9][A-Z0-9_-]{2,80}',r'\bassert[A-Z]\w*\s*\(',r'\bassert(?:Equals|ArrayEquals)\(\s*(?:[0-9]|true\b|false\b|null\b|")']:
 re.compile(pattern)
assert re.search(r'\bassert[A-Z]\w*\s*\(', 'assertEquals(1,x)') and not re.search(r'\bassert[A-Z]\w*\s*\(', 'not_an_assert')
assert re.search(r'@(BeforeAll|BeforeEach|AfterAll|AfterEach|TempDir)\b','@BeforeAll') and re.search(flags['FILESYSTEM_REFERENCE'],'Files.read')

records=[]; read_count=0
for name,rows in sorted(groups.items()):
 p=rows[0]['path'];assert all(r['path']==p and r['sha256']==rows[0]['sha256'] for r in rows)
 if 'RootFailed' in p or p in {'tools/quality/architecture/SnapshotKeyCloseWitness.java','tools/quality/pg9892_snapshot_key_close_witness.py'}:
  records.append({'className':name,'declarations':len(rows),'status':'HELD_NAME_EXCLUDED_BEFORE_STAT_HASH_READ','sourceRead':False});continue
 raw=(root/p).read_bytes();assert hashlib.sha256(raw).hexdigest()==rows[0]['sha256'];read_count+=1
 text=raw.decode();lines=text.splitlines()
 life=[i+1 for i,l in enumerate(lines) if re.search(r'@(BeforeAll|BeforeEach|AfterAll|AfterEach|TempDir)\b',l)]
 marked=[key for key,pat in flags.items() if re.search(pat,text)]
 ids=sorted(set(re.findall(r'\bPT-[A-Z0-9][A-Z0-9_-]{2,80}',text)))
 assertions=[i+1 for i,l in enumerate(lines) if re.search(r'\bassert[A-Z]\w*\s*\(',l)]
 literal=[i+1 for i,l in enumerate(lines) if re.search(r'\bassert(?:Equals|ArrayEquals)\(\s*(?:[0-9]|true\b|false\b|null\b|\")',l)]
 records.append({'className':name,'declarations':len(rows),'status':'STATIC_INDICATORS_ONLY_NOT_EXECUTION_OR_SEMANTIC_PASS','sourceRead':True,'sha256':rows[0]['sha256'],'flags':marked,'lifecycleLines':life,'assertionCalls':len(assertions),'literalFirstExpectedAssertionCount':len(literal),'testIdComments':ids})
cases=json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18454-current3008-latest270-owner-correction-v1/manifest.json').read_bytes())['cases']
byname=collections.defaultdict(list)
for c in cases:byname[c['name']].append(c['classname'])
aliases=[{'declaration':r['id'],'sameNameExistingClasses':byname[r['id'].split('#')[1]],'decision':'NOT_REUSED_NO_INHERITANCE_FIXTURE_OR_ORACLE_PROOF'} for rs in groups.values() for r in rs if r['id'].split('#')[1] in byname]
summary={'missingDeclarations':sum(r['declarations'] for r in records),'classes':len(records),'currentSourceFilesReadAndHashVerified':read_count,'heldNameExcludedClasses':sum(not r['sourceRead'] for r in records),'indicatorsByClass':dict(collections.Counter(f for r in records for f in r.get('flags',[]))),'sameNameAliasCandidatesNotMerged':len(aliases),'semanticProofsNewlyAccepted':0,'productExecutions':0,'newRequiredExecutionCount':None}
print(json.dumps({'summary':summary,'rows':records,'sameNameCandidates':aliases,'method':'READ_ONLY_CURRENT_TEST_SOURCE_SHA_AND_ASSERTION_LIFECYCLE_REFERENCES; lexical references are not evidence of actual reachability or automatic refusal/non-applicability. Full static oracle and side-effect review still required. No literals or credentials exported.'},ensure_ascii=False,separators=(',',':')))
