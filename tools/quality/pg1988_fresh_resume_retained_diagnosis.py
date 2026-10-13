"""Fresh retained finite resume owner and partial namespace, strictly readonly."""
import inspect
import pg1883_publication_retained_diagnosis as prior

HOST_PID=332236
SLOT='pg1988-fresh-resume-retained-diagnosis-v1'


def owner():
    raw=inspect.getsource(prior.owner).replace('pg1880_warning_publication_dispatch.py\\0activate\\0','pg1983_fresh_completed_resume_dispatch.py\\0prepare-resume\\0').replace('pg1880-activate','pg1983-prepare-resume').replace('PG1877_RUNTIME_RESUME_UNKNOWN phase=REFERENCE_SCOPE','PG1980_RUNTIME_RESUME_UNKNOWN phase=FINITE_FRESH_RESUME_PREPARATION')
    ns={**prior.__dict__,'HOST_PID':HOST_PID};exec(compile(raw,'<actual retained freshresume host>','exec'),ns);return ns['owner']()


PAYLOAD=prior.PAYLOAD.replace('pg1881-warning-publication-v1','pg1984-fresh-resume-preparation-v1').replace('PG1877','PG1980').replace('Pg1877OrdinaryPublication','Pg1980FreshResumePreparation').replace('pg1877-warning-publication-tools-v1/pg1877_native_refs.py','pg1980-fresh-resume-tools-v1/pg1980_native_refs.py')
PAYLOAD=PAYLOAD.replace("assert names==['refs-prepare.private.log']","assert {'before.private.json','refs-prepare.private.log'}<=set(names)and 'complete.private'not in names")
PAYLOAD=PAYLOAD.replace("'signalsStopsSqlWrites0':True","'signalsStopsSqlWrites0':True,'reloadReserved':(root/'daemon-reload-reserved.private').exists(),'freshRuntimePresent':pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1980-once-resume.conf').exists()")


def main():
    ns={**prior.__dict__,'HOST_PID':HOST_PID,'SLOT':SLOT,'owner':owner,'PAYLOAD':PAYLOAD}
    exec(compile(inspect.getsource(prior.main),'<actual freshresume readonly diagnosis>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
