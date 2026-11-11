"""Compare independent field fixtures with current canonical UI tables; never rewrite fixture/oracle."""
from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26248-canonical-ui-field-comparison-v1';assert not O.exists();layoutPattern=r'\b[A-Z]{3}(?:REQ|RSP|EVT)[0-9]{2}\b';aliases={'PAGED48','MEDIA1024','USRMUT24'};tables=collections.defaultdict(list);references=collections.defaultdict(set);docs={}
for name in ['234_認証・検索・シナリオ電文仕様.md','235_メディア・ログ電文仕様.md','236_管理・質問・通知電文仕様.md']:
 path='documents/200_UI/230_インターフェース/'+name;text=subprocess.check_output(['git','show','origin/main:'+path],text=True);docs[path]=hashlib.sha256(text.encode()).hexdigest();context=None
 for i,line in enumerate(text.splitlines(),1):
  if line.startswith('#'):
   ids=re.findall(layoutPattern,line);shared=[a for a in aliases if '`'+a+'`' in line]
   if line.startswith('## ') and shared:context=('SHARED',shared[0])
   elif ids and ('data' in line.lower() or 'record' in line.lower()):
    assert len(ids)==1;context=(ids[0],'RECORD' if 'record' in line.lower() else 'DATA')
   else:context=None
   continue
  used=[a for a in aliases if '`'+a+'`' in line or line.startswith('| '+a+' |')]
  if context and context[0]=='SHARED':
   for id in re.findall(layoutPattern,line):references[(id,'DATA')].add(context[1])
  else:
   for alias in used:
    ids=re.findall(layoutPattern,line)
    if ids:
     for id in ids:references[(id,'DATA')].add(alias)
    elif context and context[1]=='DATA' and 'RSP' in context[0]:references[context].add(alias)
  if not context or not line.startswith('|'):continue
  cells=[c.strip() for c in line.strip().strip('|').split('|')]
  if len(cells)<6 or not cells[1].replace(',','').isdigit() or not cells[2].replace(',','').isdigit():continue
  if cells[3] not in ['X','N','B']:continue
  row=[cells[0],str(int(cells[1].replace(',',''))),str(int(cells[2].replace(',',''))),cells[3],cells[4],'|'.join(cells[5:])];tables[context].append(dict(tuple=row,source=path,line=i))
fixture=R/'src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv';expected=[line.split('\t') for line in fixture.read_text().splitlines() if line and not line.startswith('#')];byScope=collections.defaultdict(list)
for row in expected:assert len(row)==8;byScope[(row[0],row[1])].append(row[2:])
results=[];differences=[]
for key,rows in byScope.items():
 actual=list(tables[key])
 for alias in sorted(references[key]):actual+=tables[('SHARED',alias)]
 actual.sort(key=lambda x:int(x['tuple'][1]));values=[x['tuple'] for x in actual];matched=values==rows
 results.append(dict(layout=key[0],area=key[1],expectedRows=len(rows),canonicalRows=len(values),matches=matched,sharedAliases=sorted(references[key]),canonicalFields=actual))
 if not matched:
  for index in range(max(len(rows),len(values))):
   old=rows[index] if index<len(rows) else None;new=values[index] if index<len(values) else None
   if old!=new:differences.append(dict(layout=key[0],area=key[1],index=index,fixture=old,canonical=new))
O.mkdir();data={'scope-comparison.json':results,'unconfirmed-differences.json':differences,'canonical-document-hashes.json':docs}
for n,v in data.items():(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),status='CANONICAL_FIELDS_MATCH' if not differences else 'UNCONFIRMED_DIFFERENCES_NOT_PRODUCT_FAILURE_OR_APPROVED_ORACLE_CHANGE',fixtureSha256=sha(fixture),fixtureFieldRows=len(expected),layoutAreaScopes=len(results),matchingScopes=sum(x['matches'] for x in results),unconfirmedRows=len(differences),fixturesModified=0,baselineModified=0,productTestsExecuted=0,newAcceptance=0,files={n:sha(O/n) for n in data},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,status=m['status'],scopes=len(results),matching=m['matchingScopes'],unconfirmedRows=len(differences),firstDifferences=differences[:8],manifestSha256=sha(O/'manifest.json')),ensure_ascii=False))
