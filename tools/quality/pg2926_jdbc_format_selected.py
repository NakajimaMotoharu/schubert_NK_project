"""Fresh exact formatted Session input, unchanged Main/current jar; preserve old success."""
import subprocess
import pg2912_jdbc_compound_close_selected as prior
from pg2918_db_failure_group_full_six import FAILURE


def server():return prior.server().replace('PG2912-candidate-v1','PG2926-candidate-v1')


def transport_body():
    return prior.transport_body().replace('pg2912-jdbc-compound-close-selected-v2','pg2926-jdbc-format-selected-v1')


def main():
    changed=set(subprocess.check_output(['git','diff','--name-only',prior.SOURCE,'HEAD','--','src','pom.xml','.mvn','mvnw'],text=True).splitlines())
    if changed!={prior.TEST,FAILURE}:raise ValueError('same two Test-only paths required')
    ns={**prior.prior.__dict__,'TEST':prior.TEST,'FILES':prior.FILES,'SLOT':'PG2926-candidate-v1','SERVER':server()}
    exec(compile(transport_body(),'<formatted Session exact bytes actual>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
