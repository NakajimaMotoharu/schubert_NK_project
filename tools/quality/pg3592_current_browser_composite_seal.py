"""Re-evaluate Root oracle then Browser oracle and exact present all24 chain."""
import ast
import inspect
import json
import types
from pg1446_current_cold_stage import W
from pg3564_current_browser_resume_sources import SOURCE,BOM
import pg3582_current_browser_acceptance as root
import pg3580_current_browser_actual as actual
import pg3146_browser_business_full_seal as template

SLOT='pg3592-current-browser-composite-full-seal-v1'


def compose(root_raw,chain,root_hash):
    fn=template.compose
    ns={**fn.__globals__,'root_seal':types.SimpleNamespace(SLOT=root.SEAL),'SLOT':SLOT}
    raw=types.FunctionType(fn.__code__,ns,'current_composite_seal')(root_raw,chain,root_hash,[])
    # Only the new composite oracle's positive prefix needs rebinding. Preserve
    # every already-current outer reader/negative authority byte unchanged.
    assignment=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ORACLE'for t in n.targets))
    oracle=ast.literal_eval(assignment.value)
    # BUG1309: CHAIN contains immutable real DB snapshots, including old run IDs.
    # A namespace/UUID binder must NEVER operate on the complete oracle string.
    old="require(root['source']=='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'and root['manifestSha256']=='37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863')"
    path="p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg3134-browser-resume-full-seal-v1/before.private.json')"
    if oracle.count(old)!=1 or oracle.count(path)!=1:raise ValueError('two exact positive prefix reader bindings required')
    before_tree=ast.parse(oracle)
    assignments_before={n.targets[0].id:ast.literal_eval(n.value)for n in before_tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
    oracle=oracle.replace(old,"require(root['source']=="+repr(SOURCE)+"and root['manifestSha256']=="+repr(BOM)+")",1)
    oracle=oracle.replace(path,"p=pathlib.Path('/var/lib/pgpt-s1-preservation/"+root.SEAL+"/before.private.json')",1)
    after_tree=ast.parse(oracle)
    assignments_after={n.targets[0].id:ast.literal_eval(n.value)for n in after_tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
    if assignments_before!=assignments_after:raise ValueError('snapshot and every independent nested oracle must remain exact')
    raw=template.constant(raw,'ORACLE',oracle)
    if "SAVE=BASE/'"+SLOT+"'" not in raw and "SAVE = BASE / '"+SLOT+"'" not in raw:
        # Inspect parsed final output role rather than relying on layout.
        assignments=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)]
        if len(assignments)!=1 or SLOT not in ast.unparse(assignments[0]):raise ValueError('new-only composite SAVE required')
    return raw


def payload(binding):
    proof=json.loads((W/actual.SLOT/'manifest.safe.json').read_bytes())
    if not(proof['actualExit']==0 and proof['productionSource']==SOURCE and proof['sourceQualified'] and proof['passedCases']==12 and proof['all24IndependentPost'] and proof['sameFourOrdinaryOwnersBeforeAfter']):
        raise ValueError('actual current finite Browser and independent all24 required')
    cases=W/actual.SLOT/'cases'
    chain={name:json.loads((cases/file).read_bytes())for name,file in [('before','before-rows.private.json'),('after','after-rows.private.json'),('context','context.private.json')]}
    context=chain['context'];template.browser.qualify(chain['before'],chain['after'],context['owner'],context['lower'],context['upper'])
    original=json.loads((W/root.SEAL/'manifest.safe.json').read_bytes())
    return compose(root.seal_payload(binding),chain,original['privateBeforeSha256'])


def main():
    module=root.previous.old_seal
    raw=inspect.getsource(module.entry)
    for a,b in [('pg2686-operation-current-live-binding-v1',root.LIVE),('pg2682-parent-watch-v1','pg3572-parent-watch-v1'),('pg2702-operation-current-rows-v1',root.ROWS),('pg2700-operation-current-terminal-v1',root.TERM)]:raw=raw.replace(a,b)
    ns={**module.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'TERM':root.TERM,'payload':payload}
    exec(compile(raw,'<current independent Root Browser composite transport>','exec'),ns);return ns['entry']()()


if __name__=='__main__':raise SystemExit(main())
