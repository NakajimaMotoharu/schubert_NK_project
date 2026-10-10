"""New immutable corrected UTC closure; old143 never reused, actual18 oracle."""
import inspect
import pg1250_fresh_owned_stop_dispatch as previous

def source():
    s=inspect.getsource(previous)
    s=s.replace('from pg1247_fresh_owned_stop_sources import','from pg1253_fresh_owned_stop_sources_v2 import')
    for old,new in [('Pg1247','Pg1253'),('pg1247','pg1253'),('pg1250','pg1256'),('PG1250','PG1256'),('pg1248','pg1254'),('pg1249-fresh-stop-preflight-v1','pg1255-fresh-stop-preflight-v2')]:s=s.replace(old,new)
    s=s.replace("'Pg1253StopLabelTest','Pg1253NativeArgumentTest','Pg1253NativeStop stop'","'Pg1253OriginalTupleTest','Pg1253StopLabelTest','Pg1253NativeArgumentTest','Pg1253NativeStop stop'")
    compile(s,'<actual whole new corrected stop dispatcher>','exec');return s

def main():
    recovered=previous.json.loads((previous.W/'pg1252-fresh-stop-fixed-handoff-v1.safe.json').read_bytes())
    if recovered['actualExit']!=0 or not recovered['oldMgmtPeerAdvisoryFlocks0']:raise ValueError('actual old management recovery required')
    env={'__name__':'actual_fresh_stop_v2_dispatch','__file__':__file__}
    exec(compile(source(),'<fixed new stop full namespace>', 'exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
