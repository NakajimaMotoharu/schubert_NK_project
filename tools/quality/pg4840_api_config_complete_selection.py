"""BUG1388: strict required-module suite inventory; no NoTests policy override."""
import ast
import subprocess
import pg4838_api_admitted_config_selected as previous

ROOT=previous.previous.ROOT
WORK=ROOT.parent/'pgpt-runs/PG379/pg4840-api-config-complete-selected-v1'
MODULES={**previous.previous.MODULES,
 'dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest':'protocol',
 'dev.codex.schubert.nk.storage.ServiceConfigFilesTest':'storage',
 'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest':'bootstrap'}


def validate_selection():
    if set(MODULES.values())!={'protocol','storage','bootstrap','api'}or len(MODULES)!=7:raise ValueError('exact required reactor module/suite set first')
    for name,module in MODULES.items():
        p=ROOT/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')
        if not p.is_file()or '@Test'not in p.read_text():raise ValueError('actual physical nonempty Test per required module')
        pom=(ROOT/('src/schubert-nk-'+module+'/pom.xml')).read_text()
        if '<failIfNoTests>true</failIfNoTests>'not in pom:raise ValueError('original strict NoTests policy required')


def source():
    tree=ast.parse(previous.source())
    class KeepStrict(ast.NodeTransformer):
        def visit_List(self,node):
            node=self.generic_visit(node)
            node.elts=[v for v in node.elts if not(isinstance(v,ast.Constant)and v.value=='-DfailIfNoTests=false')]
            return node
    return ast.unparse(ast.fix_missing_locations(KeepStrict().visit(tree)))


def main():
    validate_selection()
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed candidate first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(previous.previous.template),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES}
    exec(compile(source(),'<strict required-module API selected scope>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
