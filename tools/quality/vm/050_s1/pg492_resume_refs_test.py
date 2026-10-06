"""BREC198010-R01 independent public literal: only two fixed resume arguments."""
import ast,copy,hashlib,json,pathlib,re,stat
source=pathlib.Path(__file__).with_name('pg492_resume_refs.py');tree=ast.parse(source.read_text())
defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['require','fixed_dropin','compare']]
run='91a748b4-1abe-484c-9682-44f46429b324';morning='schubert-nk-morning-controller.service'
env={'RUN_ID':run,'MORNING':morning,'NATIVE':pathlib.Path('/etc/systemd/system/'+morning+'.d/pg477-native-coverage.conf'),'RUNTIME':pathlib.Path('/run/systemd/system/'+morning+'.d'),'NAME':'pg492-once-resume.conf'}
exec(compile(ast.Module(body=defs,type_ignores=[]),str(source),'exec'),env)
n=0
def check(value):
 global n
 assert value;n+=1
def refused(call):
 global n
 try:call()
 except (ValueError,TypeError):n+=1;return
 raise AssertionError('foreign runtime configuration accepted')
base=b'[Service]\nExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED -cp fixed dev.codex.schubert.nk.batch.file.MorningProcessMain\nUser=root\n'
native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart=/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false --enable-native-access=ALL-UNNAMED -cp fixed dev.codex.schubert.nk.batch.file.MorningProcessMain\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
golden=b'# SSC198: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart=/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false --enable-native-access=ALL-UNNAMED -cp fixed dev.codex.schubert.nk.batch.file.MorningProcessMain --resume 91a748b4-1abe-484c-9682-44f46429b324\n'
check(env['fixed_dropin'](base,native)==golden)
for bad in [None,'text',b'',base+base,base.replace(b'/usr/bin/java',b'/usr/bin/other'),base.replace(b'MorningProcessMain',b'ForeignProcessMain'),base.replace(b' -cp',b' --resume fixed -cp'),base.replace(b' -cp',b' -javaagent:foreign -cp')]:refused(lambda:env['fixed_dropin'](bad,native))
for bad in [None,'text',b'',native+b'User=foreign\n',native.replace(b'append=false',b'append=true'),native.replace(b'parent.exec',b'old.exec'),native.replace(b'\nReadWritePaths=',b' --resume foreign\nReadWritePaths='),native.replace(b'[Service]',b'[Foreign]')]:refused(lambda:env['fixed_dropin'](base,bad))
policy=source.with_name('pg477_unit_references.py').read_bytes();check(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
definition=next(x for x in ast.parse(policy).body if isinstance(x,ast.FunctionDef) and x.name=='exec_record');env['re']=re;exec(compile(ast.Module(body=[definition],type_ignores=[]),'<record>','exec'),env)
argv=golden.split(b'ExecStart=')[-1].strip().decode();env['new_argv']=argv;env['dropin']=golden
fields={'ExecStart','DropInPaths','ReadWritePaths','User','CapabilityBoundingSet','TimeoutStartUSec'};env['CONFIG']=fields
def record(value):return '{ path=/usr/bin/java ; argv[]='+value+' ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
conf={k:'signed-literal' for k in fields};conf['ExecStart']=record(argv.removesuffix(' --resume '+run));conf['DropInPaths']=str(env['NATIVE'])
before={'configuration':{morning:conf,'other.service':dict(conf)},'old':{'allValues':[1,None,'unchanged']}}
env['before']=copy.deepcopy(before);after=copy.deepcopy(before);after['configuration'][morning]['ExecStart']=record(argv);after['configuration'][morning]['DropInPaths']=str(env['NATIVE'])+' '+str(env['RUNTIME']/env['NAME'])
env['strict']=lambda *a:golden
runtime_path=env['RUNTIME']
class FixedRuntime:
 def __truediv__(self,name):return runtime_path/name
 def iterdir(self):return [pathlib.Path('pg492-once-resume.conf')]
env['RUNTIME']=FixedRuntime();env['compare'](after,True);check(True)
historical=copy.deepcopy(before);historical['configuration']['other.service']['ExecStart']=historical['configuration']['other.service']['ExecStart'].replace('start_time=[n/a]','start_time=[Tue 2026-10-06 06:28:53 UTC]').replace('stop_time=[n/a]','stop_time=[Tue 2026-10-06 06:28:54 UTC]').replace('pid=0','pid=3419000').replace('code=(null)','code=exited').replace('status=0/0','status=0')
env['before']=historical;env['compare'](after,True);check(True)
for oldfield,newfield in [('path=/usr/bin/java','path=/usr/bin/foreign'),('ignore_errors=no','ignore_errors=yes'),(' -cp fixed',' -cp foreign')]:
 bad=copy.deepcopy(after);bad['configuration']['other.service']['ExecStart']=bad['configuration']['other.service']['ExecStart'].replace(oldfield,newfield);refused(lambda:env['compare'](bad,True))
env['before']=copy.deepcopy(before)
env['compare'](copy.deepcopy(before),False);check(True)
for key in fields:
 bad=copy.deepcopy(after);bad['configuration'][morning][key]='foreign';refused(lambda:env['compare'](bad,True))
bad=copy.deepcopy(after);bad['old']['allValues'][2]='changed';refused(lambda:env['compare'](bad,True))
bad=copy.deepcopy(after);bad['configuration']['other.service']['User']='foreign';refused(lambda:env['compare'](bad,True))
env['strict']=lambda *a:b'foreign';refused(lambda:env['compare'](after,True))
check(hashlib.sha256(source.with_name('pg480_backup_refs.py').read_bytes()).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
definition=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='release_security')
env['stat']=stat;exec(compile(ast.Module(body=[definition],type_ignores=[]),'<release security>','exec'),env)
literal=[1,2,0,986,stat.S_IFREG|0o640,1,1836,3,4]
check(env['release_security'](literal,[],986))
for index,value in [(2,1),(3,0),(4,stat.S_IFREG|0o644),(4,stat.S_IFLNK|0o640),(5,2),(6,0),(6,16385)]:
 bad=list(literal);bad[index]=value;check(not env['release_security'](bad,[],986))
for bad in [None,[],literal[:-1]]:check(not env['release_security'](bad,[],986))
for acl in ['system.posix_acl_access','system.posix_acl_default']:check(not env['release_security'](literal,[acl],986))
java=source.with_name('Pg492ResumePreparation.java').read_text()
check('TOOLS.resolve("pg492_resume_refs.py")' in java and 'pg481_resume_refs.py' not in java)
check('Files.isRegularFile(TOOLS.resolve("pg492_resume_refs.py"),LinkOption.NOFOLLOW_LINKS)' in java)
check('pg492-resume-tools-v3' in java and 'pg492-resume-preparation-v3' in java)
print('PG492_RESUME_ORACLE assertions='+str(n)+' actual0=true vmAuthority0=true')
