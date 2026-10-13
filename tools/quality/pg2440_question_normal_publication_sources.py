"""Finite normal publication bound to the actually qualified current and new RO candidate."""
import inspect
import pg2170_normal_publication_sources as prior
from pg2420_question_candidate_ro_sources import sources as ro_sources
from pg2432_current_boot_question_sources import CURRENT,CURRENT_BOM,BEFORE,BOOT,production

TOOLS='pg2440-question-normal-publication-tools-v1'
SAVE='pg2443-question-normal-publication-v1'
CLASS='Pg2440OrdinaryPublication'
BOM='6e069bc89f53b513c719c27fbe71167afbd07b48caa0a31c61bda3e2222f11cf'


def cohort(raw):
    pairs=[('PG1068','PG2126'),('pg1068','pg2126'),('PG1292','PG2428'),('pg1292','pg2428'),
        ('d5b00104280028d9ea81b44c1d1c805f3c2861ed',CURRENT),
        ('769ddb15cd735c25fef581b5f9850ef9d0053c0f',production()),
        ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',CURRENT_BOM),
        ('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM),
        ('cbca8738-3b24-4090-b77c-bf029677cdd6',BOOT),
        ('9f651096-aef9-4fba-90b0-a653e99f035a','91f5484b-9702-4c7c-97f3-dd5110a853f9'),
        ('27accac0-c118-4c98-9244-02625a2d88a7','e1429ac8-f3dd-4e8c-83d2-1926c4ba8440'),
        ('2026-10-10T20:03:22.718197Z','2026-10-13T15:01:53.237266Z'),
        ('2026-10-10T20:22:34.439375Z','2026-10-13T19:18:53.785844Z'),
        ('pg1304','pg2440'),('pg1305','pg2441'),('Pg1306','Pg2440'),
        ('pg1306','pg2440'),('PG1306','PG2440')]
    for a,b in pairs:raw=raw.replace(a,b)
    return raw


def sources():
    raw=inspect.getsource(prior.sources)
    for a,b in [('2170','2440'),('Pg2164','Pg2420'),('pg2164','pg2420'),('PG2164','PG2420'),
                ('0.1.0-PG1846','0.1.0-PG2126'),
                ('pg2167-normal-candidate-host-ro-v1','pg2424-question-candidate-host-ro-v1'),
                ('pg2440-normal-candidate-ro-tools-v1','pg2440-question-candidate-ro-tools-v1')]:
        raw=raw.replace(a,b)
    namespace={**prior.__dict__,'cohort':cohort,'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,
               'BOM':BOM,'CURRENT':CURRENT,'CURRENT_BOM':CURRENT_BOM,'BEFORE':BEFORE,
               'production':production,'ro_sources':ro_sources}
    exec(compile(raw,'<actual current/new normal publication factory>','exec'),namespace)
    result=namespace['sources']()
    for name,body in result.items():
        if '3d69f5af' in body or '0.1.0-PG1846' in body or 'current-normal-unused-tools-v1' in body:
            raise ValueError('whole current boot and source path required')
    return result


if __name__=='__main__':raise SystemExit('source factory only; no VM operation')
