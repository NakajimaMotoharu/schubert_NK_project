"""Freeze SSC266 owner/refs plus already qualified flat package-only helper JAR."""
import inspect
import pg1442_current_cold_compile as compiler
from pg1489_publication_recovery_sources import java,refs

def main():
    entry=inspect.getsource(compiler.main)
    for old,new in [('Pg1441CurrentColdPreparation','Pg1489PublicationOnlyRecovery'),('pg1441_current_cold_refs.py','pg1489_publication_recovery_refs.py'),('pg1441_current_cold_sources_test.py','pg1489_publication_recovery_sources_test.py'),('PG1442-current-cold-compile-v1','PG1490-publication-recovery-compile-v1'),('pg1442-current-cold-frozen-v1.safe.json','pg1490-publication-recovery-frozen-v1.safe.json')]:
        if old not in entry:raise ValueError('fixed current source compiler binding refused')
        entry=entry.replace(old,new)
    marker='    commands=['
    assert entry.count(marker)==1
    entry=entry.replace(marker,"""    helper=W/'pg1488-publication-helper-frozen-v1'
    helper_manifest=json.loads((helper/'manifest.safe.json').read_bytes())
    assert helper_manifest['actualExit']==0 and helper_manifest['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
    assert helper_manifest['jarSha256']=='f0584b4db40df3f0b40783f2f63cd8b95f382e6d9829429fc595c11723bcbf08' and sha(helper/'publication-only-helper.jar')==helper_manifest['jarSha256']
    write(OUT/'publication-only-helper.jar',(helper/'publication-only-helper.jar').read_bytes())
    cp+=':'+str(OUT/'publication-only-helper.jar')
"""+marker)
    ns={**compiler.__dict__,'OUT':compiler.W/'pg1489-publication-only-tools-v1','java':java,'observer':refs}
    exec(compile(entry,'<new-only qualified source owner recovery compiler>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
