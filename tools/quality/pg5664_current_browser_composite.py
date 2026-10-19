"""Current0ea Root→strict guest-clock Browser→all24; no historical failed effects."""
import ast
import inspect
import types
import pg5050_current_browser_composite as previous
import pg5644_current_admission_image as admission
import pg5650_current_newday_whole_seal as root
import pg5662_current_same_owner_browser as actual
import pg5520_guest_clock_contract as clock
from pg2025_fresh_resume_full_live_seal import constant

SLOT='pg5664-current-browser-composite-v1'


def literal(raw,name):
    return next(ast.literal_eval(n.value)for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))


def compose(raw,chain,digest):
    clock.verify_context(chain['context'])
    ns={**vars(previous),'admission':admission,'root':root,'SLOT':SLOT}
    base=types.FunctionType(previous.compose.__code__,ns)(raw,chain,digest)
    oracle=literal(base,'ORACLE')
    helper='import datetime\nDOMAIN='+repr(clock.DOMAIN)+'\nSOURCE='+repr(clock.SOURCE)+'\n'+inspect.getsource(clock.instant)+'\n'+inspect.getsource(clock.verify_context)
    target="context=CHAIN['context'];a=datetime.datetime.fromisoformat"
    if oracle.count(target)!=1:raise ValueError('one new Browser captured clock boundary')
    replacement="context=CHAIN['context'];clock_ns={};exec(compile("+repr(helper)+",'<strict guest clock>','exec'),clock_ns);clock_ns['verify_context'](context);a=datetime.datetime.fromisoformat"
    oracle=oracle.replace(target,replacement,1)
    result=constant(base,'ORACLE',oracle)
    if literal(result,'GUARD')!=literal(raw,'GUARD')or literal(oracle,'ROOT_ORACLE')!=literal(raw,'ORACLE')or literal(oracle,'CHAIN')!=chain:
        raise ValueError('immutable Root oracle/guard/captured Browser chain')
    return result


def payload(observed):
    ns={**vars(previous),'admission':admission,'root':root,'actual':actual,'compose':compose}
    return types.FunctionType(previous.payload.__code__,ns)(observed)


def main():
    ns={**vars(previous),'admission':admission,'SLOT':SLOT,'payload':payload}
    return types.FunctionType(previous.main.__code__,ns)()


if __name__=='__main__':raise SystemExit(main())
