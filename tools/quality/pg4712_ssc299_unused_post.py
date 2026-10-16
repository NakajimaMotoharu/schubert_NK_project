"""Independent unused candidate187/current full preservation, all reads inside owned refs."""
import ast
import json
from pyflakes.api import check
import pg3988_literal_invariant_unused_post as old
import pg4704_current_preservation_readonly as current
import pg4706_ssc299_unused_sources as role
from pg4584_current_admission_image import execute

SLOT='pg4712-ssc299-unused-post-v1'


def payload():
    role.qualify()
    raw=current.payload()
    # Change the evidence output only; immutable original/current proof capsules stay exact.
    boundary="save = base / '"+current.SLOT+"'"
    if raw.count(boundary)!=1:raise ValueError('one fresh evidence output boundary')
    raw=raw.replace(boundary,"save = base / '"+SLOT+"'",1)
    raw=raw.replace("'run': 'PG4704-current-preservation-readonly-v1'","'run': 'PG4712-ssc299-unused-post-v1'",1)
    candidate=json.loads((role.W/'pg4702-candidate-build-v1.safe.json').read_bytes())
    capture=role.pinned(role.W/role.TOOLS,'pg4706_configuration_capture.py')
    original_nodes=ast.parse(raw).body
    for node in ast.parse(capture).body:
        if isinstance(node,(ast.Assign,ast.FunctionDef)):
            if not any(ast.dump(node)==ast.dump(n)for n in original_nodes):
                raise ValueError('existing current complete-configuration reader must be exact')
    extra=role.normalized_text(old.extra_source()).replace('native46Preserved','native64Preserved')
    tree=ast.parse(extra);last=tree.body[-1]
    if not(isinstance(last,ast.Expr)and isinstance(last.value,ast.Call)and isinstance(last.value.args[0],ast.Call)):
        raise ValueError('one original independent unused summary boundary')
    summary=last.value.args[0].args[0]
    checks=ast.unparse(ast.Module(body=tree.body[:-1],type_ignores=[]))
    # Existing completed-post scope owns the same ten refs through this entire extra read.
    point="    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(point)!=1:raise ValueError('one before-ref-finally proof boundary')
    addition="expected=after\nrequire(sum(p.endswith('.exec')for p in native)==64)\n"+checks
    raw=raw.replace(point,'\n'.join('    '+line for line in addition.splitlines())+'\n'+point,1)
    # The old summary claimed zero writes; this new verifier creates three private evidence files.
    for key,value in zip(summary.keys,summary.values):
        if isinstance(key,ast.Constant)and key.value=='guestFilesWritten':value.value=3
    point="with (save / 'result.safe.json').open('x') as f:"
    if raw.count(point)!=1:raise ValueError('one after-normal-close durable summary boundary')
    raw=raw.replace(point,'result.update('+ast.unparse(summary)+')\n'+point,1)
    result='CANDIDATE='+repr(candidate)+'\nBEFORE='+repr(role.BEFORE)+'\nfrom pathlib import Path\n'+raw
    if check(result,'<full current and unused candidate independent verifier>'):
        raise ValueError('entire emitted namespace required')
    compile(result,'<normal unused independent full post>','exec')
    return result


def main():
    placement=json.loads((role.W/'pg4710-place-v1.safe.json').read_bytes())
    if (type(placement['actualExit'])is not int or placement['actualExit']!=0
            or placement['sourceQualified']is not True or placement['currentApprovalEpochChanged']is not False):
        raise ValueError('genuine unused-only placement first')
    return execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
