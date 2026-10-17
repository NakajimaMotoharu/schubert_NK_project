"""Pinned full-input static diagnostic on actual current3761 six-Jar ABI, no suppression."""
import ast
import inspect
import pg4700_ssc299_static as previous
from pg4844_ssc301_302_full import SOURCE,ROOT,W


def current_auxiliary(before,qualified):
    return {path.replace('/source-full-PG4694/','/source-full-PG4844/'):digest for path,digest in previous.current_auxiliary(before,qualified).items()}


def server_source(data):
    raw=previous.server_source(data).replace('source-full-PG4694','source-full-PG4844')
    raw=raw.replace('runs/PG4424-shared-manager-static-v1/manifest.safe.json','runs/PG4700-ssc299-static-v1/manifest.safe.json')
    raw=raw.replace('actualRuleCountDeltaFromOld964e','actualRuleCountDeltaFromOld825e')
    marker="result['sameCurrentSixJarAbi'] = True"
    if raw.count(marker)!=1:raise ValueError('one actual same-ABI final result')
    raw=raw.replace(marker,marker+"\n    result['auxMeaning']='All six project Jars are exact independently qualified PG4844 current3761 ABI; every original third-party auxiliary retained. Not F03/native/coverage acceptance.'\n    result['semanticEvidence']='PG4846 exact original PG4844 full3761/551/all1647; two implementation changes and one data-only declaration addition; old825e native not imported; all-six format order independently verified.'")
    return raw


def main():
    raw=inspect.getsource(previous.old.main)
    pairs=[('pg4428-shared-manager-whole-qualified-v1','pg4846-ssc301-302-whole-qualified-v1'),('pg3970-current-main-static-v1','pg4700-ssc299-static-v1'),('pg4424-shared-manager-static-v1','pg4850-ssc301-302-static-v1'),('PG4424-shared-manager-static-input-v1','PG4850-ssc301-302-static-input-v1'),('PG4424-shared-manager-static-v1','PG4850-ssc301-302-static-v1'),('actualRuleCountDeltaFromOld7bb','actualRuleCountDeltaFromOld825e')]
    for old,new in pairs:raw=raw.replace(old,new)
    raw=raw.replace("'includeCheckstyle': False","'includeCheckstyle': True")
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {3721,1644}:return ast.copy_location(ast.Constant({3721:3761,1644:1647}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    ns={**vars(previous.old),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'current_auxiliary':current_auxiliary,'server_source':server_source}
    exec(compile(raw,'<same3761 exact frozen original static rules>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
