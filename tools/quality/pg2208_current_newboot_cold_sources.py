"""SS343/SSC264 current completed WARNING cold finite preparation; no start/epoch.

PT-OPS-2208-001. New current proof rather than old boot/PID/run acceptance.
"""
import json
import ast
from pg1446_current_cold_stage import W
import pg1441_current_cold_sources as old_java
import pg1441_current_cold_refs as old_refs
from pg2206_outage_cold_reauthentication_v2 import payload as cold_payload
from pg2176_newsource_normal_observer import SOURCE,BOM

TOOLS='pg2208-current-newboot-cold-tools-v1'
PREPARED='pg2212-current-newboot-cold-prepared-v1'
BOOT='b2d6f605-61cf-425f-8fbd-12d606f6ee66'
SIG='7ef03cf927c2f5b79b39a5d5187db439c753c57933bfff18b26386a02afaf449'


def bindings(raw):
    for old,new in [('Pg1441CurrentColdPreparation','Pg2208CurrentColdPreparation'),
        ('pg1441-current-cold-tools-v1',TOOLS),('pg1441-current-cold-prepared-v1',PREPARED),
        ('pg1441_current_cold_refs.py','pg2208_current_cold_refs.py'),('PG1441_','PG2212_'),
        ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),
        ('d2e3a86f-27a4-4c2a-be21-b512eebf1216','02bddddf-9cd3-4668-9d67-7561232fc4e4'),
        ('841b507c-2713-4ffe-8882-68f5fb3f87f5','20b86040-ffd5-4d17-9fca-5d83048ba905'),
        ('2026-10-10T23:30:23.481632Z','2026-10-13T06:29:34.698736Z'),
        ('2026-10-10T23:54:39.918039Z','2026-10-13T06:56:23.969590Z'),
        ('PG1292','PG2126'),('pg1292','pg2126'),
        ('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE),
        ('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM),
        ('97fd4c41a795c5f2465cf2f5074831723db0c3942fa8d62d16a5aad54cb318f7',SIG)]:raw=raw.replace(old,new)
    return raw


def qualify_before():
    v=json.loads((W/'pg2206-outage-cold-reauthentication-v2/manifest.safe.json').read_bytes())
    if v['actualExit']!=0 or v['boot']!=BOOT or v['source']!=SOURCE or not v['newBootTenColdTwice'] or not v['allDurableUnchanged']:
        raise ValueError('actual whole newboot cold proof required')


def java():
    raw=bindings(old_java.java())
    old='done.outcome()==MaintenanceCompletion.Outcome.SUCCESS'
    if raw.count(old)!=1:raise ValueError('one completed current outcome required')
    return raw.replace(old,'done.outcome()==MaintenanceCompletion.Outcome.WARNING')


def observer():
    # Prefix and complete observe function are already qualified against this
    # exact current source. Keep durable/data/signature assertions unchanged.
    raw=cold_payload();point=raw.index('bus=dbus.SystemBus(private=True);manager=')
    prefix=raw[:point]
    prefix=prefix.replace('hashlib,re,dbus\n','hashlib,re\n')
    syntax=ast.parse(prefix)
    observe=next(n for n in syntax.body if isinstance(n,ast.FunctionDef) and n.name=='observe')
    peers=next(n for n in observe.body if isinstance(n,ast.Assign) and any(isinstance(q,ast.Name) and q.id=='peers' for q in n.targets))
    prefix=prefix.replace(' '+ast.get_source_segment(prefix,peers)+'\n','')
    prefix=prefix.replace("require(peers.splitlines()==[b'0',b'0'])",'peer_check()')
    old=" for name in ['startup','pt-coverage','backup-request','cleanup-request','expiry-request']:\n  require(not os.path.lexists('/run/schubert-nk/'+name))"
    if prefix.count(old)!=1:raise ValueError('one finite runtime boundary required')
    prefix=prefix.replace(old,' runtime_check()')
    # The maintenance inode remains unchanged; new children affect only its
    # parent's finite entry count, whose complete old/new vectors BODY checks.
    prefix+='\nBOOT='+repr(BOOT)+'\nrequire(boot==BOOT)\nsnapshot=observe\n'
    old_source=old_refs.source();tree=ast.parse(old_source)
    constants=[]
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'INVENTORY_SOURCE','LOCK_SOURCE'} for t in n.targets):
            constants.append(ast.get_source_segment(old_source,n))
    if len(constants)!=2:raise ValueError('current ownership/FD closure sources required')
    result='\n'.join(constants)+'\n'+prefix+'\n'+bindings(old_refs.BODY)
    from pyflakes.api import check
    if check(result,'<whole newboot current Ref graph>'):raise ValueError('whole actual current Ref namespace required')
    compile(result,'<newboot current Ref graph>','exec');return result


def main():
    qualify_before();print('PG2208_SOURCE_ONLY',len(java()),len(observer()))


if __name__=='__main__':main()
