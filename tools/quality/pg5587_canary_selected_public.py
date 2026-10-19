"""Original73 selected publication, stronger runtime oracle; no old71/failed3904 transfer."""
import ast
import inspect
import pg5570_monitor_public as previous

SOURCE='0ea400109d79e47327d9fff105ff763f9310a31f'
BASE=previous.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5587-monitor-canary-v1'
IDS={**previous.IDS,'bat283RuntimePostgresDriverAndScopeCanaries':'PT-BAT-283',
    'bat283bBootstrapFixtureCannotMaskWrongRuntimeScopeOrDuplicate':'PT-BAT-283B'}


def publication_source():
    class Current(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(71,8):return ast.copy_location(ast.Constant({71:73,8:9}[node.value]),node)
            if node.value=='27d1b35269b9a4e8848100565e7d6b901f425cd599805c6afe1031dc874ced50':node.value='9eef40acd5388ebf53737907bb5d664cf60a38430894de07a4a56df31896ca73'
            if node.value=='fb7917b4b9d9944f0cf3a6fb286d173569e31193ab1e8fbc31cf3f2f91d554ec':node.value='8e852219d9ada714da01b66604238ecf21025bfae14ce76b0d33a21bf87f0d32'
            if node.value=='pg5566-private-monitor-green-v2/source':node.value='pg5566-private-monitor-green-v3/source'
            return node
        def visit_Call(self,node):
            node=self.generic_visit(node)
            if isinstance(node.func,ast.Name)and node.func.id=='load':
                if isinstance(node.args[0],ast.Constant)and node.args[0].value=='pg5566-private-monitor-green-v2':node.args[0]=ast.Constant('pg5566-private-monitor-green-v3')
                if isinstance(node.args[0],ast.Attribute)and node.args[0].attr=='SLOT':node.args[0]=ast.Constant('pg5568-monitor-bytecode-v3')
            return node
        def visit_Tuple(self,node):
            node=self.generic_visit(node)
            if [e.value if isinstance(e,ast.Constant)else None for e in node.elts]==['pg5566-private-monitor-red-v1','pg5566-private-monitor-green-v1','pg5566-private-monitor-green-v2']:
                node.elts.append(ast.Constant('pg5566-private-monitor-green-v3'))
            return node
        def visit_Dict(self,node):
            node=self.generic_visit(node)
            for index,key in enumerate(node.keys):
                if isinstance(key,ast.Constant)and key.value=='newCriterionTraces':node.keys[index]=ast.Constant('criterionTraces');node.values[index]=ast.Constant(6)
            return node
    return ast.unparse(ast.fix_missing_locations(Current().visit(ast.parse(inspect.getsource(previous.main)))))


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'BASE':BASE,'IDS':IDS}
    exec(compile(publication_source(),'<original73 selected current scope>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
