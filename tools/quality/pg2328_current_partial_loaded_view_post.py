"""GC/LoadUnit partial view is an exact declared delta, not a normal reload receipt."""
import types
from pyflakes.api import check
import pg2326_current_partial_runtime_recovery_post as prior
from pg870_ordinary_before import parser_source

SLOT='pg2328-current-partial-loaded-view-post-v1'


def admitted_configuration(old,new,parse):
    if type(old)is not dict or type(new)is not dict or set(old)!=set(new):return False
    morning='schubert-nk-morning-controller.service'
    for unit,before in old.items():
        after=new[unit]
        if type(before)is not dict or type(after)is not dict or set(before)!=set(after)or len(before)!=32:return False
        if any(type(v)is not str for v in [*before.values(),*after.values()]):return False
        if unit!=morning:
            if after!=before:return False
            continue
        if any(before[k]!=after[k]for k in before if k not in {'ExecStart','DropInPaths'}):return False
        left= parse(before['ExecStart']);right=parse(after['ExecStart'])
        if left is None or right is None or len(left)!=8 or len(right)!=8:return False
        if right[:3]!=(left[0],left[1]+' --resume 91f5484b-9702-4c7c-97f3-dd5110a853f9',left[2]):return False
        if tuple(right[3:])!=('n/a','n/a','0','(null)','0/0'):return False
        if after['DropInPaths']!=before['DropInPaths']+' /run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf':return False
    return morning in old


def payload():
    import inspect
    raw=prior.payload().replace(prior.SLOT,SLOT)
    raw=parser_source()+'\n'+inspect.getsource(admitted_configuration)+'\n'+raw
    marker='\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker)!=1:raise ValueError('one complete held reference scope required')
    raw=raw.replace(marker,'\ncurrent_view={}\n'+marker)
    old="            require(complete_configuration(command(['systemctl', 'show', u, '--property=' + ','.join(sorted(FIELDS))]).decode(), u) == after['configuration'][u])"
    if raw.count(old)!=1:raise ValueError('one exact old config equality boundary required')
    raw=raw.replace(old,"            current_view[u]=complete_configuration(command(['systemctl','show',u,'--property='+','.join(sorted(FIELDS))]).decode(),u)")
    marker="        for k, p in [('startup', '/run/schubert-nk/startup')"
    point=raw.index(marker)
    raw=raw[:point]+"        require(admitted_configuration(after['configuration'],current_view,exec_record))\n"+raw[point:]
    raw=raw.replace("value={'before':after,","value={'before':{**after,'configuration':dict(current_view)},")
    raw=raw.replace("'exactPartialRuntimeRetained':True","'exactPartialRuntimeRetained':True,'partialLoadedConfigDeltaOnly':True,'normalReloadAccepted':False")
    if check(raw,'<whole current partial loadedview>'):raise ValueError('all current view globals required')
    compile(raw,'<exact partial loaded current configuration>','exec');return raw


def main():
    fn=types.FunctionType(prior.main.__code__,{**prior.__dict__,'SLOT':SLOT,'payload':payload},'current_partial_loadedview_post')
    return fn()


if __name__=='__main__':raise SystemExit(main())
