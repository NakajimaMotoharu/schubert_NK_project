"""Fresh retained reload owner inventory, readonly; no reload/start/TERM issued."""
import inspect
import pg1883_publication_retained_diagnosis as prior

HOST_PID=325364
SLOT='pg1943-reload-retained-diagnosis-v1'


def owner():
    raw=inspect.getsource(prior.owner).replace('pg1880_warning_publication_dispatch.py\\0activate\\0','pg1938_unique_archive_partial_reload_dispatch.py\\0finish-reload\\0').replace('pg1880-activate','pg1938-finish-reload').replace('PG1877_RUNTIME_RESUME_UNKNOWN phase=REFERENCE_SCOPE','PG1925_RUNTIME_RESUME_UNKNOWN phase=ONLY_NORMAL_RELOAD')
    ns={**prior.__dict__,'HOST_PID':HOST_PID}
    exec(compile(raw,'<actual retained reload host owner>','exec'),ns)
    return ns['owner']()


PAYLOAD=prior.PAYLOAD.replace('pg1881-warning-publication-v1','pg1929-partial-reload-v1').replace('PG1877','PG1925').replace('Pg1877OrdinaryPublication','Pg1925PartialReload').replace('pg1877-warning-publication-tools-v1/pg1877_native_refs.py','pg1925-partial-reload-tools-v1/pg1925_native_refs.py')
PAYLOAD=PAYLOAD.replace("assert names==['refs-prepare.private.log']","assert {'before.private.json','refs-prepare.private.log'}<=set(names)and 'complete.private'not in names")
PAYLOAD=PAYLOAD.replace("'signalsStopsSqlWrites0':True", "'signalsStopsSqlWrites0':True,'reloadReserved':(root/'daemon-reload-reserved.private').exists()")


def main():
    ns={**prior.__dict__,'HOST_PID':HOST_PID,'SLOT':SLOT,'owner':owner,'PAYLOAD':PAYLOAD}
    exec(compile(inspect.getsource(prior.main),'<actual readonly reload diagnosis>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
