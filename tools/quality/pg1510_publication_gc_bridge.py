"""SSC268 data-only warm stop/current strictGC bridge. GC alone proves no stop or authority."""
import copy

ORDER=('schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-cleanup.service')
FIELDS=set('Id LoadState ActiveState SubState Job MainPID ControlPID InvocationID Type Restart RemainAfterExit Result ExecMainCode ExecMainStatus ExecMainStartTimestampMonotonic ExecMainExitTimestampMonotonic KillMode SendSIGKILL'.split())
GC={'InvocationID':'','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'0','ExecMainExitTimestampMonotonic':'0'}

def require(v):
    if not v:raise ValueError('strict publication GC bridge refused')

def unit_kind(warm,current):
    require(type(warm)is dict and type(current)is dict and set(warm)==set(current)==FIELDS and all(type(v)is str for v in [*warm.values(),*current.values()]))
    require(warm['Id']in ORDER and warm['ActiveState']=='inactive'and warm['SubState']=='dead'and warm['Result']=='success'and warm['MainPID']==warm['ControlPID']=='0'and warm['Job']=='' and len(warm['InvocationID'])==32 and int(warm['ExecMainStartTimestampMonotonic'])>0)
    if current==warm:return 'WARM'
    require(all(current[k]==v for k,v in GC.items())and all(current[k]==warm[k]for k in FIELDS-set(GC)))
    return 'STRICT_GC'

def configuration(warm,current,parse,kind):
    require(type(warm)is dict and type(current)is dict and len(warm)==32 and set(warm)==set(current)and all(type(v)is str for v in [*warm.values(),*current.values()])and callable(parse))
    if kind=='WARM':require(current==warm);return
    require(kind=='STRICT_GC'and all(current[k]==warm[k]for k in warm if k!='ExecStart'))
    a=parse(warm.get('ExecStart'));b=parse(current.get('ExecStart'))
    require(a is not None and b is not None and a[:3]==b[:3]and b[3:]==('n/a','n/a','0','(null)','0/0'))

def normalize(expected,actual,parse):
    require(type(expected)is dict and type(actual)is dict and set(expected)==set(actual))
    result=copy.deepcopy(actual);kinds={}
    for name in ORDER:
        kind=unit_kind(expected['units'][name],actual['units'][name]);kinds[name]=kind
        configuration(expected['configuration'][name],actual['configuration'][name],parse,kind)
        result['units'][name]=copy.deepcopy(expected['units'][name]);result['configuration'][name]=copy.deepcopy(expected['configuration'][name])
    require(result==expected)
    return result,kinds
