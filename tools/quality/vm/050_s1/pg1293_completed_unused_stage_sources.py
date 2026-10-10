"""SS343 signed unused placement under current genuine-DONE M/A/RODB/tenRefs.

No cold-empty/INVALID authority is substituted for current ordinary ISSUED/DONE.
Only the unused sibling release and private signature may be created.
"""
import ast
from pg1253_fresh_owned_stop_sources_v2 import sources as previous
from pg1069_cold_candidate_sources import stage_body as archive_stage

SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
DIGEST='ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99'
BASELINE='/var/lib/pgpt-s1-preservation/pg1253-native-stop-v1/after.private.json'
BASELINE_SHA='7b48c21af7d30d0bdad3d0341ad3a29412fff405540ef95c0ca97328608f8f77'


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('fixed completed stage boundary refused')
    return text.replace(old,new)


def stage_body():
    text=archive_stage()
    for old,new in [('d5b00104280028d9ea81b44c1d1c805f3c2861ed',SOURCE),
      ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',DIGEST),
      ('PG1068','PG1292'),('pg1068','pg1292'),('pg1071','pg1295')]:text=text.replace(old,new)
    ast.parse(text);return text


def sources():
    result={}
    for name,text in previous().items():
        name=name.replace('Pg1253','Pg1293').replace('pg1253','pg1293')
        text=text.replace('Pg1253','Pg1293').replace('pg1253','pg1293').replace('PG1253','PG1293')
        text=text.replace('Pg1293NativeStop','Pg1293UnusedStage')
        name=name.replace('Pg1293NativeStop','Pg1293UnusedStage')
        text=text.replace('PG998-native-stop','PG998-native-stage')
        if name=='Pg1293UnusedStage.java':
            text=once(text,'"stop".equals(args[0])','"place".equals(args[0])')
            text=once(text,'"stop",Integer.toString(pid)','"place",Integer.toString(pid)')
            text=once(text,'require("before".equals(name) || name.startsWith("stop:") || "terminal".equals(name));',
                'require("before".equals(name) || "place".equals(name) || "terminal".equals(name));')
            text=once(text,'for(var unit:dev.codex.schubert.nk.batch.platform.MaintenanceUnit.values()){phase="OWNED_STOP_"+unit.name();refs.check("stop:"+unit.serviceName());}',
                'phase="SIGNED_UNUSED_PLACEMENT";refs.check("place");')
            text=text.replace('allEightOwnedTerminal=true','unusedCandidatePlaced=true').replace('starts0=true','startsStopsReloadsEpochWrites0=true')
        elif name=='Pg1293NativeArgumentTest.java':
            text=text.replace('new String[]{"stop","foreign"}','new String[]{"place","foreign"}')
        elif name=='pg1293_native_owned_stop.py':
            tree=ast.parse(text)
            # Retain only the current parent FLOCK/argv/PID identity and kernel
            # readback functions. No service mutation capability is transported.
            remove={'validate_live','same_generation','normal_terminal','broker_witness','save','parent_receipt','stop_one','main','show','command'}
            tree.body=[n for n in tree.body if not(isinstance(n,ast.FunctionDef)and n.name in remove)and not isinstance(n,(ast.If,ast.ImportFrom))and not(isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id in {'ORDER','EXPECTED'}for v in n.targets))]
            tree.body[0]=ast.Expr(value=ast.Constant('SS343 completed-DONE unused placement: current parent argv/FLOCK and ten kernel readback only. No service mutations or historical live PID assumptions.'))
            text=ast.unparse(tree)+'\n';text=text.replace("b'stop'","b'place'")
            text=once(text,"require(argv[-3:] == [b'Pg1293UnusedStage', b'place', b''] and argv[0] == b'/opt/jdk-25.0.4/bin/java')",'require(placement_family(argv))')
            text+=PURE_PROTOCOL
        elif name=='pg1293_native_refs.py':
            text=once(text,"sys.argv[1]=='stop'","sys.argv[1]=='place'")
            text=text.replace('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/fresh-completed-capture-v3/before.private.json',BASELINE)
            text=text.replace('28801629bec559edc757ef5df9c50b66fc524d898c1bca0a34f6015dd15f7218',BASELINE_SHA)
            text=once(text,"durable=json.loads(original)['durable']","durable=json.loads(original)['extraDurable']")
            text=once(text,"files=json.loads(original)['unitFiles']","files=json.loads(original)['unitFilesActual']")
            first=text.index(' def check_data(now):');last=text.index(" print('REF_READY',flush=True)",first)
            text=text[:first]+CHECK_DATA_AND_BASELINE+text[last:]
            first=text.index(' for line in sys.stdin.buffer:');last=text.index(" raise ValueError('readonly owner channel ended')",first)
            text=text[:first]+ACTION_LOOP+text[last:]
            text=text.replace("stages=[];captures=None;first=None","placed=False;first=None")
            # Insert a closed archive routine within the same reference lifetime.
            marker=" print('REF_READY',flush=True)"
            routine=stage_body();routine=routine[:routine.rindex('place_candidate()')]
            text=once(text,marker,''.join(' '+line+'\n'for line in routine.splitlines())+marker)
            ast.parse(text)
        text=text.replace('pg1293-native-stop-v1','pg1293-unused-stage-v1')
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result


CHECK_DATA_AND_BASELINE=r'''
 def check_data(now):
  require(first is not None and same_value(now,first))
  for u in UNITS:require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)
 first=capture_data(True);require(first==capture_data(True));save('before.private.json',first)
 baseline=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1253-native-stop-v1/after.private.json').read_bytes()
 require(hashlib.sha256(baseline).hexdigest()==BASELINE_SHA)
 prior=json.loads(baseline);require(set(prior)==set(first)and same_value(first,prior))
 for u in UNITS:require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)
'''
# save() is a private immutable receipt writer, not a business/release authority.
CHECK_DATA_AND_BASELINE=CHECK_DATA_AND_BASELINE.replace(" first=capture_data(True)"," def save(name,v):\n  durable_save(SAVE,name,json.dumps(v,sort_keys=True).encode())\n first=capture_data(True)")

ACTION_LOOP=r'''
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii');h.placement_action(action,placed)
  check_data(capture_data(action!='release'))
  if action=='place':
   require(not placed);place_candidate();placed=True;check_data(capture_data(True))
  if action in ['terminal','release']:require(placed)
  if action=='release':
   save('after.private.json',capture_data(False))
   for i,raw_journal in enumerate(JOURNAL_READS):durable_save(SAVE,'parent-journal-read-'+str(i)+'.private.jsonl',raw_journal)
   for u in reversed(refs):manager.UnrefUnit(u)
   bus.close();print('REF_RELEASED',flush=True);return
  print('REF_CHECKED',flush=True)
'''

PURE_PROTOCOL=r'''
def placement_family(argv):
 if type(argv)is not list or len(argv)<4 or any(type(v)is not bytes for v in argv):return False
 return argv[-3:]==[b'Pg1293UnusedStage',b'place',b'']and argv[0]==b'/opt/jdk-25.0.4/bin/java'
def placement_action(action,placed):
 require(type(action)is str and type(placed)is bool and action in ['before','place','terminal','release'])
 if action=='place':require(not placed)
 if action in ['terminal','release']:require(placed)
 return True
'''
