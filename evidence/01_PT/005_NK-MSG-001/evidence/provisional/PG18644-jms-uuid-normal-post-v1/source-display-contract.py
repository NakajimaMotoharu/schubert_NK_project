import re,json,hashlib,xml.etree.ElementTree as E,subprocess,copy
from pathlib import Path
R=Path('/home/mini/codex/project1/work/pgpt-foundation');S=R.parent/'pgpt-runs/PG379/pg18644-jms-uuid-normal-unit-v1';source='b09393b0e746b55fd480176d57996d65bd76a95d';raw=json.loads((S/'manifest.safe.json').read_text());expected=set();vectors=[]
for name,pin in raw['begin']['testHashes'].items():
 p=R/name;b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==pin;assert b==subprocess.check_output(['git','show',source+':'+name],cwd=R);s=b.decode();pkg=re.search(r'^package ([\w.]+);',s,re.M).group(1);cl=p.stem;expected.update((pkg+'.'+cl,n) for n in re.findall(r'@Test\s+void (\w+)\(',s));part=s.split('void identityPropertiesMustRetainExactLowercaseCanonicalUuidText()',1)[1].split('  private static',1)[0];table=re.search(r'String\[\]\[\] aliases = \{(.*?)\n    \};',part,re.S).group(1);rows=re.findall(r'\{([^{}]+)\}',table,re.S);assert len(rows)==2 and all(len(row.split(','))==5 for row in rows);assert re.search(r'for \(int field = 0; field < fields.length; field\+\+\)',part);assert 'for (String alias : aliases[field])' in part;assert not re.search(r'\b(return|break|continue)\b',part);vectors.append({'class':pkg+'.'+cl,'method':'identityPropertiesMustRetainExactLowercaseCanonicalUuidText','sourceSha256':pin,'positive':1,'negativeRows':2,'negativePerRow':5,'total':11})
def normalize(rows):
 out=[]
 for cl,n in rows:
  if not isinstance(n,str) or not n.endswith('()') or n[:-2].endswith('()') or (cl,n[:-2]) not in expected:raise ValueError('noarg/source mismatch')
  out.append((cl,n[:-2]))
 if len(out)!=14 or len(set(out))!=14 or set(out)!=expected:raise ValueError('case set mismatch')
 return out
rows=[(c.get('classname'),c.get('name')) for p in (S/'xml').glob('TEST-*.xml') for c in E.parse(p).getroot().findall('.//testcase')];assert len(normalize(rows))==14;neg=[]
for label,changed in [('missing_parentheses',(rows[0][0],rows[0][1][:-2])),('double_parentheses',(rows[0][0],rows[0][1]+'()')),('unknown_method',(rows[0][0],'different()')),('wrong_class',('other.Class',rows[0][1]))]:
 r=rows.copy();r[0]=changed
 try:normalize(r)
 except ValueError:neg.append(label)
 else:raise AssertionError('bad display metadata accepted')
d={'actualExit':0,'source':source,'sourceMethodCases':14,'displayNegativeVectors':neg,'newMethodVectors':vectors,'newMethodTotalVectors':sum(v['total'] for v in vectors),'productTestsExecuted':0,'oldSuccessReexecuted':False,'originalFailure':'f0dd99/1 preserved post-attempt1.py','formalUpdated':False};(S/'source-display-contract.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(d))
