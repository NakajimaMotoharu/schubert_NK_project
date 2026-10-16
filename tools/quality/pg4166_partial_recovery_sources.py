"""SSC288 new-only controller/post, deriving exact historical bytes without hotpatching5fdb/a89c."""
import ast
import hashlib
import inspect
from pg1446_current_cold_stage import W
from pg4060_original_profile_dual_stack import once
import pg4162_configuration_declarations as declarations
import pg4178_pool_bounds as pool

SLOT='pg4184-partial-owned-recovery-v1'
POST='pg4186-partial-independent-post-v1'


def archived(relative,digest):
    raw=(W/relative).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('unchanged qualified predecessor required')
    return raw.decode()


def inject_declarations(raw):
    raw='DECLARATION_SOURCE='+repr(inspect.getsource(declarations))+'\n'+raw
    marker='def config():\n'
    raw=once(raw,marker,"declaration_contract={};exec(DECLARATION_SOURCE,declaration_contract)\n"+marker)
    replacement="declaration_contract['same_configurations'](fixed_config,config(),CONFIG_CONTRACT['same'],exec_record)"
    count=raw.count('config()==fixed_config')
    if count not in (1,2):raise ValueError('all exact configuration boundaries required')
    return raw.replace('config()==fixed_config',replacement)


def controller():
    raw=archived('pg4144-complete-signed-dispatch-qualification-v1-artifact/dispatch.private.py','5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3')
    raw=once(raw,"save=base/('pg4146-complete-signed-owned-recovery-v1-'+MODE)","save=base/('"+SLOT+"-'+MODE)")
    raw=once(raw,"EXPECTED_ACTORS=actor_certificate['second']['actors']","EXPECTED_ACTORS={u:a for u,a in actor_certificate['second']['actors'].items()if u!='caddy.service'}")
    old="captures={unit:show_terminal(unit)for unit in ORDER};durable_save('before.private.json',encode(baseline));durable_save('terminal-before.private.json',encode(captures))"
    new="captures={unit:show_terminal(unit)for unit in ORDER}\n caddy_reference=Path('/var/lib/pgpt-s1-preservation/pg4160-retained-config-read-v1/observed.private.json').read_bytes();require(hashlib.sha256(caddy_reference).hexdigest()=='e5fff095e3d770b128150029cefa2b3c501462d1e4f5b41279b5d80500be0d0b');prior_caddy=json.loads(caddy_reference)['caddyBefore']\n require(terminal_contract.normal_terminal(prior_caddy,captures['caddy.service']));terminal_contract.kernel_empty('caddy.service');require(not Path('/proc/761848').exists());captures['caddy.service']=prior_caddy\n durable_save('before.private.json',encode(baseline));durable_save('terminal-before.private.json',encode(captures))"
    raw=once(raw,old,new)
    old=" def reserve(unit):durable_save(unit+'.stop-reserved.private',encode({'unit':unit,'before':captures[unit],'holderPid':owned[0],'holderTicks':holder_ticks}))"
    new=" def reserve(unit):\n  name=unit+('.prior-terminal-observed.private'if unit=='caddy.service'else'.stop-reserved.private')\n  durable_save(name,encode({'unit':unit,'before':captures[unit],'holderPid':owned[0],'holderTicks':holder_ticks,'newStopPermitted':unit!='caddy.service'}))"
    raw=once(raw,old,new)
    raw=once(raw," def stop(unit):\n  require(show_terminal(unit)==captures[unit]);holder()",
      " def stop(unit):\n  if unit=='caddy.service':\n   require(terminal_contract.normal_terminal(captures[unit],show_terminal(unit)));terminal_contract.kernel_empty(unit);require(not Path('/proc/761848').exists());holder();return\n  require(show_terminal(unit)==captures[unit]);holder()")
    raw=once(raw,"print('SSC287_STOPPED unit='+unit+' generationVerified=true',flush=True)","print('SSC288_TERMINAL unit='+unit+' issued='+str(unit!='caddy.service').lower()+' generationVerified=true',flush=True)")
    raw=once(raw,"'recoverySixNormal':MODE=='recover'","'recoverySixNormal':MODE=='recover','caddyPriorStopAuthenticated':True,'newStopCount':5 if MODE=='recover'else 0,'old4152Normal':False")
    raw=inject_declarations(raw)
    raw='POOL_SOURCE='+repr(inspect.getsource(pool))+'\n'+raw
    raw=once(raw,'def peer_check(value,held):',"pool_contract={};exec(POOL_SOURCE,pool_contract)\ndef peer_check(value,held):")
    raw=once(raw,"expected={k:(0 if u in completed_units else count)for k,(u,count)in roles.items()};counts={k:0 for k in roles}","counts={k:0 for k in roles}")
    raw=once(raw,"actual=value['database']['peers'];require(len(actual)==sum(expected.values())+(1 if held else 0))","actual=value['database']['peers']")
    raw=once(raw,' require(counts==expected)'," require(pool_contract['counts_valid'](counts,set(completed_units)&{u for u,n in roles.values()},1 if held else 0,len(actual))is True)")
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='peer_check')
    old_check=ast.get_source_segment(raw,node)
    new_check=once(old_check,"require(row['user']in roles);unit,_=roles[row['user']];counts[row['user']]+=1;pid=value['actors'][unit]['pid']",
                  "require(row['user']in roles);unit,_=roles[row['user']];require(unit not in completed_units and row['application']==('schubert-nk-api'if unit=='schubert-nk-api.service'else'schubert-nk-web'));counts[row['user']]+=1;pid=value['actors'][unit]['pid']")
    raw=once(raw,old_check,new_check)
    raw=once(raw,'import time,sys','import time,sys,traceback')
    raw=once(raw,'except BaseException:\n # If a child/scope ever existed',
       "except BaseException as failure:\n try:durable_save('failure.private.json',encode({'type':type(failure).__name__,'frames':[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}for t in traceback.extract_tb(failure.__traceback__)]}))\n except OSError:print('FAILURE_CAPTURE_UNAVAILABLE oldScopeStillUnknown=true',flush=True)\n # If a child/scope ever existed")
    compile(raw,'<new partial controller>','exec');return raw


def post():
    raw=archived('pg4150-failed-done-post-artifact-v1/post.private.py','a89c7dfa784be50951614441b1fa674125d7f3dde32b79cffef5ebaea88361ad')
    raw=once(raw,"save=base/'pg4148-failed-done-independent-post-v1'","save=base/'"+POST+"'")
    raw=once(raw,"RECOVERY='/var/lib/pgpt-s1-preservation/pg4146-complete-signed-owned-recovery-v1-recover'","RECOVERY='/var/lib/pgpt-s1-preservation/"+SLOT+"-recover'")
    raw=once(raw,"before['actors']==reference['actors']","before['actors']=={u:a for u,a in reference['actors'].items()if u!='caddy.service'}")
    raw=inject_declarations(raw)
    compile(raw,'<new partial independent post>','exec');return raw
