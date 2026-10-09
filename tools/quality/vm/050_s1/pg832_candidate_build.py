"""New-only signed same2a/830 candidate; source102/current796 remains unchanged."""
from pathlib import Path
from pg796_candidate_build import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous()
    raw=raw.replace('pg796_candidate_contract','pg832_candidate_contract')
    raw=raw.replace('PG796','NEXT_PG832').replace('pg796','NEXT_pg832').replace('PG750','PG796').replace('pg750','pg796').replace('NEXT_PG832','PG832').replace('NEXT_pg832','pg832')
    changes=(
      ("SOURCE = '102cdf1d365ab321f74b523237590eee764ae858'","SOURCE = '2a0d5aa392c85a1dc12a1cdb423978e8500895b8'"),
      ("OLD_SOURCE = '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'","OLD_SOURCE = '102cdf1d365ab321f74b523237590eee764ae858'"),
      ('pg794-completion-six-host-v1','pg830-manager-six-host-v1'),
      ('72267f887833cb04c491568f4dcfb3653d7aed64172abe190646a56e40c7ba44','85c90fd6c60c88040127538ced822dce3e8260f290809635916d36871e685ede'),
      ('a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289','c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'),
      ('3517','3534'),('520','522'),('1620','1632'),("'changedClasses': 1","'changedClasses': 2"),
      ("'addedAbstractInterfaces': 2, 'addedInternalClasses': 2","'addedAbstractInterfaces': 6, 'addedInternalClasses': 4, 'addedOuterClasses': 2"))
    for old,new in changes:
        assert old in raw,old
        raw=raw.replace(old,new)
    return raw
if __name__=='__main__':
    exec(compile(source(),'<832 new same-source signed candidate>','exec'),{'__file__':str(R/'pg832_candidate_build.py'),'__name__':'__main__'})
