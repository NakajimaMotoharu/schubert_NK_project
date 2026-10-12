"""Fresh whole-qualified SSC278 signed candidate; no deployment or key transfer."""
import inspect
import pg1638_api_signed_candidate as prior
from pg1844_warning_unit_full_six import CANDIDATE,OLD as OLD_SOURCE

W,P,T=prior.W,prior.P,prior.T
OLD=W/'pg1638-release-v1'
NEXT=W/'pg1846-release-v1'
FROZEN=W/'pg1846-frozen-six-v1'
SIG=P/'pg1846-manifest-v1.sig'
OLD_BOM='195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'


def unit_vector(old):
    if type(old)is not bytes or old.count(b'Restart=no\n')!=1 or b'SuccessExitStatus='in old:raise ValueError('strict old signed Unit vector required')
    expected=old.replace(b'Restart=no\n',b'Restart=no\nSuccessExitStatus=10\n')
    marker=b'[Unit]\n'
    if expected.count(marker)!=1:raise ValueError('one exact Unit header required')
    return expected.replace(marker,b'# SSC278/BUG1162: completed WARNING10 is normal; all other nonzero exits remain failures.\n'+marker)


def validate_gate(outer,source):
    expected={'actualExit':0,'productionSource':source,'tests':3618,'suites':536,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,'classifierFourCounters100':True,'global100':False,'formalAccepted':False}
    if type(outer)is not dict or type(outer.get('actualExit'))is not int or outer['actualExit']!=0:raise ValueError('actual independent full required')
    gate=outer.get('result')
    if type(gate)is not dict or any(type(gate.get(k))is not type(v)or gate[k]!=v for k,v in expected.items()):raise ValueError('exact candidate-source full counts/static required')
    if gate.get('changedClasses')!=[]or gate.get('addedClasses')!=[]:raise ValueError('all Java Main unchanged required')
    hashes=gate.get('jarHashes')
    if type(hashes)is not dict or set(hashes)!=set(prior.MODULES)or any(type(h)is not str or len(h)!=64 or set(h)-set('0123456789abcdef')for h in hashes.values()):raise ValueError('all six actual qualified jar hashes required')
    return gate


def verify_delta(before,after):
    if type(before)is not dict or type(after)is not dict or set(before)!=set(prior.MODULES)or before!=after:raise ValueError('candidate Java class bytes must all match old signed Main')
    count=sum(len(v)for v in after.values())
    if count!=1643:raise ValueError('complete physical Main scope required')
    return count


def receive(module):
    raw=inspect.getsource(prior.transfer.receive).replace('PG1532','PG1844').replace('pg1535','pg1846')
    ns={**prior.transfer.__dict__,'FROZEN':FROZEN}
    exec(compile(raw,'<fixed fresh candidate whole JAR transport>','exec'),ns)
    return ns['receive'](module)


def main():
    raw=inspect.getsource(prior.main)
    raw=raw.replace('pg1638','pg1846').replace('PG1638','PG1846').replace('PG1544','PG1638')
    raw=raw.replace('1683dd9f6de00e71d2317d9af3cd50400a37bf4e',CANDIDATE)
    raw=raw.replace('pg1636-api-boundary-full-qualified-v1','pg1845-warning-unit-full-qualified-v1').replace('from pg1636_api_boundary_full_qualification import server','from pg1845_warning_unit_full_qualification import server')
    marker="    main_paths = {'api/api.jar': 'api', 'web/web.jar': 'web', 'operations/batch.jar': 'batch'}"
    if raw.count(marker)!=1:raise ValueError('one signed Unit candidate transformation boundary required')
    extra="""    unit='systemd/schubert-nk-morning-controller.service'
    template=(T/'src/deployment/systemd/schubert-nk-morning-controller.service.template').read_bytes()
    require(unit_vector((OLD/unit).read_bytes())==template)
    (NEXT/unit).write_bytes(template)
"""
    raw=raw.replace(marker,extra+marker).replace("allowed = {'VERSION'}","allowed = {'VERSION',unit}")
    raw=raw.replace("{'VERSION', 'api/api.jar'} <= changed","{'VERSION',unit} <= changed")
    raw=raw.replace("'tests': 3596, 'suites': 532","'tests': 3618, 'suites': 536").replace("'changedClasses': 3, 'addedClasses': 6","'changedClasses': 0, 'addedClasses': 0, 'soleUnitContractChanged':True")
    ns={**prior.__dict__,'PRODUCTION':CANDIDATE,'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'receive':receive,'verify_delta':verify_delta,'validate_gate':validate_gate,'unit_vector':unit_vector}
    exec(compile(raw,'<actual whole-qualified signed Unit candidate>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
