"""Own four-source six-parent source change only; no Test/native/process execution."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG23114-six-parent-original-v1';m=json.loads((O/'manifest.json').read_bytes());old={v['path']:(R/v['path']).read_text() for v in m['inputs']};assert all(hashlib.sha256(old[v['path']].encode()).hexdigest()==v['sha256'] for v in m['inputs']);new={}
def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)
def wrap_declaration(s,name,owner,typed='var'):
 a=f'{typed} {name} =\n';assert s.count(a)==1;start=s.index(a);end=s.index('.start();',start)+len('.start();');builder=s[start+len(a):end-1].strip();return s[:start]+f'try(var {owner}=new OwnedTestProcess(\n'+builder+f')) {{\n{typed} {name}={owner}.process();'+s[end:]
for path,s in old.items():
 if path.endswith('/LinuxExecDescriptorsTest.java'):
  for name in ['competitor','after']:
   s=wrap_declaration(s,name,name+'Owner');needle=f'assertEquals({20 if name=="competitor" else 0}, {name}.exitValue());';s=once(s,needle,needle+'\n}')
 elif path.endswith('/LinuxInodeSecurityTest.java'):
  s=wrap_declaration(s,'process','processOwner','Process');s=once(s,'Process process=processOwner.process();\n    try {','Process process=processOwner.process();');s=once(s,'    } finally {\n      process.destroyForcibly();\n    }','    }')
 else:
  # external helper only, leaving other methods and all arguments/oracles unchanged.
  start=s.index('  private int external(Path file) throws Exception {');end=s.index('\n  private ',start+4);part=s[start:end];part=wrap_declaration(part,'child','childOwner');part=once(part,'var child=childOwner.process();\n    try {','var child=childOwner.process();');part=once(part,'    } finally {\n      if (child.isAlive()) child.destroy();\n    }','    }');s=s[:start]+part+s[end:]
  if path.endswith('/LinuxFileLockTest.java'):
   start=s.index('  void externalFlockInteroperability()');end=s.index('\n  @Test',start);part=s[start:end];part=wrap_declaration(part,'child','childOwner');part=once(part,'if (child.isAlive()) child.destroy();','childOwner.close();');part=once(part,'            }\n          }\n          assertEquals(Optional.of(9)', '            }\n            }\n          }\n          assertEquals(Optional.of(9)');s=s[:start]+part+s[end:]
 new[path]=s
assert len(new)==4 and all(new[n]!=old[n] for n in old)
for n,s in new.items():(R/n).write_text(s)
print('six parent ownership scopes source-written; no actual operation')
