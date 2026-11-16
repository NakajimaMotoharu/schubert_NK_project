"""Read approved Markdown wire tables independently; never invoke a production codec."""
from pathlib import Path
import csv,re,subprocess

def cells(line):return [x.strip() for x in line.strip().strip('|').split('|')]
def integer(value):return int(value.replace(',',''))
def rows(text):
 out=[]
 for number,line in enumerate(text.splitlines(),1):
  if not line.startswith('|'):continue
  c=cells(line)
  if len(c)>=6 and re.fullmatch(r'[\d,]+',c[1]) and re.fullmatch(r'[\d,]+',c[2]) and c[3] in ['N','X','B'] and c[4] in ['M','O','C','F']:
   out.append(dict(label=c[0],start=integer(c[1]),length=integer(c[2]),wire=c[3],presence=c[4],rule='|'.join(c[5:]),lineInBlock=number))
 return out

def split_blocks(text):
 found=list(re.finditer(r'^#{2,4} (.*)$',text,re.M));return [dict(title=m.group(1),body=text[m.end():found[i+1].start() if i+1<len(found) else len(text)],startLine=text[:m.start()].count('\n')+1) for i,m in enumerate(found)]
def ui_layouts(text):
 out={};current_if=None
 for number,line in enumerate(text.splitlines(),1):
  if not line.startswith('|'):continue
  c=cells(line)
  if len(c)<9:continue
  match=re.fullmatch(r'([A-Z]) `([A-Z0-9]{8})`',c[1])
  if not match:continue
  kind,key=match.groups();assert key not in out
  if c[0]:current_if=c[0]
  out[key]=dict(layout=key,kind=kind,interaction=c[2],data=integer(c[3]),record=integer(c[4]),maximum=integer(c[5]),total=integer(c[6]),interface=current_if,role=c[7],uiSpec=c[8],line=number)
 return out

def ss_types(text):
 out={}
 for number,line in enumerate(text.splitlines(),1):
  if not line.startswith('|'):continue
  c=cells(line)
  if len(c)<5:continue
  m=re.fullmatch(r'`([A-Z0-9]{8})` ([\d,]+)/([\d,]+)/([\d,]+)/([\d,]+)',c[0])
  if not m:continue
  key=m.group(1);assert key not in out;names=re.findall(r'`([A-Z][A-Za-z0-9_]*)`',c[1]);assert len(names) in [1,2],(key,names)
  out[key]=dict(layout=key,lengths=list(map(integer,m.groups()[1:])),dataType=names[0],recordType=names[1] if len(names)>1 else '-',handler=c[2],databaseTrace=c[3],validationTrace=c[4],line=number)
 return out

def ui_field_blocks(documents):
 common={};specific={}
 for name,text in documents.items():
  for block in split_blocks(text):
   block.update(document=name,rows=rows(block['body']));m=re.search(r'`([A-Z0-9]{8})` (data|record)',block['title'])
   if m:
    key=(m.group(1),m.group(2).upper());assert key not in specific;specific[key]=block
   elif '共通' in block['title']:
    keys=re.findall(r'`([A-Z0-9]+)`',block['title'])
    if keys and block['rows']:
     assert len(keys)==1 and keys[0] not in common;common[keys[0]]=block
 return common,specific

def resolve_field_rows(layout,area,length,common,specific,documents):
 key=(layout,area);block=specific.get(key)
 if length==0:
  assert block is None or not block['rows'],(key,'zero-length area has fields')
  return []
 if block is None:
  matches=[]
  for doc,text in documents.items():
   m=re.search(r'`'+layout+r'`は`([A-Z0-9]+)`',text)
   if m:matches.append((doc,m.group(1)))
  assert len(matches)==1,(key,'no unique direct or common clause',matches)
  doc,alias=matches[0];assert alias in common;block=dict(document=doc,body='`'+alias+'`',rows=[],title=layout+' common clause')
 own=block['rows'];position=1;full=bool(own)
 for x in own:
  if x['start']!=position:full=False
  position=x['start']+x['length']
 if full and position==length+1:
  return [dict(x,document=block['document'],sourceBlock=block['title']) for x in own]
 result=[]
 for alias,c in common.items():
  relevant=[]
  for line in block['body'].splitlines():
   other=re.search(r'`([A-Z0-9]{8})`は`([A-Z0-9]+)`',line)
   if other and other.group(1)!=layout:continue
   relevant.append(line)
  if '`'+alias+'`' in '\n'.join(relevant):result.extend(dict(x,document=c['document'],sourceBlock=c['title']) for x in c['rows'])
 result.extend(dict(x,document=block['document'],sourceBlock=block['title']) for x in block['rows'])
 result.sort(key=lambda x:x['start']);next_start=1
 for x in result:assert x['start']==next_start,(key,'gap/duplicate',x,next_start);next_start+=x['length']
 assert next_start==length+1,(key,'field length',next_start,length)
 return result

def tsv(path):return list(csv.reader([l for l in path.read_text().splitlines() if l and not l.startswith('#')],delimiter='\t'))

if __name__=='__main__':
 r=Path.cwd();folder=r/'documents/200_UI/230_インターフェース';doc={str(p.relative_to(r)):subprocess.check_output(['git','show','origin/main:'+str(p.relative_to(r))],text=True) for p in sorted(folder.glob('23[456]*'))};common,specific=ui_field_blocks(doc);ui_name='documents/200_UI/230_インターフェース/233_固定長電文インターフェース一覧.md';u=ui_layouts(subprocess.check_output(['git','show','origin/main:'+ui_name],text=True));base=r/'src/schubert-nk-protocol/src/test/resources/protocol';expected=tsv(base/'fields-ui234-236.tsv');fixture={}
 for row in expected:fixture.setdefault((row[0],row[1]),[]).append((int(row[3]),int(row[4]),row[5],row[6]))
 discrepancies=[]
 for key,l in u.items():
  for area,length in [('DATA',l['data']),('RECORD',l['record'])]:
   try:actual=resolve_field_rows(key,area,length,common,specific,doc);shapes=[(x['start'],x['length'],x['wire'],x['presence']) for x in actual];assert shapes==fixture.get((key,area),[]),(key,area,'shape mismatch',shapes,fixture.get((key,area),[]))
   except AssertionError as failure:discrepancies.append(str(failure))
 print('common',list(common),'layout',len(u),'fieldRows',len(expected),'discrepancies',discrepancies[:12],'total',len(discrepancies))
