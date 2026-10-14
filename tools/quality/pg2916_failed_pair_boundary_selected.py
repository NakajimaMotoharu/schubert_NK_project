"""Real-DB first/final identity, nullable14-column projections and pair invariants."""
import inspect
import subprocess
from pyflakes.api import check
import pg2912_jdbc_compound_close_selected as prior

TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BackupFailureSnapshotTest.java'
FILES=[TEST,'tools/quality/vm/050_s1/SelectedClassContractLauncher.java']


def server():
    raw=prior.server().replace('PG2912','PG2916').replace('MorningDatabaseSessionTest','BackupFailureSnapshotTest')
    raw=raw.replace("'Pg2796JdbcContractLauncher',str(xml),str(expected)","'SelectedClassContractLauncher',str(xml),'dev.codex.schubert.nk.batch.repository.BackupFailureSnapshotTest',str(expected),'PG2916'")
    raw=raw.replace("{'name':'PG2796'","{'name':'PG2916'")
    start=raw.index("{'mdb2792001");end=raw.index('}.issubset(names)',start)
    raw=raw[:start]+"{'cfdb2916001FirstAndFinalIdentityDriftRejectWithoutMutation','cfdb2916002EveryNullColumnAndMissingResourceIsBounded','cfdb2916003PairRejectsEqualIdAndForeignRunAtConstructor'"+raw[end:]
    if check('INPUT={}\n'+raw,'<actual failed pair complete server>'):raise ValueError('complete graph required')
    compile(raw,'<failed pair independent SQL postconditions>','exec');return raw


def transport_body():
    return prior.transport_body().replace('pg2912-jdbc-compound-close-selected-v2','pg2916-failed-pair-boundary-selected-v1')


def main():
    changes=set(subprocess.check_output(['git','diff','--name-only',prior.SOURCE,'HEAD','--','src','pom.xml','.mvn','mvnw'],text=True).splitlines())
    if changes!={TEST,prior.TEST}:raise ValueError('two explicit Test-only paths required')
    ns={**prior.prior.__dict__,'FILES':FILES,'TEST':TEST,'SLOT':'PG2916-candidate-v1','SERVER':server()}
    exec(compile(transport_body(),'<named failed pair Test input>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
