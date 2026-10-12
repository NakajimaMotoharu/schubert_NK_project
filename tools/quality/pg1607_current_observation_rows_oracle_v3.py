"""Root batch DONE bound is distinct from owned live Web observation bound."""
from pg1605_current_ordinary_rows_oracle_v2 import source as previous

def source():
    raw=previous()
    raw=raw.replace('def qualify(old,new,lower,upper):','def qualify(old,new,lower,done_end,observed_upper):')
    raw=raw.replace("result=after(old,new,run,lower,upper)","require(instant(lower)<=instant(done_end)<=instant(observed_upper));result=after(old,new,run,lower,observed_upper)")
    marker="    for row in added:\n"
    if raw.count(marker)!=1:raise ValueError('batch independent terminal-bound insertion refused')
    raw=raw.replace(marker,marker+"        require(instant(row['ended_at'])<=instant(done_end))\n")
    compile(raw,'<separate batch DONE/live Web bounds>','exec');return raw

def qualify(old,new,lower,done_end,observed_upper):
    env={};exec(compile(source(),'<independent observation bounds>','exec'),env)
    return env['qualify'](old,new,lower,done_end,observed_upper)
