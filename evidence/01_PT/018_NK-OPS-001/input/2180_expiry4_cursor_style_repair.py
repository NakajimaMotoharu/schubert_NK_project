from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'input';TC=R.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');c=ld(I/'2179_expiry4_actual_universe_profile.json');p=R/c['testSources'][0]['path'];old=p.read_text();before='                  case "next" -> (reference || auditPresent) && position[0]++ == 0;\n';after='''                  case "next" -> {
                    if (!reference && !auditPresent) yield false;
                    int current = position[0];
                    position[0]++;
                    yield current == 0;
                  }
''';assert old.count(before)==1;p.write_text(old.replace(before,after));q=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],capture_output=True,text=True);assert q.returncode==0;assert p.read_text().replace(after,before)==old
# Exhaustive relevant Boolean flags and zero/nonzero cursor relation, independent of Production.
cases=[]
for reference in [False,True]:
 for present in [False,True]:
  for pos in [0,1,2,2147483647]:
   expected=(reference or present) and pos==0;oldpos=((pos+1+2**31)%2**32)-2**31 if reference or present else pos;newpos=pos
   if not reference and not present:actual=False
   else:current=newpos;newpos=((newpos+1+2**31)%2**32)-2**31;actual=current==0
   assert (actual,newpos)==(expected,oldpos);cases.append([reference,present,pos,actual,newpos])
proof=ld(B/'evidence/PG28698-expiry4-literal-alias-closure-v1/manifest.json');proof.update(atJST=datetime.datetime.now().astimezone().isoformat(),priorAliasClosure=ref(B/'evidence/PG28698-expiry4-literal-alias-closure-v1/manifest.json'),whole4CursorStyleInverseExact=True,cursorIndependentStateTable=cases,originalStatic38Preserved=ref(B/'evidence/PG28704-expiry4-static-v1/manifest.json'),reasonNewBuildRequired='Whole Test fixture source changed after previous full compiler/static; exact same Main bytes retained, fresh small whole-source qualification is not replay of any completed Product test or global regression.');proof['wholeTestHashes'][str(p.relative_to(R))]=sha(p);O=B/'evidence/PG28722-expiry4-cursor-style-closure-v1';assert not O.exists();O.mkdir();wr(O/'manifest.json',proof);c['guardTypeOnly']=dict(sourceClosure=ref(O/'manifest.json'));c['closureProofs']=[ref(O/'manifest.json'),*c['closureProofs'][1:]];c['slots'].update(prestyle='evidence/01_PT/018_NK-OPS-001/evidence/PG28728-expiry4-prestyle-v1',prepare='evidence/01_PT/018_NK-OPS-001/evidence/PG28730-expiry4-prepare-v1',static='evidence/01_PT/018_NK-OPS-001/evidence/PG28732-expiry4-static-v1',preflight='evidence/01_PT/018_NK-OPS-001/evidence/PG28734-expiry4-preflight-v1');c['privateDirs']['prepare']='pg28730-expiry4-prepare-v1';out=I/'2180_expiry4_cursor_qualified_profile.json';assert not out.exists();wr(out,c);print('cursor inverse-exact; 16 independent flag/position cases; no Producttest run')
