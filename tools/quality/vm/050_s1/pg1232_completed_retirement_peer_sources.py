"""New unused slots and actual retire peer argv closure after BUG1064."""
from pg1224_completed_runtime_sources import generated as previous

def generated():
    values={n.replace('1224','1232'):v.replace('Pg1224','Pg1232').replace('PG1224','PG1232').replace('pg1224','pg1232')for n,v in previous().items()}
    n='pg1232_native_owned_stop.py';old="[b'Pg1232NativeStop',b'stop',b'']"
    if values[n].count(old)!=1:raise ValueError('fixed actual peer action insertion rejected')
    values[n]=values[n].replace(old,"[b'Pg1232NativeStop',b'retire',b'']")
    for n,v in values.items():
        if n.endswith('.py'):compile(v,'<actual retire peer '+n+'>','exec')
    return values
