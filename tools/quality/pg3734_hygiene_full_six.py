"""One necessary batched-Main whole3714/545/1643, fixed source; no VM/business action."""
import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import pg3412_outbox_fixed_full as previous
from pg3274_header_group_full_six import rebase
from git_source_contract import last_main_source

ROOT=Path(__file__).resolve().parents[2];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='7fffab57a567914956b66452e5e54388642efdec'
NEW_TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceExecutableAdmissionTest.java'
NEW_CASES=[('dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmissionTest','typedValueBoundariesAreRejectedBeforeAclAndCorrectLimitsRemainAdmitted'),('dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmissionTest','aclFailureIdentityAndRequiredBoundaryValuesCannotBeAccepted')]
EXPECTED={**previous.EXPECTED,'batch':(1305,174,568)}


def require(value,reason):
    if not value:raise ValueError(reason)


def validate(head):
    require(last_main_source(ROOT)==SOURCE,'exact actually applied current source identity')
    prior=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes());require(prior['actualExit']==0 and prior['result']['tests']==3712,'genuine previous qualified whole')
    a=json.loads((W/'pg3730-octal-candidate-static-v1/manifest.safe.json').read_bytes());s=a['result'];applied=json.loads((W/'pg3732-octal-candidate-material-v1/apply.safe.json').read_bytes());require(a['actualExit']==applied['actualExit']==0 and applied['changedMainFiles']==30 and s['octalDelta']['actualRawReduction']==187 and s['octalDelta']['onlyOctalRuleChanged']and s['checkstyle']['findings']==0,'actual final unchanged static/candidate Main materialization')
    files=s['octalDelta']['allSourceSha256'];require(len(files)==849 and files=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'all849 Main bytes equal independently proven and statically diagnosed source')
    changed=set(subprocess.check_output(['git','diff','--name-only',prior['result']['sourceSnapshot'],head,'--',*previous.base.SCOPE],cwd=ROOT,text=True).splitlines());java={p for p in changed if '/src/main/java/'in p and p.endswith('.java')};require(changed==java|{NEW_TEST}and java<=set(files),'only batched registered Main hygiene plus exact one Test file; no settings/oracle change')
    approved=set()
    for name in ['pg3694-hygiene-candidate-material-v1','pg3724-private-candidate-material-v1','pg3732-octal-candidate-material-v1']:
        stage=json.loads((W/name/'stage.safe.json').read_bytes());approved.update(stage['changes'])
    require(java==approved,'all Main changes join all three original semantic/apply witnesses')
    require(not subprocess.check_output(['git','diff','e72911c2c4685dacd440bda00707b5be87f2716d',head,'--',NEW_TEST],cwd=ROOT),'exact selected-tested fixed type boundary fixture unchanged')
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean frozen operator')


def server_source(head,digest):
    h,d='a2'*20,'b3'*32
    return rebase(previous.server_source(h,d),'PG3412','PG3734',3712,3714,{h:head,d:digest,previous.SOURCE:SOURCE})


def main():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();validate(head)
    engine=previous.base.prior.transport_base.previous.previous.previous.previous.transport
    tree=ast.parse(inspect.getsource(engine.main))
    class Current(ast.NodeTransformer):
        def visit_Constant(self,node):
            value=node.value
            if isinstance(value,str):
                value=value.replace('PG1528','PG3734').replace('pg1528','pg3734')
                if value=='3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained':value='3712 retained plus exact two independent Root inode value/ACL boundary cases;545suite1643Main; batched semantic-proof source hygiene'
                if value.startswith('SSC269 new production storage/batch dependency'):value='BUG1312 Test boundary plus BUG1313/1317/1320 batched cross-module Main hygiene; required one fresh whole, old4856 native not candidate credit'
                return ast.copy_location(ast.Constant(value),node)
            if type(value)is int and value in {3582,524,1637}:return ast.copy_location(ast.Constant({3582:3714,524:545,1637:1643}[value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Current().visit(tree)));namespace={**engine.__dict__,'PRODUCTION':SOURCE,'server_source':server_source};exec(compile(raw,'<one necessary exact3714 whole>','exec'),namespace);return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
