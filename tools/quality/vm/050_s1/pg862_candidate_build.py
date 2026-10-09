"""New-only signed same e016/857 qualified candidate; no current/VM mutation."""
from pathlib import Path
from pg832_candidate_build import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous().replace('pg832_candidate_contract','pg862_candidate_contract')
    raw=raw.replace('PG832','NEXT_PG862').replace('pg832','NEXT_pg862').replace('PG796','PG832').replace('pg796','pg832').replace('NEXT_PG862','PG862').replace('NEXT_pg862','pg862')
    changes=(("SOURCE = '2a0d5aa392c85a1dc12a1cdb423978e8500895b8'","SOURCE = 'e01612fcd7f2752df5ae0836b78538fd5e87f120'"),
      ("OLD_SOURCE = '102cdf1d365ab321f74b523237590eee764ae858'","OLD_SOURCE = '2a0d5aa392c85a1dc12a1cdb423978e8500895b8'"),
      ('pg830-manager-six-host-v1','pg857-completed-reference-six-host-v1'),
      ('85c90fd6c60c88040127538ced822dce3e8260f290809635916d36871e685ede','fcc7df91f91af8867e2c911fd54e7a834c6d3ef313fc028be0d8c9f417e0d6c6'),
      ('c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'),
      ('3534','3541'),("'changedClasses': 2","'changedClasses': 15"),
      ("'addedAbstractInterfaces': 6, 'addedInternalClasses': 4, 'addedOuterClasses': 2","'addedAbstractInterfaces': 0, 'addedInternalClasses': 0, 'addedOuterClasses': 0"))
    for a,b in changes:assert a in raw,a;raw=raw.replace(a,b)
    marker="gate['knownOracleHold'] is None and gate['mainClasses'] == 1632"
    assert raw.count(marker)==1
    # This pinned qualification is explicitly host-only, not QA051/CHR/native/global acceptance.
    raw=raw.replace(marker,"gate['sourceQualification'] == 'FRESH_SIX_HOST_ONLY' and gate['mainClasses'] == 1632 and not gate['formalAccepted'] and gate['newNativePending']")
    return raw
if __name__=='__main__':
    exec(compile(source(),'<862 same frozen qualified whole candidate>', 'exec'),{'__file__':str(R/'pg862_candidate_build.py'),'__name__':'__main__'})
