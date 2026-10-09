"""New-only signed source102/794 candidate; current750 preserved and no guest mutation."""
from pathlib import Path
from pg750_candidate_build import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(),(
        ('pg749_candidate_contract','pg796_candidate_contract'),
        ('PG750','NEXT_PG796'),('pg750','NEXT_pg796'),('PG715','PG750'),('pg715','pg750'),
        ('NEXT_PG796','PG796'),('NEXT_pg796','pg796'),
        ("SOURCE = '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'","SOURCE = '102cdf1d365ab321f74b523237590eee764ae858'"),
        ("OLD_SOURCE = '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'","OLD_SOURCE = '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'"),
        ('pg748-closing-six-host-v1','pg794-completion-six-host-v1'),
        ('d4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e','72267f887833cb04c491568f4dcfb3653d7aed64172abe190646a56e40c7ba44'),
        ('74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5','a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'),
        ('3513','3517'),('519','520'),('1616','1620'),("'changedClasses': 7","'changedClasses': 1"),
        ("'addedAbstractInterfaces': 1, 'addedInternalClasses': 1","'addedAbstractInterfaces': 2, 'addedInternalClasses': 2"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<796 signed same794 candidate>','exec'),{'__file__':str(R/'pg796_candidate_build.py'),'__name__':'__main__'})
