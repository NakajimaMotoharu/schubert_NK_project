"""Independent current full-value/declared-config and ordered terminal Ref vectors."""
import ast,pathlib,json,re,copy,tempfile,types
R=pathlib.Path(__file__).parent;env={'pathlib':pathlib,'json':json};checks=0
def check(v):
 global checks
 checks+=1;assert v,'current Ref vector '+str(checks)
tree=ast.parse((R/'pg579_native_refs.py').read_text())
nodes=[n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name in ['require','check_data']]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pure current Ref checks>','exec'),env)
node=next(n for n in ast.parse((R/'pg477_unit_references.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<declaration parser>','exec'),env);env['re']=re
import pg579_native_owned_stop as h
env['h']=types.SimpleNamespace(terminal=h.terminal,same_generation=h.same_generation,normal_terminal=h.normal_terminal,unique=h.unique,kernel_empty=lambda u:None)
def record(tail='pid=0 ; code=(null) ; status=0/0'):
 return '{ path=/usr/bin/java ; argv[]=/usr/bin/java fixed Main ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; '+tail+' }'
units={u:{'Id':u,'MainPID':'0'if u not in h.EXPECTED else h.EXPECTED[u][0],'ControlPID':'0','Job':'','ActiveState':'inactive'if u not in h.EXPECTED else'active','SubState':'dead'if u not in h.EXPECTED else'running','InvocationID':'a'*32}for u in h.ORDER}
for v in units.values():v.update(LoadState='loaded',ExecMainCode='0',ExecMainStatus='0',Result='success',ExecMainStartTimestampMonotonic='100',ExecMainExitTimestampMonotonic='0',KillMode='control-group',SendSIGKILL='no',Restart='no',Type='simple',RemainAfterExit='no')
first={'units':units,'configuration':{u:{'ExecStart':record(),'User':'literal-declared','ReadWritePaths':'same-native-paths'}for u in h.ORDER},'rows':{'all24':'allColumns'},'pid1':['fixedDone4'],'startup':{'all7':'rawHashAndMetadata'},'originals':{'all102':'unchanged'},'backup':{'allArtifacts':'unchanged'}}
env.update(first=first,stages=[]);env['check_data'](copy.deepcopy(first));check(True)
def denied(v):
 try:env['check_data'](v)
 except (ValueError,TypeError,KeyError):check(True);return
 raise AssertionError('foreign current values accepted')
for key in first:
 if key in ['units','configuration']:continue
 v=copy.deepcopy(first);v[key]='changed';denied(v)
for u in h.ORDER:
 for key in first['configuration'][u]:
  v=copy.deepcopy(first);v['configuration'][u][key]='foreign';denied(v)
 v=copy.deepcopy(first);v['units'][u]['InvocationID']='foreign';denied(v)
v=copy.deepcopy(first);v['configuration']['artemis.service']['ExecStart']=record('pid=353417 ; code=exited ; status=143/0');env['check_data'](v);check(True) # History is data, declaration stays exact.
v=copy.deepcopy(first);v['units']['artemis.service'].update(MainPID='0',ActiveState='inactive',SubState='dead');denied(v) # Before owned Cleanup, implicit broker stop is not admitted.
# Actual durable stop receipt binds each planned terminal; dependent broker admissible only after Cleanup.
with tempfile.TemporaryDirectory(prefix='pg526-ref-fixture-')as tmp:
 env['SAVE']=pathlib.Path(tmp);done=copy.deepcopy(first);stages=h.ORDER[:4];env['stages']=stages
 for u in stages:
  done['units'][u].update(MainPID='0',ActiveState='inactive',SubState='dead');(env['SAVE']/(u+'.stopped.private')).write_text(json.dumps(done['units'][u]))
 done['units']['artemis.service'].update(MainPID='0',ActiveState='inactive',SubState='dead')
 env['check_data'](done);check(True)
 v=copy.deepcopy(done);v['units']['artemis.service']['InvocationID']='foreign';denied(v)
 v=copy.deepcopy(done);v['units']['schubert-nk-api.service']['Job']='changed';denied(v)
helper=(R/'pg579_native_refs.py').read_text();java=(R/'Pg579NativeStop.java').read_text()
check('contextlib.redirect_stdout(sys.stderr)'in helper)
check("unit==h.ORDER[len(stages)]"in helper and 'stages==h.ORDER'in helper)
check('pg578-completed-readonly-v1/before.private.json'in helper and '1951d015fb51a808f85cf86e814222be3de94df80f6564868c6d898ff9e8606f'in helper)
check('MaintenanceUnit.values()'in java and 'refs.check("terminal")'in java)
check('TimeUnit.SECONDS.toNanos(240)'in java and 'Pg579NativeStop'in java and 'PG579-native-stop'in java)
check('import ast,datetime,hashlib,json,os,pathlib,re,'in helper) # re is GLOBAL for injected parser, not a local import.
print('PG579_REFERENCE_ORACLE independentAssertions='+str(checks)+' declaredVsPrimaryHistory=true all24AndOriginalsPreserved=true implicitBrokerAfterOwnedCleanupOnly=true orderedReceipts=true vmActions0=true productionPT0=true')

# Actual oneshot/RemainAfterExit dependency is not a simple service. Before Cleanup it
# must remain active/exited; after its owned receipt only same-generation normal idle.
with tempfile.TemporaryDirectory(prefix='pg579-expiry-fixture-')as tmp:
 env['SAVE']=pathlib.Path(tmp);initial=copy.deepcopy(first)
 expiry='schubert-nk-expiry-cleanup.service'
 initial['units'][expiry].update(ActiveState='active',SubState='exited',MainPID='0',Type='oneshot',RemainAfterExit='yes',ExecMainCode='1',ExecMainStatus='0',ExecMainExitTimestampMonotonic='130')
 env.update(first=initial,stages=[])
 changed=copy.deepcopy(initial);changed['units'][expiry].update(ActiveState='inactive',SubState='dead')
 denied(changed)
 env['stages']=h.ORDER[:4]
 for u in env['stages']:
  changed['units'][u].update(MainPID='0',ActiveState='inactive',SubState='dead');(env['SAVE']/(u+'.stopped.private')).write_text(json.dumps(changed['units'][u]))
 env['check_data'](changed);check(True)
 for key,value in [('InvocationID','foreign'),('ExecMainCode','0'),('ExecMainExitTimestampMonotonic','200'),('Type','simple')]:
  bad=copy.deepcopy(changed);bad['units'][expiry][key]=value;denied(bad)
 print('PG579_EXPIRY_REFERENCE_ORACLE independentAssertions='+str(checks)+' actualOneshot=true afterOwnedCleanupOnly=true')
