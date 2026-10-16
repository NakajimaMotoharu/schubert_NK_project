"""BUG1388 new-only exact API campaign; non-target upstream is not a passed PT."""
import ast
import subprocess
import pg4836_api_admitted_config_selected as previous

WORK=previous.ROOT.parent/'pgpt-runs/PG379/pg4838-api-admitted-config-selected-v1'


def source():
    raw=previous.source()
    marker="'-Dsurefire.failIfNoSpecifiedTests=false', 'test'"
    if raw.count(marker)!=1:raise ValueError('one non-target reactor option boundary')
    raw=raw.replace(marker,"'-Dsurefire.failIfNoSpecifiedTests=false', '-DfailIfNoTests=false', 'test'")
    tree=ast.parse(raw)
    node=tree.body[0]
    start=next(i for i,n in enumerate(node.body)if isinstance(n,ast.Assign)and ast.unparse(n.targets[0])=='tree')
    end=next(i for i,n in enumerate(node.body[start:],start)if isinstance(n,ast.If)and ast.unparse(n.test)=='actual != expected')
    if start>=end:raise ValueError('one actual helper qualification block')
    block=node.body[start:end]
    guard=ast.parse("if (snapshot/'src/schubert-nk-api/target/site/jacoco/jacoco.xml').exists():\n pass\nelse:\n reasons.append('target coverage absent; not executed or failed, never accepted')").body[0]
    guard.body=block;node.body[start:end]=[guard]
    marker=next(n for n in node.body if isinstance(n,ast.If)and ast.unparse(n.test)=='actual != expected')
    idx=node.body.index(marker)
    node.body.insert(idx,ast.parse("if not expected or any(not methods for methods in expected.values()):reasons.append('every selected suite requires explicit nonempty methods')").body[0])
    return ast.unparse(ast.fix_missing_locations(tree))


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed candidate first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(previous.template),'SOURCE':head,'WORK':WORK,'TESTS':previous.TESTS,'MODULES':previous.MODULES}
    exec(compile(source(),'<new-only exact selected API with failure persistence>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
