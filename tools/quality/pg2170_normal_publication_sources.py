"""Normal completed current -> signed candidate finite publication, Unit unchanged."""
import ast
import inspect
import pg1306_ordinary_publication_sources as template
from pg2164_normal_candidate_ro_fixed_sources import sources as ro_sources
from pg2132_current_normal_unused_sources import CURRENT, CURRENT_BOM, BEFORE, production

TOOLS='pg2170-normal-publication-tools-v1'
SAVE='pg2173-normal-publication-v1'
CLASS='Pg2170OrdinaryPublication'
BOM='62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c'


def cohort(raw):
    pairs=[('PG1068','PG1846'),('pg1068','pg1846'),('PG1292','PG2126'),('pg1292','pg2126'),('d5b00104280028d9ea81b44c1d1c805f3c2861ed',CURRENT),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',production()),('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',CURRENT_BOM),('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM),('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),('9f651096-aef9-4fba-90b0-a653e99f035a','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'),('27accac0-c118-4c98-9244-02625a2d88a7','9026b2ab-bb42-49cd-a2bd-4c661049dce3'),('2026-10-10T20:03:22.718197Z','2026-10-13T03:08:18.452473Z'),('2026-10-10T20:22:34.439375Z','2026-10-13T03:35:44.330028Z'),('pg1304','pg2170'),('pg1305','pg2171'),('Pg1306','Pg2170'),('pg1306','pg2170'),('PG1306','PG2170')]
    for old,new in pairs:raw=raw.replace(old,new)
    return raw


def sources():
    code=inspect.getsource(template.sources)
    for old,new in [('Pg1300','Pg2164'),('pg1300','pg2164'),('PG1300','PG2164'),('Pg1306','Pg2170'),('pg1306','pg2170'),('PG1306','PG2170')]:code=code.replace(old,new)
    # Template compares literal old release; bind only this exact old-current condition.
    code=code.replace("'/opt/schubert-nk/releases/0.1.0-PG1068' and owner() == held)","'/opt/schubert-nk/releases/0.1.0-PG1846' and owner() == held)")
    initial=cohort(template.REF_INITIAL).replace('direct_tree,fd_record,path_record','direct_tree,fd_record')
    initial=initial.replace('pg1253-native-stop-v1/after.private.json','pg2167-normal-candidate-host-ro-v1/after.private.json')
    java=cohort(template.JAVA_PUBLICATION).replace('Outcome.SUCCESS','Outcome.WARNING')
    transition=cohort(template.TRANSITION_TEST).replace('Outcome.SUCCESS','Outcome.__OLD__').replace('Outcome.WARNING','Outcome.SUCCESS').replace('Outcome.__OLD__','Outcome.WARNING')
    ns={**template.__dict__,'previous':lambda:ro_sources(BOM,BEFORE),'JAVA_PUBLICATION':java,'REF_INITIAL':initial,'REF_LOOP':cohort(template.REF_LOOP),'TRANSITION_TEST':transition}
    exec(compile(code,'<actual normal finite publication factory>','exec'),ns)
    result={}
    for name,raw in ns['sources']().items():
        name=cohort(name);raw=cohort(raw)
        raw=raw.replace('pg2170-normal-candidate-ro-tools-v1',TOOLS).replace('pg2167-normal-candidate-host-ro-v1',SAVE)
        raw=raw.replace(SAVE+'/after.private.json','pg2167-normal-candidate-host-ro-v1/after.private.json')
        if name=='pg2170_input_preflight.py':
            raw=raw.replace('Pg2170CandidateRo','Pg2170OrdinaryPublication').replace("'traceback'))","'traceback', 'uuid'))")
        result[name]=raw
    helper='pg2170_native_owned_stop.py'
    original=ro_sources(BOM,BEFORE)['pg2164_native_owned_stop.py']
    fn=next(n for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)and n.name=='parent_configuration')
    result[helper]+='\n'+ast.unparse(fn)+'\n'
    namespace={'__name__':'actual_normal_publication_exports'}
    exec(compile(result[helper],'<actual whole normal helper>','exec'),namespace)
    attrs={n.attr for n in ast.walk(ast.parse(result['pg2170_native_refs.py']))if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='h'}
    if not attrs<=namespace.keys():raise ValueError('whole consumer exports required')
    for name,raw in result.items():
        if name.endswith('.py'):compile(raw,'<normal publication actual '+name+'>','exec')
        if '0.1.0-PG1638'in raw or 'REGULAR_MORNING_UNIT_EXCHANGE'in raw or 'NORMAL_DAEMON_RELOAD'in raw:
            raise ValueError('old release or duplicate Unit action forbidden')
    return result
