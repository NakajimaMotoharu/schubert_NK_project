"""BUG1141: compile-only dependency empty selection is never an API PT pass."""
import inspect
import pg1630_api_terminal_selected as prior


def server():
    raw=prior.server().replace('PG1630','PG1631')
    marker="'-Dsurefire.failIfNoSpecifiedTests=false'"
    if raw.count(marker)!=1:raise ValueError('one fixed compile-only selection marker required')
    raw=raw.replace(marker,marker+", '-DfailIfNoTests=false'")
    compile(raw,'<new compile-only dependencies, exact mandatory API13>','exec');return raw


def main():
    raw=inspect.getsource(prior.prior.main).replace('PG1525','PG1631').replace('pg1525','pg1631').replace("'expectedTests':101","'expectedTests':13").replace("'expectedSuites':7","'expectedSuites':4").replace('SSC269 production filesystem implementation and all delegated original/runtime IO selected suites','PG-D412 BUG1141 compile-only deps empty selection permitted; API four suites13 exact or rejected')
    ns={**prior.prior.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only selected dependency correction>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
