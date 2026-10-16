"""SSC300 independent captured20/all24/187/resources post; GC never supplies success."""
import ast
import hashlib
import json
from pathlib import Path
from pyflakes.api import check
import pg4820_new_current_bootstrap_sources as role
import pg4826_new_current_bootstrap_dispatch as dispatch
import pg989_current_bootstrap_post as old

SLOT='pg4828-new-current-bootstrap-post-v1'


def payload():
    fixed,target=dispatch.fixed()
    actual=json.loads((role.W/(dispatch.SLOT+'-execute-v1.safe.json')).read_bytes())
    if not(type(actual['actualExit'])is int and actual['actualExit']==0 and actual['productionSource']==role.SOURCE and actual['operatorUnchanged']):raise ValueError('actual new execute normal scopes first')
    raw=(role.W/role.before.SLOT/'payload.private.py').read_text()
    manifest=json.loads((role.W/role.before.SLOT/'manifest.safe.json').read_bytes())
    if hashlib.sha256(raw.encode()).hexdigest()!=manifest['payloadSha256']:raise ValueError('exact actual4818 source first')
    def tool(name):
        value=(target/name).read_bytes()
        if hashlib.sha256(value).hexdigest()!=fixed['fileHashes'][name]:raise ValueError('exact frozen current helper')
        return value.decode()
    prefix='CONTRACT={};exec('+repr(tool('pg4820_bootstrap_contract.py'))+',CONTRACT)\nCONFIG={};exec('+repr(tool('pg4820_configuration.py'))+',CONFIG)\n'+tool('pg4820_exec_record.py').replace('import re\n','')+'\n'
    extra=role.current_text(role.template.bind(old.base_namespace()['EXTRA'])).replace('33554432','67108864')
    extra=extra.replace("baseline895=json.loads(strict(base/'"+role.before.SLOT+"/after.private.json',0o600,67108864))", "baseline_raw=strict(base/'"+role.before.SLOT+"/after.private.json',0o600,67108864);require(hashlib.sha256(baseline_raw).hexdigest()=="+repr(role.BASELINE)+");baseline895=json.loads(baseline_raw)")
    extra+="\nafter={**after,'extraDurable':{**after['extraDurable'],'credentials':boot_after['credentials']}}\n"
    buses=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bus'for t in n.targets)]
    if len(buses)!=1:raise ValueError('one actual held metadata scope')
    lines=raw.splitlines(keepends=True);lines.insert(buses[0].lineno-1,prefix+extra+'\n');raw=''.join(lines)
    current=(Path(old.__file__).parent/'pg902_terminal_current.py').read_text()
    authentic="""
current_bootstrap=show(bootstrap,STATE_FIELDS)
require(current_normal_or_gc(terminal,current_bootstrap))
current_configuration=complete_configuration(command(['systemctl','show',bootstrap,'--property='+','.join(sorted(FIELDS))]).decode(),bootstrap)
require(CONFIG['same'](boot_after['configuration'][bootstrap],current_configuration,exec_record))
after={**after,'units':{**after['units'],bootstrap:current_bootstrap},'configuration':{**after['configuration'],bootstrap:current_configuration}}
"""
    marker='        refs.append(u)'
    if raw.count(marker)!=1:raise ValueError('one held tenRef scope')
    raw=raw.replace(marker,marker+'\n'+'\n'.join('    '+line if line else line for line in authentic.splitlines()),1)
    raw=current+'\n'+raw
    marker='    require(native == snapshot())'
    if raw.count(marker)!=1:raise ValueError('one stable whole snapshot')
    raw=raw.replace(marker,marker+"\n    require(native==boot_after['native']and boot_raw_before==newproof('before.private.json')and boot_raw_after==newproof('after.private.json'))")
    marker="save=base/"+repr(role.before.SLOT)
    if raw.count(marker)!=1:raise ValueError('one new post output only')
    raw=raw.replace(marker,"save=base/"+repr(SLOT),1)
    raw=raw.replace("'startsStopsWrites0':True", "'startsStopsWrites0':True,'capturedNormal20VerifiedBeforeCurrent':True,'gcDoesNotInferPastSuccess':True,'currentCredentialsRetired':True,'allResources0':True,'bootstrap':bootstrap_meta,'bootstrapProofHashes':{n:hashlib.sha256(newproof(n)).hexdigest()for n in ('before.private.json','after.private.json','pid1.private.jsonl','complete.private')}")
    if check(raw,'<current Bootstrap normal20 independent full post>'):raise ValueError('complete emitted static0 required')
    compile(raw,'<actual captured20 then current whole>','exec');return raw


if __name__=='__main__':raise SystemExit(role.before.admission.execute(SLOT,payload(),120))
