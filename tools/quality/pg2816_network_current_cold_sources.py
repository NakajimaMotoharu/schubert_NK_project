"""SSC264 finite newboot source042 preparation; existing original DONE is data, not old authority."""
import ast
import inspect
import json
from pyflakes.api import check
import pg2208_current_newboot_cold_sources as historical
import pg1441_current_cold_refs as refs
from pg2814_network_newboot_readonly import payload as cold_payload,BOOT,SOURCE,BOM,one
from pg1446_current_cold_stage import W

TOOLS='pg2816-network-current-cold-tools-v1'
PREPARED='pg2822-network-current-cold-prepared-v1'
CLASS='Pg2816NetworkCurrentColdPreparation'
SIG='e22919d29b823bb7224887a9d136c77fecd62b8b1a3d663abf6915b9408ea2cd'
DONE_SHA='8c2b9f315cb284cbaba2bc6b9d9b7db1098d6370db3a37ce17bff7f07bde1ef0'


def bindings(raw):
    for a,b in [('Pg2208CurrentColdPreparation',CLASS),(historical.TOOLS,TOOLS),(historical.PREPARED,PREPARED),
      ('pg2208_current_cold_refs.py','pg2816_network_current_cold_refs.py'),('PG2212_','PG2822_'),
      (historical.BOOT,BOOT),(historical.SOURCE,SOURCE),(historical.BOM,BOM),(historical.SIG,SIG),
      ('PG2126','PG2654'),('pg2126','pg2654'),
      ('02bddddf-9cd3-4668-9d67-7561232fc4e4','77601cf8-0ade-40fd-813f-c81d5210845e'),
      ('20b86040-ffd5-4d17-9fca-5d83048ba905','26250063-8755-43b6-9ac7-f76d5eee7257'),
      ('2026-10-13T06:29:34.698736Z','2026-10-14T06:56:07.778154Z'),
      ('2026-10-13T06:56:23.969590Z','2026-10-14T07:24:35.698243Z')]:raw=raw.replace(a,b)
    return raw


def qualify_before():
    v=json.loads((W/'pg2814-network-newboot-readonly-v2/manifest.safe.json').read_bytes())
    expected={'actualExit':0,'boot':BOOT,'source':SOURCE,'tables':24,'signedArtifacts':187,
        'allDurableUnchanged':True,'newBootTenColdTwice':True,'metadataRefsClosed':True,
        'oldRunPermitNativeRestored':False,'newLocksNoFlockTwice':True}
    if any(type(v.get(k))is not type(x)or v[k]!=x for k,x in expected.items()):raise ValueError('actual current newboot complete read-only proof required')


def java():
    return bindings(historical.java())


def observer():
    raw=cold_payload();prefix=raw[:raw.index('bus=dbus.SystemBus(private=True);manager=')]
    prefix=prefix.replace('hashlib,re,dbus\n','hashlib,re\n')
    syntax=ast.parse(prefix);observe=next(n for n in syntax.body if isinstance(n,ast.FunctionDef)and n.name=='observe')
    peer=next(n for n in observe.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='peers'for t in n.targets))
    prefix=one(prefix,' '+ast.get_source_segment(prefix,peer)+'\n','')
    prefix=one(prefix,"require(peers.splitlines()==[b'0',b'0'])",'peer_check()')
    old=" for name in ['startup','pt-coverage','backup-request','cleanup-request','expiry-request']:\n  require(not os.path.lexists('/run/schubert-nk/'+name))"
    prefix=one(prefix,old,' runtime_check()')
    # The Java parent now genuinely owns both locks; actor() below proves this exact PID/inode.
    # Keep metadata checks, replace only the incompatible no-holder test from the standalone proof.
    old="""  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
"""
    prefix=one(prefix,old,'')
    prefix+='\nBOOT='+repr(BOOT)+'\nrequire(boot==BOOT)\nsnapshot=observe\n'
    constants=[]
    for n in ast.parse(refs.source()).body:
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'INVENTORY_SOURCE','LOCK_SOURCE'}for t in n.targets):
            constants.append(ast.get_source_segment(refs.source(),n))
    if len(constants)!=2:raise ValueError('one independent held-inventory and lock contract required')
    body=historical.bindings(refs.BODY)
    result='\n'.join(constants)+'\n'+prefix+'\n'+bindings(body)
    if check(result,'<current042 whole finite newboot Ref graph>'):raise ValueError('complete newboot Ref namespace required')
    compile(result,'<newboot data/ownership and finite preparation>','exec');return result


if __name__=='__main__':raise SystemExit('factory only, no actual prepare')
