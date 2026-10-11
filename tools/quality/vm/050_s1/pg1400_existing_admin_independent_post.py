"""Current-source normal20/closing, credential retirement and full protected post under Ref."""
import json
import pg1395_existing_role_normal_post as previous
import pg901_bootstrap_post as bootstrap
import pg1396_existing_admin_sources as admin
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

def payload(seals):
    raw=previous.payload(seals)
    generated=admin.files('37715c53df9f698f1d544233eb8582595b0f90121e583228f8402b92c37f1ac0')
    hashes=json.loads((W/'pg1396-frozen-v3.safe.json').read_bytes())['fileHashes']
    extra=bootstrap.EXTRA.replace('pg894-bootstrap-existing-v3','pg1396-bootstrap-existing-v3').replace('pg895-bootstrap-before-v1','pg1395-existing-role-normal-post-v1').replace('cc9ed8747f4f450ea1888de1e42c8441','cbca87383b244090b77cbf029677cdd6').replace('33554432','67108864')
    extra=extra.replace("after={**after,'units':boot_after['units'],'configuration':boot_after['configuration']}","after={**after,'units':boot_after['units'],'configuration':boot_after['configuration'],'extraDurable':{**after['extraDurable'],'credentials':boot_after['credentials']}}")
    prefix="old_after=after\nCONTRACT={};exec("+repr(generated['pg1396_bootstrap_contract.py'])+",CONTRACT)\nCONFIG={};exec("+repr(generated['pg1396_configuration.py'])+",CONFIG)\n"+generated['pg1396_exec_record.py']+'\n'+extra
    prefix+='\nADMIN_HASHES='+repr(hashes)+"\ntools=base/'pg1396-bootstrap-tools-v3'\nrequire({p.name for p in tools.iterdir()}==set(ADMIN_HASHES)|{'payload-sha256.json'})\nfor name,digest in ADMIN_HASHES.items():require(hashlib.sha256(strict(tools/name,0o400,67108864)).hexdigest()==digest)\n"
    marker='bus=dbus.SystemBus(private=True);'
    if raw.count(marker)!=1:raise ValueError('one whole current independent Ref scope required')
    raw=raw.replace(marker,prefix+'\n'+marker)
    current_code=(bootstrap.R/'pg902_terminal_current.py').read_text()
    marker=' for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)'
    if raw.count(marker)!=1:raise ValueError('current bootstrap observed only under all Ref')
    block=current_code+'''\ncurrent_bootstrap=show(bootstrap,STATE_FIELDS)
require(current_normal_or_gc(terminal,current_bootstrap))
current_configuration=complete_configuration(command(['systemctl','show',bootstrap,'--property='+','.join(sorted(FIELDS))]).decode(),bootstrap)
require(CONFIG['same'](boot_after['configuration'][bootstrap],current_configuration,exec_record))
after={**after,'units':{**after['units'],bootstrap:current_bootstrap},'configuration':{**after['configuration'],bootstrap:current_configuration}}
'''
    raw=raw.replace(marker,marker+'\n'+''.join(' '+line+'\n'for line in block.splitlines()))
    replacements=(
        ("initial['current']==prepared['current']==after", "initial['current']==prepared['current']==old_after"),
        ("and prepared['native']==native", "and prepared['native']==boot_before['native']"),
        ("role_policy.delta(initial['native'],native,", "role_policy.delta(initial['native'],boot_before['native'],"),
        ("recovered['current']==after and recovered['native']==native", "recovered['current']==old_after and recovered['native']==boot_before['native']"),
        ("verified_initial['current']==verified_prepared['current']==after", "verified_initial['current']==verified_prepared['current']==old_after"),
        ("verified_initial['native']==verified_prepared['native']==native", "verified_initial['native']==verified_prepared['native']==boot_before['native']"),
        ("require(not list(role.iterdir())and not os.listxattr(role)", "require({p.name for p in role.iterdir()}=={terminal['InvocationID']+'.terminal.exec',terminal['InvocationID']+'.closing.exec'}and not os.listxattr(role)"),
        ('pg1395-existing-role-normal-post-v1','pg1400-existing-admin-independent-post-v1'),
        ('PG1395-existing-role-normal-post-v1','PG1400-existing-admin-independent-post-v1'),
    )
    # Keep the prior immutable baseline literal inside EXTRA, not the new save slot.
    for old,new in replacements:
        if old not in raw:raise ValueError('actual full before/after phase binding required: '+old)
        raw=raw.replace(old,new)
    raw=raw.replace("base/'pg1400-existing-admin-independent-post-v1/after.private.json'","base/'pg1395-existing-role-normal-post-v1/after.private.json'")
    marker="result['existingRoleVerificationNormalClose']=True"
    raw=raw.replace(marker,marker+"\nresult['bootstrap']=bootstrap_meta\nresult['bootstrapProofHashes']={name:hashlib.sha256(newproof(name)).hexdigest()for name in ('before.private.json','after.private.json','pid1.private.jsonl','complete.private')}\nresult['currentCredentialsRetired']=True\nresult['capturedNormal20VerifiedBeforeCurrent']=True\nresult['gcDoesNotInferPastSuccess']=True")
    marker=' native=snapshot();require(native==snapshot())'
    raw=raw.replace(marker,marker+";require(native==boot_after['native']and boot_raw_before==newproof('before.private.json')and boot_raw_after==newproof('after.private.json'))")
    compile(raw,'<current ADMIN genuine terminal and independent fullpost>','exec');return raw

def main():
    if (W/'pg1396-execute-v3.exit').read_bytes()!=b'0\n':raise ValueError('actual current ADMIN normal execute required')
    env=dict(previous.previous.previous.previous.previous.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    raw=previous.previous.previous.previous.source().replace('pg1344-current-bootstrap-before-v1','pg1400-existing-admin-independent-post-v1')
    exec(compile(raw,'<current ADMIN fullpost transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
