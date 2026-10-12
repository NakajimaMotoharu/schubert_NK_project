"""Current completed-DONE ordinary publication, explicit old/new/cohort joins."""
import inspect
import pg1306_ordinary_publication_sources as template
from pg1686_completed_candidate_ro_sources import sources as completed_ro
from pg1681_input_closure_contract import STANDARD

TOOLS='pg1691-completed-publication-tools-v1'
SAVE='pg1694-completed-ordinary-publication-v1'
CLASS='Pg1691OrdinaryPublication'

REPLACEMENTS=(
 ('PG1068','PG1544'),('pg1068','pg1544'),
 ('d5b00104280028d9ea81b44c1d1c805f3c2861ed','4d6bcbddb417b76d27e52d5d9640752c300edccf'),
 ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'),
 ('PG1292','PG1638'),('pg1292','pg1638'),
 ('769ddb15cd735c25fef581b5f9850ef9d0053c0f','2741c4546afad6c1e8b6efbd53dfb58144edf7bb'),
 ('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99','195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'),
 ('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),
 ('9f651096-aef9-4fba-90b0-a653e99f035a','0be226b1-bbb7-43d3-aa9e-59d0bda70f9a'),
 ('27accac0-c118-4c98-9244-02625a2d88a7','d28eead2-941c-4b97-9747-1758c0809e29'),
 ('2026-10-10T20:03:22.718197Z','2026-10-12T06:23:13.176261Z'),
 ('2026-10-10T20:22:34.439375Z','2026-10-12T06:48:58.973359Z'),
 ('pg1304','pg1691'),('pg1305','pg1692'),
 ('pg1253-native-stop-v1/after.private.json','pg1689-completed-candidate-host-ro-v1/after.private.json'),
)


def bind(raw):
    for old,new in REPLACEMENTS:raw=raw.replace(old,new)
    return raw


def sources():
    code=inspect.getsource(template.sources)
    for old,new in [('Pg1300','Pg1686'),('pg1300','pg1686'),('Pg1306','Pg1691'),('pg1306','pg1691')]:code=code.replace(old,new)
    # Current code spelling is joined explicitly, not by changing the frozen
    # current source to an obsolete role merely to make the template fit.
    code=code.replace("'/opt/schubert-nk/releases/0.1.0-PG1068' and owner() == held)","'/opt/schubert-nk/releases/0.1.0-PG1544' and owner() == held)")
    ns={**template.__dict__,'previous':completed_ro,'JAVA_PUBLICATION':bind(template.JAVA_PUBLICATION).replace('pg1306','pg1691'),'REF_INITIAL':bind(template.REF_INITIAL),'REF_LOOP':bind(template.REF_LOOP),'TRANSITION_TEST':bind(template.TRANSITION_TEST).replace('Pg1306','Pg1691').replace('PG1306','PG1691')}
    exec(compile(code,'<explicit current ordinary publication composition>', 'exec'),ns)
    result={}
    for name,raw in ns['sources']().items():
        name=bind(name);raw=bind(raw)
        raw=raw.replace('pg1691-completed-candidate-ro-tools-v1',TOOLS).replace('pg1689-completed-candidate-host-ro-v1',SAVE)
        # Only the baseline still belongs to the completed hostRO slot.
        raw=raw.replace(SAVE+'/after.private.json','pg1689-completed-candidate-host-ro-v1/after.private.json')
        if name=='pg1691_native_refs.py':raw=raw.replace('direct_tree,fd_record,path_record','direct_tree,fd_record')
        if name=='pg1691_input_preflight.py':
            raw=raw.replace('Pg1686CandidateRo','Pg1691OrdinaryPublication')
            raw=raw.replace(repr(tuple(sorted(STANDARD))),repr(tuple(sorted(STANDARD|{'uuid'}))))
        result[name]=raw
    return result
