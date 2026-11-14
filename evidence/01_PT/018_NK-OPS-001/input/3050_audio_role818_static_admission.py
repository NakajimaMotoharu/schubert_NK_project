"""Fresh per-site Role11 review plus same-byte prior qualifications. No suppression/coverage exclusions."""
from pathlib import Path
import json,hashlib,collections,re,subprocess
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3049_audio_role818_physical56_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);proof=load(b/'evidence/PG32606-audio-role818-source-v1/manifest.json');changed=set(proof['changedMigrationMainAndTestPaths']);paths=set(pf['mainSources']+[x['path'] for x in pf['testSources']]);assert changed<=paths
# Verify every changed class differs from its prior source only by declared role width/new vector.
def tokens(text):return [x for x in re.findall(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:[^"\\]|\\.)*"|\w+|[^\s]',text) if not x.startswith(('//','/*'))]
inverse={}
for path in changed:
 current=(r/path).read_text();old=subprocess.check_output(['git','show',proof['previousProductionCoreMain']+':'+path],text=True)
 if path.endswith('/AudioFileCopyRow.java'):
  current=current.replace('  private static final int MAXIMUM_AUDIO_ROLE_BYTES = 11;\n','').replace('boundedText(required(fields, 6), MAXIMUM_AUDIO_ROLE_BYTES);','boundedText(required(fields, 6), 8);')
 elif path.endswith('/AudioFileCopyRowTest.java'):
  current=current.replace('  private static final String CURRENT_MOVIE_AUDIO_ROLE = "movie_audio";\n','').replace('List.of(6, 11)','List.of(6, 8)');start=current.index('  @Test\n  void currentMovieAudioElevenBytesArePreservedWithoutRenamingOrTruncating()');end=current.index('  private static AudioFileCopyRow rowWith',start);current=current[:start]+current[end:]
 else:
  current=current.replace(r'audio_role\tvarchar\tcharacter varying(11)',r'audio_role\tvarchar\tcharacter varying(8)').replace('octet_length(audio_role) BETWEEN 1 AND 11','octet_length(audio_role) BETWEEN 1 AND 8')
 assert tokens(current)==tokens(old),path;inverse[path]=dict(priorSha256=hashlib.sha256(old.encode()).hexdigest(),currentSha256=sha(r/path),allOtherCodeTokensUnchanged=True)
prior={};historical={};sources=['2986_identity_sequence645_static_admission.json','3030_file_map122_static_admission.json','3039_audio_read20_static_admission.json','2995_entry_read20_static_admission.json','3013_file_read20_static_admission.json','3004_entry_map180_static_admission.json','2851_speaker_read176_static_admission.json','2842_speaker_map156_static_admission.json','2833_master_finger403_static_admission.json']
for file in sources:
 a=load(i/file);old=load(r/a['static']['path'])
 for x in a['sourceAnchors']:
  path=x['path']
  if path not in paths:continue
  key=(path,x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']);hkey=(path,x['rule'],x['sourceAnchor'],x['message'])
  if path in changed:historical.setdefault(hkey,x)
  elif sha(r/path)==old['inputHashes'][path]:prior.setdefault(key,x)
rows=[];counts=collections.Counter();fresh=[]
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path not in changed:
  assert key in prior,key;rows.append(prior[key]);counts['sameByte']+=1;continue
 hkey=(path,raw['rule'],anchor,raw['message']);assert hkey in historical,hkey;before=historical[hkey];rule=raw['rule']
 if rule=='AvoidCatchingGenericException':assert anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {']
 elif rule=='CompareObjectsWithEquals':assert anchor=='if (cleanup != primary) primary.addSuppressed(cleanup);'
 elif rule=='UseProperClassLoader':assert re.fullmatch(r'(Connection|Statement|PreparedStatement|ResultSet)\.class\.getClassLoader\(\),',anchor)
 elif rule=='NullAssignment':assert path.endswith('MigrationMasterTargetPublisherTest.java') and anchor=='? null'
 elif rule in ['DoNotUseThreads','CloseResource']:
  assert '/test/' in path and ('executor' in anchor or anchor in ['var conn = f.connection();','var connection = f.connection();'])
 else:raise AssertionError((rule,anchor))
 reason='SSC396 fresh site review on current Role11 source: the inverse code-token proof confirms only the declared width/new independent vector changed; this exact owned-resource, synthetic SQL-null, JDK-only Proxy or finite-worker contract remains individually valid. '+before['reason']
 rows.append(dict(path=path,rule=rule,sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'));counts['freshRoleWidthSites']+=1;fresh.append(dict(path=path,rule=rule,line=line,anchor=anchor))
assert len(rows)==len(s['rawFindings'])==466 and counts==dict(sameByte=399,freshRoleWidthSites=67)
review=b/'evidence/PG32636-audio-role818-static-v1/role11-site-review.json';assert not review.exists();review.write_text(json.dumps(dict(actualExit=0,sourceInverseTokenProof=inverse,freshSites=fresh,sameByteSites=399,freshReviewedSites=67,scope='JAVA_ONLY_DB_TEST_NOT_COMPILED',applicable=0,unclassified=0),ensure_ascii=False,indent=2)+'\n')
p=i/'3050_audio_role818_static_admission.json';assert not p.exists();p.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,sameByte=399,freshReviewed=67,rawPmd=466,applicable=0,unclassified=0))
