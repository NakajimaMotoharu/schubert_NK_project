"""Finite new-source publication graph; no Unit exchange/reload or business start."""
import json
from pyflakes.api import check
import pg2532_strict_normal_publication_sources as previous
import pg2658_operation_candidate_sources as current_roles
from pg2658_operation_candidate_sources import bind as roles,production,W
from pg2666_operation_ro_sources import sources as ro_sources

TOOLS='pg2674-operation-publication-tools-v1';SAVE='pg2678-operation-publication-v1';CLASS='Pg2674OrdinaryPublication'
CURRENT,CURRENT_BOM,BEFORE,BOOT=current_roles.CURRENT,current_roles.CURRENT_BOM,current_roles.BEFORE,current_roles.BOOT


def candidate_bom():
    v=json.loads((W/'pg2654-candidate-build-v1.safe.json').read_bytes())
    if type(v.get('actualExit'))is not int or v['actualExit']!=0 or v.get('candidateSource')!=production()or v.get('signatureVerified')is not True:raise ValueError('actual signed new candidate required')
    return v['manifestSha256']


def bind(raw,bom):
    if type(bom)is not str or len(bom)!=64 or set(bom)-set('0123456789abcdef'):raise ValueError('one immutable candidate BOM required')
    # Old candidateBOM is this CURRENT_BOM; reserve its candidate role first.
    raw=roles(raw.replace(CURRENT_BOM,'__OPERATION_NEW_BOM__')).replace('__OPERATION_NEW_BOM__',bom)
    for a,b in [(previous.TOOLS,TOOLS),(previous.SAVE,SAVE),('pg2532','pg2674'),('Pg2532','Pg2674'),('PG2532','PG2674'),
      ('pg2524','pg2666'),('Pg2524','Pg2666'),('PG2524','PG2666'),('pg2528-strict-candidate-host-ro-v1','pg2670-operation-host-ro-v1')]:raw=raw.replace(a,b)
    return raw


def sources(bom=None):
    if bom is None:bom=candidate_bom()
    values={bind(n,bom):bind(raw,bom)for n,raw in previous.sources('c'*64).items()}
    # previous.sources supplied a synthetic pending BOM solely as source data;
    # replace that one candidate marker with the immutable actual requested BOM.
    values={n:raw.replace('c'*64,bom)for n,raw in values.items()}
    normal=ro_sources(bom)
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:values['pg2674_'+suffix]=normal['pg2666_'+suffix]
    for name,raw in values.items():
        if name.endswith('.py'):
            prelude="BUNDLE_HASH='pending-real-bundle'\n"if name=='pg2674_native_refs.py'else ''
            if check(prelude+raw,'<whole operation finite publication>'):raise ValueError('whole generated exports required')
            compile(raw,'<new finite publication graph>','exec')
        if '__OPERATION_'in raw or 'REGULAR_MORNING_UNIT_EXCHANGE'in raw or 'NORMAL_DAEMON_RELOAD'in raw:raise ValueError('unbound or duplicate action refused')
    return values


if __name__=='__main__':raise SystemExit('source factory only')
