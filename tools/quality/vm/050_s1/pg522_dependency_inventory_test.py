"""BUG822/YKT591 independent host/guest dependency closure for this one connection."""
import ast,pathlib
R=pathlib.Path(__file__).parent;checks=0
def check(v):
 global checks
 checks+=1
 assert v,'operator dependency inventory '+str(checks)
def imports(name):
 result=set()
 for n in ast.walk(ast.parse((R/name).read_text())):
  if isinstance(n,ast.Import):result.update(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom):result.add(n.module)
 return result
for n in ['pg519_runtime_retirement_test.py','pg520_runtime_retirement_test.py']:
 check(imports(n)=={'ast','copy','pathlib','re'})
 check('.java' not in (R/n).read_text() and 'pg520_static_scope_check' not in (R/n).read_text())
check(imports('pg521_runtime_resume_test.py')=={'ast','copy','pathlib','re','pg520_static_scope_check'})
check('Pg521RuntimeResume.java' in (R/'pg521_runtime_resume_test.py').read_text())
old=(R/'pg521_resume_native_v1.py').read_text();new=(R/'pg521_resume_native_v2.py').read_text()
check("test=subprocess.run(ssh+['sudo -n python3 -B '+dest+'/pg521_runtime_resume_test.py']" in old)
check("test=subprocess.run(ssh+['sudo -n python3 -B '+dest+'/pg521_runtime_resume_test.py']" not in new)
check("subprocess.run(['python3','-B',str(R/'pg521_runtime_writer_test.py')],check=True)" in new)
check("['Pg521RuntimeResume.class','Pg521RuntimeResume$References.class']" in new)
check('Pg521RuntimeArgumentTest.class' not in new)
check("classes=W/'pg521-resume-tools-v2'" in new)
check(imports('pg522_watch_parent.py')=={'datetime','hashlib','http.client','json','pathlib','re','ssl','subprocess','sys','time','pg457_stable_actor','pg462_observer_identity'})
check(imports('pg457_stable_actor.py')=={'pathlib'})
check(imports('pg462_observer_identity.py')==set())
stage=(R/'pg522_prepare_observer_v1.py').read_text()
check("['pg522_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py']" in stage)
check("set(p.name for p in stage.iterdir())==set(EXPECTED)" in stage)
check("hashlib.sha256((root/name).read_bytes()).hexdigest()==sha" in stage)
for n in ['pg522_prepare_observer_v1.py','pg522_external_resume_once.py']:
 tree=ast.parse((R/n).read_text())
 payload=next(x.value.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'payload','PAYLOAD'}for t in x.targets))
 for x in ast.walk(ast.parse(payload)):
  if isinstance(x,ast.Import):check(all(a.name in {'ast','datetime','hashlib','json','os','pathlib','shutil','stat','subprocess'}for a in x.names))
 check('pyflakes' not in payload and 'Pg521RuntimeResume.java' not in payload)
print('PG522_DEPENDENCY_ORACLE independentAssertions='+str(checks)+' oldHostGuestViolationReproduced=true currentHostOnlySeparated=true observerExact3Closure=true productionPT0=true vmActions0=true')
