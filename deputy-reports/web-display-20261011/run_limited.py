import json,subprocess,sys,time
from pathlib import Path
unit,clazz,phase=sys.argv[1:4]; r=Path('deputy-reports/web-display-20261011'); out=Path('target/deputy-'+unit+'/classes'); out.mkdir(parents=True,exist_ok=True)
base=json.loads((r/'P016-21-compile-command.json').read_text())['argv']; cp=base[base.index('-cp')+1]
if phase=='compile':
 argv=base[:base.index('-d')]+['-sourcepath','src/schubert-nk-protocol/src/main/java:src/schubert-nk-web/src/main/java:src/schubert-nk-web/src/test/java','-d',str(out),'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+clazz+'.java',str(r/'DeputySuiteRunner.java')]
else: argv=[base[0].replace('/javac','/java'),'-Xmx192m','-cp',str(out)+':'+cp,'DeputySuiteRunner','dev.codex.schubert.nk.web.view.'+clazz]
begin=time.time(); result=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True); (r/(unit+'-'+phase+'.txt')).write_text(result.stdout); (r/(unit+'-'+phase+'-command.json')).write_text(json.dumps({'argv':argv,'exit':result.returncode,'wallSeconds':time.time()-begin,'phase':phase,'trigger':unit+' scoped contract'},indent=2)+'\n');print(result.stdout);print('ACTUAL_EXIT',result.returncode)
