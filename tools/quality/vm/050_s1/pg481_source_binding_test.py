"""Fixed one-delivery authority/source/budget structural guard, never executes payload."""
import ast,pathlib
r=pathlib.Path(__file__).parent;source=(r/'pg481_external_resume_once.py').read_text();tree=ast.parse(source)
payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets));ast.parse(payload)
n=0
def check(v):
 global n
 assert v;n+=1
for token in ['pg479-six-full-v1.source','pg479-six-full-v1.exit','pg481-prepared-resume-acceptance','0.1.0-PG479','2026-10-06T06:28:43.734078+00:00','O_EXCL','O_NOFOLLOW',"originalBudgetSeconds':1800",'priorGuardRequiresReattachment',"rows()==before['rows']","metadata(request/'backup-request')==before['request']['metadata']"]:check(token in source)
check(source.count("'start','--no-block','schubert-nk-morning-controller.service'")==1)
check("b'preparedResumeAccepted=true\\nallNewScopesReturnedNormally=true\\noriginalRunCutoffUnchanged=true\\ndatabaseUpdates0=true\\nstarts0=true\\n'" in source)
for name in ['pg481_prepare_observer_v1.py','pg481_parent_observer_v1.sh','pg481_watch_parent.py']:
 text=(r/name).read_text();check('cce61f63900b1479f9f8dbdc338e222b1c8c38a3' not in text and '613b71a06c2b215887219cd3502d3db34542fea957e0d88dbb9c54c8bab18667' not in text)
check('bab704707b8fd7e0dc7581c4489f0892236efe73' in (r/'pg481_parent_observer_v1.sh').read_text())
check('pg481-pending-codeonly' in (r/'pg481_prepare_observer_v1.py').read_text())
accept=(r/'pg481_prepared_resume_refs.py').read_text();check('daemon-reload' not in accept and 'RUNTIME.mkdir' not in accept and "['before','release']" in accept)
print('PG481_SOURCE_BINDING_ORACLE assertions='+str(n)+' starts0=true productionPT0=true')
