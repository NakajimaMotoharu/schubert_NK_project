"""Offline private HPROF diagnostic: print only storage exception stack structure.
Never emit raw String/byte arrays, credentials, owners, or heap contents. No VM mutation.
"""
import pathlib,struct,re,json
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
raw=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg1045-storage-private-v1.hprof').read_bytes()
p=raw.index(b'\0')+1;size=struct.unpack_from('>I',raw,p)[0];assert size in (4,8);p+=12
strings={};names={};classes={};instances={};arrays={};frames=[];objects={};primitive_arrays={}
sizes={2:size,4:1,5:2,6:4,7:8,8:1,9:2,10:4,11:8}
def number(buf,at,n):return int.from_bytes(buf[at:at+n],'big')
while p<len(raw):
 tag=raw[p];length=number(raw,p+5,4);b=raw[p+9:p+9+length];p+=9+length
 if tag==1:strings[number(b,0,size)]=b[size:].decode('utf-8',errors='replace')
 elif tag==2:names[number(b,4,size)]=number(b,8+size,size)
 elif tag in (12,28):
  q=0
  while q<len(b):
   t=b[q];q+=1
   if t in (255,5,7):q+=size
   elif t==1:q+=size*2
   elif t in (2,3):
    if t==3:frames.append((number(b,q,size),number(b,q+size,4),number(b,q+size+4,4)))
    q+=size+8
   elif t in (4,6):q+=size+4
   elif t==8:q+=size+8
   elif t==32:
    cid=number(b,q,size);superclass=number(b,q+size+4,size);q+=size*7+8
    n=number(b,q,2);q+=2
    for _ in range(n):typ=b[q+2];q+=3+sizes[typ]
    n=number(b,q,2);q+=2
    for _ in range(n):typ=b[q+size];q+=size+1+sizes[typ]
    n=number(b,q,2);q+=2;fields=[]
    for _ in range(n):fields.append((number(b,q,size),b[q+size]));q+=size+1
    classes[cid]=(superclass,fields)
   elif t==33:
    oid=number(b,q,size);cid=number(b,q+size+4,size);n=number(b,q+size*2+4,4);q+=size*2+8
    instances[oid]=(cid,b[q:q+n]);q+=n
   elif t==34:
    oid=number(b,q,size);n=number(b,q+size+4,4);q+=size*2+8
    objects[oid]=b[q:q+n*size];q+=n*size
   elif t==35:
    oid=number(b,q,size);n=number(b,q+size+4,4);typ=b[q+size+8];q+=size+9
    primitive_arrays[oid]=(typ,b[q:q+n*sizes[typ]])
    if typ==8:arrays[oid]=b[q:q+n]
    q+=n*sizes[typ]
   else:raise ValueError('Unsupported heap tag '+str(t))
   assert q<=len(b)
assert p==len(raw)
def classname(cid):return strings.get(names.get(cid),'unknown')
def fields(oid):
 cid,data=instances[oid];result={};offset=0
 while cid:
  parent,fs=classes[cid]
  for name,t in fs:
   n=sizes[t];result[strings[name]]=number(data,offset,n);offset+=n
  cid=parent
 assert offset==len(data)
 return result
def ancestry(cid):
 result=[]
 while cid:result.append(classname(cid));cid=classes[cid][0]
 return result
def text(oid):
 if not oid:return ''
 f=fields(oid);data=arrays.get(f.get('value'),b'');coder=f.get('coder',0)
 return data.decode('latin1' if coder==0 else 'utf-16le',errors='replace')
literals=set()
for path in (ROOT/'src').rglob('*.java'):
 if '/src/main/' in str(path):literals.update(re.findall(r'"([^"\n\\]{3,150})"',path.read_text()))
results=[]
for oid,thread,frame in frames:
 if oid not in instances:continue
 cid=instances[oid][0]
 if classname(cid)!='dev/codex/schubert/nk/storage/StorageIoException':continue
 if 'java/lang/Throwable' not in ancestry(cid):continue
 f=fields(oid);message=text(f.get('detailMessage',0))
 item={'exceptionClass':classname(cid),'threadSerial':thread,'frame':frame,'exactSourceLiteral':'<all-messages-redacted>'}
 bt=f.get('backtrace',0)
 if bt in objects:
  safe_classes=[];safe_methods=[];indexes=[];a=objects[bt]
  for offset in range(0,len(a),size):
   nested=number(a,offset,size)
   if nested in primitive_arrays:
    typ,data=primitive_arrays[nested]
    if typ in (9,10):indexes.append({'slot':offset//size,'type':typ,'first24':[number(data,i,sizes[typ]) for i in range(0,min(len(data),sizes[typ]*24),sizes[typ])]})
   if nested not in objects:continue
   na=objects[nested]
   for index in range(0,len(na),size):
    value=number(na,index,size)
    if value in names:safe_classes.append(classname(value))
    elif value in instances and classname(instances[value][0])=='java/lang/String':
     candidate=text(value)
     if re.fullmatch(r'[A-Za-z0-9_.$<>]{1,100}',candidate):safe_methods.append(candidate)
  item['backtraceClasses']=safe_classes[:24];item['backtraceMethodNames']=safe_methods[:24];item['backtraceMethodIndexes']=indexes
 trace=f.get('stackTrace',0)
 if trace in objects:
  safe=[];a=objects[trace]
  for offset in range(0,len(a),size):
   element=number(a,offset,size)
   if element not in instances:continue
   ef=fields(element);declaring=text(ef.get('declaringClass',0));method=text(ef.get('methodName',0))
   if re.fullmatch(r'[A-Za-z0-9_.$/]+',declaring) and re.fullmatch(r'[A-Za-z0-9_.$<>]+',method):
    line=ef.get('lineNumber',0);safe.append({'class':declaring,'method':method,'line':line if line<2**31 else line-2**32})
  item['stackTrace']=safe[:24]
 cause=f.get('cause',0)
 if cause and cause!=oid and cause in instances:
  cf=fields(cause);cm=text(cf.get('detailMessage',0));item['causeClass']=classname(instances[cause][0]);item['causeSourceLiteral']='<all-messages-redacted>'
 results.append(item)
print(json.dumps({'privateHeapParsed':True,'onlyFrameRootExceptions':results,'rawHeapPrinted':False,'arbitraryMessagesPrinted':False}))
