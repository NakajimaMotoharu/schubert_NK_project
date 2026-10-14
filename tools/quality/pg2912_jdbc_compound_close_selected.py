"""Test-only Session compound close oracle against qualified a9 jar, no VM replay."""
import inspect
import subprocess
from pyflakes.api import check
import pg2796_jdbc_candidate_contract as prior
from pg2798_jdbc_null_fixed_full_six import SOURCE,TEST

FILES=[TEST,'tools/quality/vm/050_s1/Pg2796JdbcContractLauncher.java']


def server():
    raw=prior.SERVER.replace('PG2796','PG2912').replace('source-full-PG2770','source-full-PG2798')
    # Reuse the stable shared JUnit launcher; its XML suite label is not a source ID.
    raw=raw.replace('Pg2912JdbcContractLauncher','Pg2796JdbcContractLauncher').replace("{'name':'PG2912'","{'name':'PG2796'")
    raw=raw.replace('require(mainclasses)','require(not mainclasses)').replace("'mainRecompiled':True","'mainRecompiled':False")
    raw=raw.replace("'mdb2796001ReadOnlyAndAbandonedNullResourcesPreserveAllCommittedRows'","'mdb2796001ReadOnlyAndAbandonedNullResourcesPreserveAllCommittedRows','mdb2804001CheckedCallbackAndCompoundJdbcClosePreserveRowsAndRedactSecondary'")
    if check('INPUT={}\n'+raw,'<complete Session Test-only compile>'):raise ValueError('whole server required')
    compile(raw,'<Session checked IO primary/compound close>','exec');return raw


def transport_body():
    raw=inspect.getsource(prior.main).replace('pg2772-db-contract-full-qualified-v1','pg2800-jdbc-null-fixed-full-qualified-v1').replace('3673','3680').replace('pg2796-jdbc-candidate-contract-v1','pg2912-jdbc-compound-close-selected-v1')
    old="(ROOT/FILES[1]).read_text().count('@Test\\n')"
    if raw.count(old)!=1:raise ValueError('one explicit Test role required')
    raw=raw.replace(old,"(ROOT/TEST).read_text().count('@Test\\n')")
    raw=raw.replace('pg2912-jdbc-compound-close-selected-v1','pg2912-jdbc-compound-close-selected-v2')
    compile(raw,'<Test role explicit independent transport>','exec');return raw


def main():
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    changed=subprocess.check_output(['git','diff','--name-only',SOURCE,head,'--','src','pom.xml','.mvn','mvnw'],text=True).splitlines()
    if changed!=[TEST]:raise ValueError('exact Test-only Session change required')
    ns={**prior.__dict__,'FILES':FILES,'TEST':TEST,'SLOT':'PG2912-candidate-v2','SERVER':server().replace('PG2912-candidate-v1','PG2912-candidate-v2')}
    raw=transport_body()
    exec(compile(raw,'<current Test-only Session transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
