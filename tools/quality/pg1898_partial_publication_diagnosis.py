"""Fresh actual unit-exchanged/not-reloaded owner; readonly inventory only."""
import inspect
import pg1883_publication_retained_diagnosis as prior

HOST_PID=318548
SLOT='pg1898-partial-publication-diagnosis-v1'


def owner():
    raw=inspect.getsource(prior.owner).replace('pg1880_warning_publication_dispatch.py','pg1894_complete_publication_dispatch.py').replace('pg1880','pg1894').replace('PG1877','PG1891').replace('phase=REFERENCE_SCOPE','phase=REGULAR_MORNING_UNIT_EXCHANGE')
    ns={**prior.__dict__,'HOST_PID':HOST_PID}
    exec(compile(raw,'<current partial publication host owner>','exec'),ns)
    return ns['owner']()


PAYLOAD=prior.PAYLOAD.replace('pg1881','pg1895').replace('pg1877','pg1891').replace('Pg1877','Pg1891').replace('PG1877','PG1891')
PAYLOAD=PAYLOAD.replace("assert names==['refs-prepare.private.log']","assert {'before.private.json','refs-prepare.private.log','current-link.private','expected-epoch.private','morning-unit-old.private'}<=set(names)and not any(n in names for n in ['complete.private','after.private.json','daemon-reload-reserved.private'])")


def main():
    ns={**prior.__dict__,'HOST_PID':HOST_PID,'SLOT':SLOT,'owner':owner,'PAYLOAD':PAYLOAD}
    exec(compile(inspect.getsource(prior.main),'<actual partial readonly diagnosis>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
