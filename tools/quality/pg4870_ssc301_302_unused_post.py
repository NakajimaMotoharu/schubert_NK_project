"""Independent unused187 and current825e/all72 full post inside held tenRefs."""
import ast
import json
from pyflakes.api import check
import pg4712_ssc299_unused_post as previous
import pg4862_current_preservation_readonly as current
import pg4864_ssc301_302_unused_sources as role

SLOT='pg4870-ssc301-302-unused-post-v1'


def payload():
    role.qualify();raw=current.payload()
    marker='save=base/'+repr(current.SLOT)
    if raw.count(marker)!=1:raise ValueError('one fresh independent output namespace')
    raw=raw.replace(marker,'save=base/'+repr(SLOT),1)
    candidate=json.loads((role.W/'pg4860-candidate-build-v1.safe.json').read_bytes())
    capture=role.pinned(role.W/role.TOOLS,'pg4864_configuration_capture.py')
    nodes=ast.parse(raw).body
    for node in ast.parse(capture).body:
        if isinstance(node,(ast.Assign,ast.FunctionDef)) and not any(ast.dump(node)==ast.dump(n)for n in nodes):
            raise ValueError('actual same complete configuration definition required')
    # extra_source is already at the3982 boundary, unlike raw BASE roles.
    # Cross each remaining namespace exactly once; recursive role_text here
    # would turn the installed release into the candidate as well.
    extra=role.normalized_text(previous.role.normalized_text(previous.old.extra_source())).replace('native46Preserved','native72Preserved')
    marker="json.loads(before)=={k:v for k,v in expected.items()if k!='native'}"
    if extra.count(marker)!=1:raise ValueError('one strict actual canonical full11 boundary')
    extra=extra.replace(marker,'json.loads(before)==expected',1)
    tree=ast.parse(extra);last=tree.body[-1]
    if not(isinstance(last,ast.Expr)and isinstance(last.value,ast.Call)and isinstance(last.value.args[0],ast.Call)):
        raise ValueError('one unused summary schema')
    summary=last.value.args[0].args[0]
    for key,value in zip(summary.keys,summary.values):
        if isinstance(key,ast.Constant)and key.value=='guestFilesWritten':value.value=2
    checks=ast.unparse(ast.Module(body=tree.body[:-1],type_ignores=[]))
    addition="expected={**after,'native':native}\nrequire(sum(p.endswith('.exec')for p in native)==72)\n"+checks+'\ncandidate_post='+ast.unparse(summary)
    marker="    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(marker)!=1:raise ValueError('one held-tenRef pre-finally proof boundary')
    raw=raw.replace(marker,'\n'.join('    '+line for line in addition.splitlines())+'\n'+marker,1)
    marker="'genuineCompletion':FRESH_DONE}))"
    if raw.count(marker)!=1:raise ValueError('one after-normal-close terminal summary')
    raw=raw.replace(marker,"'genuineCompletion':FRESH_DONE,**candidate_post,'newTenReferencesReturnedNormally':len(refs)==10}))",1)
    raw='CANDIDATE='+repr(candidate)+'\nBEFORE='+repr(role.BEFORE)+'\nfrom pathlib import Path\n'+raw
    if check(raw,'<unused187/current full11/72native independent post>'):raise ValueError('all complete emitted static0')
    return raw


def main():
    placed=json.loads((role.W/'pg4868-place-v1.safe.json').read_bytes())
    if not(type(placed['actualExit'])is int and placed['actualExit']==0 and placed['sourceQualified']is True and placed['currentApprovalEpochChanged']is False):
        raise ValueError('actual unused-only placement first')
    return current.completed.role.before.admission.execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
