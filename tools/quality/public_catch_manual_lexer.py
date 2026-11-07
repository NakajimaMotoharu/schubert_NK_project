"""Independent raw-source character scanner; definitions only, no file or target operation."""
import json
import hashlib

def lexical(text):
 out=[];i=0
 while i<len(text):
  at=i;c=text[i]
  if c.isspace():i+=1;continue
  if text.startswith('//',i):
   z=text.find('\n',i+2);i=len(text) if z<0 else z;continue
  if text.startswith('/*',i):
   z=text.find('*/',i+2);assert z>=0;i=z+2;continue
  if c in ['"',"'"]:
   if text.startswith('"""',i):
    z=text.find('"""',i+3);assert z>=0;i=z+3
   else:
    quote=c;i+=1
    while i<len(text) and text[i]!=quote:
     i+=2 if text[i]=='\\' else 1
    assert i<len(text);i+=1
   out.append(('LITERAL',at));continue
  if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$':
   i+=1
   while i<len(text) and text[i] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$0123456789':i+=1
   out.append((text[at:i],at));continue
  out.append((c,at));i+=1
 return out

def bodies(text):
 tokens=lexical(text);out=[]
 def closing(at,left,right):
  assert tokens[at][0]==left;depth=0
  for j in range(at,len(tokens)):
   if tokens[j][0]==left:depth+=1
   elif tokens[j][0]==right:depth-=1
   if depth==0:return j
  raise AssertionError('incomplete declared raw-source delimiter')
 for at,(word,offset) in enumerate(tokens):
  if word!='catch':continue
  end=closing(at+1,'(',')');head=[x for x,_ in tokens[at+2:end]]
  if 'SQLException' not in head:continue
  stop=closing(end+1,'{','}');body=[x for x,_ in tokens[end+2:stop]];out.append((text.count('\n',0,offset)+1,hashlib.sha256(json.dumps(body).encode()).hexdigest()))
 return out
