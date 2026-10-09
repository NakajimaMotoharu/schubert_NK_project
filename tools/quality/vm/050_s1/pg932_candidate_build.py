"""New-only signed 40ef/926 candidate, installed e016/862 never modified here."""
from pathlib import Path
from pg862_candidate_build import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous().replace('pg862_candidate_contract','pg931_candidate_contract')
    raw=raw.replace('PG862','NEXT_PG932').replace('pg862','NEXT_pg932').replace('PG832','PG862').replace('pg832','pg862').replace('NEXT_PG932','PG932').replace('NEXT_pg932','pg932')
    changes=(("SOURCE = 'e01612fcd7f2752df5ae0836b78538fd5e87f120'","SOURCE = '40ef6e894573d2ffab1d1732124960f9c98d5f97'"),("OLD_SOURCE = '2a0d5aa392c85a1dc12a1cdb423978e8500895b8'","OLD_SOURCE = 'e01612fcd7f2752df5ae0836b78538fd5e87f120'"),('pg857-completed-reference-six-host-v1','pg926-body-six-host-v1'),('fcc7df91f91af8867e2c911fd54e7a834c6d3ef313fc028be0d8c9f417e0d6c6','4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf'),('8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'),('3541','3560'),('522','523'),("'changedClasses': 15","'changedClasses': 4"))
    for a,b in changes:assert a in raw,a;raw=raw.replace(a,b)
    return raw
if __name__=='__main__':
    exec(compile(source(),'<932 same-source new-only signed candidate>','exec'),{'__file__':str(R/'pg932_candidate_build.py'),'__name__':'__main__'})
