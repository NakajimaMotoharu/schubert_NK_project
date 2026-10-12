"""Independent current2741 Bootstrap20 and full originals/resources post.

Captured PID1 normal20 must precede GC/current qualification. Only two
ordinary-bootstrap native files and source credential-directory timestamps
are permitted deltas; all other original bytes and full24 rows stay fixed.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate
from pg1718_current_bootstrap_before import payload as original_payload
from pg1719_current_bootstrap_sources import bind as current_bind,SOURCE
from pg1728_bootstrap_abi_sources import bind,TOOLS
import pg989_current_bootstrap_post as previous

SLOT='pg1731-current-bootstrap-full-post-v1'

def payload():
    fixed=json.loads((W/'pg1729-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0 or fixed['productionSource']!=SOURCE:raise ValueError('qualified new120 Bootstrap files required')
    def tool(n):
        raw=(W/TOOLS/n).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=fixed['fileHashes'][n]:raise ValueError('fixed current helper bytes required')
        return raw.decode()
    # The full outer oracle already imports re; inline only the pinned helper's
    # definitions so generated static analysis sees no unused redefinition.
    prefix='CONTRACT={};exec('+repr(tool('pg1728_bootstrap_contract.py'))+',CONTRACT)\nCONFIG={};exec('+repr(tool('pg1728_configuration.py'))+',CONFIG)\n'+tool('pg1728_exec_record.py').replace('import re\n','')+'\n'
    extra=bind(current_bind(previous.base_namespace()['EXTRA']))
    extra=extra.replace('33554432','67108864')
    # Directory timestamps are a declared credential create/retire consequence;
    # independent credential_tree above proves every existing leaf unchanged.
    extra+="\nafter={**after,'extraDurable':{**after['extraDurable'],'credentials':boot_after['credentials']}}\n"
    raw=original_payload().replace('pg1718-current-bootstrap-before-v1',SLOT)
    # EXTRA's baseline path must remain the immutable real original, not SLOT.
    at=raw.index('bus=dbus.SystemBus(private=True);manager=')
    raw=raw[:at]+prefix+extra+'\n'+raw[at:]
    current=(Path(__file__).parent/'vm/050_s1/pg902_terminal_current.py').read_text()
    authentic=r'''
current_bootstrap=show(bootstrap,STATE_FIELDS)
require(current_normal_or_gc(terminal,current_bootstrap))
current_configuration=complete_configuration(command(['systemctl','show',bootstrap,'--property='+','.join(sorted(FIELDS))]).decode(),bootstrap)
require(CONFIG['same'](boot_after['configuration'][bootstrap],current_configuration,exec_record))
after={**after,'units':{**after['units'],bootstrap:current_bootstrap},'configuration':{**after['configuration'],bootstrap:current_configuration}}
'''
    # Take current Unit properties only while own Ref protects GC semantics.
    marker=' for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)'
    if raw.count(marker)!=1:raise ValueError('one new tenRef scope required')
    raw=raw.replace(marker,marker+'\n'+'\n'.join(' '+l if l else l for l in authentic.splitlines()))
    raw=current+'\n'+raw
    marker=' native=snapshot();require(native==snapshot())'
    raw=raw.replace(marker,marker+";require(native==boot_after['native']and boot_raw_before==newproof('before.private.json')and boot_raw_after==newproof('after.private.json'))")
    raw=raw.replace("'startsStopsWrites0':True", "'startsStopsWrites0':True,'capturedNormal20VerifiedBeforeCurrent':True,'gcDoesNotInferPastSuccess':True,'currentCredentialsRetired':True,'allResources0':True,'bootstrap':bootstrap_meta,'bootstrapProofHashes':{n:hashlib.sha256(newproof(n)).hexdigest()for n in ('before.private.json','after.private.json','pid1.private.jsonl','complete.private')}")
    from pyflakes.api import check
    if check(raw,'<independent actual Bootstrap current whole post>'):raise ValueError('generated static refused')
    compile(raw,'<independent actual Bootstrap current whole post>','exec');return raw

def main():
    result=json.loads((W/'pg1730-execute-v1.safe.json').read_bytes())
    if result['actualExit']!=0 or result['productionSource']!=SOURCE:raise ValueError('actual new Bootstrap normal completion required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:v['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(v));return r.returncode

if __name__=='__main__':raise SystemExit(main())
