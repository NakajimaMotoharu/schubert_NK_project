"""Complete ordinary constructor's normal return with independent literal, preserve v1 partial."""
import argparse
import inspect
import pg6798_web_correlation_selected as prior

ROOT,W,BASE=prior.ROOT,prior.W,prior.BASE
MAIN,OLD,TESTS,EXPECTED,MEASURED_TARGETS=prior.MAIN,prior.OLD,prior.TESTS,prior.EXPECTED,prior.MEASURED_TARGETS
guard,inventory=prior.guard,prior.inventory
SLOT='pg6806-web-correlation-positive-v2'


def read_original():
    scope={**vars(prior),'SLOT':SLOT}
    raw=inspect.getsource(prior.read_original)
    for before,after in (('pg6800-web-correlation-original-v1','pg6808-web-correlation-original-v2'),('PG6800-web-correlation-original-v1','PG6808-web-correlation-original-v2')):
        if raw.count(before)!=1:raise ValueError('one original48v2 output guard')
        raw=raw.replace(before,after,1)
    exec(compile(raw,'<independent original48v2>','exec'),scope);return scope['read_original']()


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'))
    if p.parse_args().action=='read':return read_original()
    cases,counts=inventory();scope={**vars(prior.profile),'runner':prior.previous.runner}
    exec(compile(inspect.getsource(prior.profile.execute),'<ordinary positive48v2>','exec'),scope)
    return scope['execute'](SLOT,guard,cases,counts,EXPECTED,{'web':['web/bootstrap/WebManagementServer'],
      'batch':['batch/file/StartupLaunchRecord','batch/platform/CleanupWorkerRequest$Expiry','batch/platform/CleanupFailedBackupRequest']})


if __name__=='__main__':main()
