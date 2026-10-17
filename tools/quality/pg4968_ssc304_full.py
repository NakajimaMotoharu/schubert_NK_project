"""Required frozen SSC304 whole once, after actual53/7 selection; six format before PT."""
import ast
import inspect
import json
import pg4844_ssc301_302_full as previous
import pg4956_expiry_success_selected as selected_role

SOURCE='a8a09d7f88268131107c3b75705ba528efeb3041'
LABEL='PG4968'
ROOT,W=previous.ROOT,previous.W


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG4844',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {3761,551,1647}:
                return ast.copy_location(ast.Constant({3761:3785,551:553,1647:1649}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    compile(raw,'<SSC304 exact whole3785/553/1649>','exec');return raw


def main():
    raise ValueError('DRAFT: actual factory-owned PG4972 qualification and source repin required before one full campaign')
    selected=json.loads((W/'pg4964-expiry-success-selected-v1/manifest.safe.json').read_bytes())
    if not(type(selected['actualExit'])is int and selected['actualExit']==selected['actualMavenExit']==0
           and selected['sourceSnapshot']==SOURCE and selected['tests']==53 and selected['suites']==7 and not selected['reasons']):
        raise ValueError('actual frozen SSC304 selected53/7 all gates before whole')
    delta=selected_role.verify_main_bytes(W/'pg4964-expiry-success-selected-v1/source')
    if delta!=selected['coverage']['mainDelta']:raise ValueError('actual one Main/two interface bytes')
    raw=inspect.getsource(previous.previous.previous.main)
    raw=raw.replace('pg4420','pg4968').replace('shared-manager','ssc304')
    old="'tests': 3721, 'suites': 545, 'mainClasses': 1644"
    if raw.count(old)!=1:raise ValueError('one exact recorded planned whole inventory')
    raw=raw.replace(old,"'tests': 3785, 'suites': 553, 'mainClasses': 1649")
    raw=raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved',
        'SSC304 one repository Main ownership/predicate change plus two internal interfaces; new18 and prior test-only6; selected4964 exact53/7/static0; new whole required, no old native imported')
    ns={**vars(previous.previous.previous),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(raw,'<SSC304 required whole once>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
