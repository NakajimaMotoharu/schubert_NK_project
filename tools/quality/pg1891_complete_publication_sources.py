"""New-only SSC283 profile with full actual helper exports; old failed bytes untouched."""
import ast
from pg1877_warning_publication_sources import sources as previous,BOM,BEFORE
from pg1872_warning_ro_marker_sources import sources as ro_sources

TOOLS='pg1891-warning-publication-tools-v1'
SAVE='pg1895-warning-publication-v1'
CLASS='Pg1891OrdinaryPublication'


def bind(raw):
    for old,new in [('pg1877','pg1891'),('Pg1877','Pg1891'),('PG1877','PG1891'),('pg1878','pg1892'),('pg1881','pg1895')]:raw=raw.replace(old,new)
    return raw


def sources():
    result={bind(name):bind(raw)for name,raw in previous().items()}
    original=ro_sources(BOM,BEFORE)['pg1872_native_owned_stop.py']
    function=[n for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)and n.name=='parent_configuration']
    target='pg1891_native_owned_stop.py'
    if len(function)!=1 or any(isinstance(n,ast.FunctionDef)and n.name=='parent_configuration'for n in ast.parse(result[target]).body):raise ValueError('one explicit preserved suffix export required')
    result[target]+='\n'+ast.unparse(function[0])+'\n'
    # Resolve the actual module API, not merely imports/text and not a stub with
    # the missing attribute supplied by a fixture.
    namespace={'__name__':'actual_export_prequalification'}
    exec(compile(result[target],'<actual full publication helper>','exec'),namespace)
    refs=ast.parse(result['pg1891_native_refs.py'])
    names={n.attr for n in ast.walk(refs)if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='h'}
    if not names or not names<=namespace.keys():raise ValueError('actual consumer helper export missing')
    return result
