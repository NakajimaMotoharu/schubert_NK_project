"""Project genuine original3971 XML only after independent qualification; never replay PT."""
import ast
import inspect
from pyflakes.api import check
import pg5836_current3967_public as previous
from pg5862_terminal_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,added_cases


def payload(data):
    raw=previous.payload(data).replace('PG5832','PG5860')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3967:return ast.copy_location(ast.Constant(3971),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<original3971 XML allowlist reader>'):raise ValueError('complete emitted reader')
    if 'PG5832'in raw or'Popen'in raw:raise ValueError('original current artifacts only')
    return raw


def operator_source():
    raw=inspect.getsource(previous.main)
    changes={'==(3967,590,1666)':'==(3971,592,1666)','pg5836-current3967-projection-v1':'pg5864-current3971-projection-v1','PG5836-case-reader-v1':'PG5864-case-reader-v1',"len(cases)!=3967":"len(cases)!=3971", "})!=3967":"})!=3971",'PG5831-isolation66-v1':'PG5866-terminal81-v1','c6244a36c37c2101c0625c911b35cc94f196b490186414ff034ffcc3d21a4057':'2bc4a5ea09fe9820f5b7798eb69bd2bb367e964ae191550834cd47b498dc739f','len(trace)!=12':'len(trace)!=4',"'PT-JMS-ISO'+str(i).zfill(3)for i in range(1,13)":"'PT-JMS-TERM'+str(i).zfill(3)for i in range(1,5)",'PG5827-isolation-reds-v1':'PG5855-terminal-reds-v1','f3de8b29bd903ed6d0e007e2bc43f8409a2670fd0e11905db76e7d9a0497a265':'e4419d0226f86570831110cb62bc7663b7675d5acc8582f134a1e30e186d9d5e','PG5832-current3967-cases':'PG5860-current3971-cases',"'BUG1494LimitedPolicyScopeVerified'":"'BUG1501ReceiverCoverageScopeVerified'","'tests':3967,'suites':590":"'tests':3971,'suites':592","'newCasesTraced':12":"'newCasesTraced':4"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one original3971 projection binding: '+old)
        raw=raw.replace(old,new,1)
    compile(raw,'<original3971 projection operator>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'QUALIFIED':QUALIFIED,'added_cases':added_cases,'payload':payload}
    exec(compile(operator_source(),'<original3971 projection operator>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
