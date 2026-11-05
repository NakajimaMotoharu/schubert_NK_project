"""Literal-only same-token refactor for actual PG18660 findings; preserve all raw values."""
from pathlib import Path
import re,json,hashlib,xml.etree.ElementTree as E
root=Path.cwd();run=root.parent/'pgpt-runs/PG379/pg18668-char-literal-repair-v1';assert not run.exists();run.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
def tokens(s):
 out=[];i=0
 while i<len(s):
  if s[i].isspace():i+=1;continue
  if s.startswith('//',i):
   j=s.find('\n',i);i=len(s) if j<0 else j+1;continue
  if s.startswith('/*',i):j=s.index('*/',i+2);i=j+2;continue
  start=i;c=s[i]
  if c in ('"',"'"):
   assert not s.startswith('"""',i),'textblocks require separate parser'
   i+=1
   while i<len(s):
    if s[i]=='\\':i+=2;continue
    if s[i]==c:i+=1;break
    i+=1
   out.append((start,i,'string' if c=='"' else 'char',s[start:i]));continue
  if c.isalpha() or c in '_$':
   i+=1
   while i<len(s) and (s[i].isalnum() or s[i] in '_$'):i+=1
   out.append((start,i,'id',s[start:i]));continue
  i+=1;out.append((start,i,'symbol',s[start:i]))
 return out
raw=E.parse(root.parent/'pgpt-runs/PG379/pg18660-correlated-log-char-static-v1/pmd.xml').getroot();rows=[]
for f in raw:
 if not f.tag.endswith('file'):continue
 path=Path(f.get('name'));wanted=[]
 for v in f:
  if v.get('rule')=='AvoidDuplicateLiterals':
   msg=' '.join(v.itertext()).strip();m=re.search(r'literal \\\"(.*?)\\\" appears',msg);assert m,msg;wanted.append(m.group(1))
 if not wanted:continue
 old=path.read_text();lex=tokens(old);sourceTokens={t for _,_,kind,t in lex if kind=='string'};mapping={};used={t for _,_,kind,t in lex if kind=='id'}
 for text in wanted:
  candidates=[]
  for token in sourceTokens:
   decoded=None
   try:decoded=json.loads(token)
   except json.JSONDecodeError:pass
   if token[1:-1]==text or decoded==text:candidates.append(token)
  assert len(candidates)==1,(path.name,text,candidates)
  token=candidates[0];label=re.sub(r'[^A-Za-z0-9]+','_',text).strip('_').upper();prefix='FIXTURE_' if path.name.endswith('Test.java') else 'FIELD_' if re.fullmatch(r'[a-z][A-Za-z0-9]*',text) else 'VALUE_';name=prefix+(label[:70] or 'TEXT')
  if name in used:name+='_'+sha(token.encode())[:8].upper()
  assert name not in used;used.add(name);mapping[token]=name
 changes=[(a,b,mapping[t]) for a,b,k,t in lex if k=='string' and t in mapping];new=old
 for a,b,value in reversed(changes):new=new[:a]+value+new[b:]
 declarations=''.join('  private static final String '+name+' = '+token+';\n' for token,name in mapping.items())+'\n';match=re.search(r'(?m)^(?:public )?(?:final )?class \w+ \{\n',new);assert match,path;insert=match.end();new=new[:insert]+declarations+new[insert:]
 check=new.replace(declarations,'',1);inverse={name:token for token,name in mapping.items()};expanded=[inverse.get(t,t) if k=='id' else t for _,_,k,t in tokens(check)];assert expanded==[t for *_,t in lex],path
 backup=run/path.name;backup.write_text(old);path.write_text(new);rows.append({'path':str(path.relative_to(root)),'beforeSha256':sha(old.encode()),'afterSha256':sha(new.encode()),'literals':len(mapping),'useSites':len(changes),'expandedTokensExact':True,'constantBindings':{v:k for k,v in mapping.items()},'originalSource':str(backup)})
(run/'manifest.json').write_text(json.dumps({'rows':rows,'changedFiles':len(rows),'newLiteralConstants':sum(r['literals'] for r in rows),'semanticsCheck':'Remove only exact generated declarations, expand new identifiers to original exact Java string tokens, compare entire non-comment token sequence. No values normalized.','productTestsExecuted':0},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'files':len(rows),'constants':sum(r['literals'] for r in rows),'tokenEquality':True,'manifestSha256':sha((run/'manifest.json').read_bytes())}))
