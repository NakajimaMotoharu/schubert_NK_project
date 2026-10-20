"""Publish genuine original6014 XML and six terminal traces;never replay PT/runtime."""
import inspect
import subprocess
import pg5930_current3973_public as engine
import pg5948_private_lock3973_public as previous
from pg6014_constants_whole import SOURCE,ROOT,W,OLD

QUALIFIED='pg6016-constants-qualified-v1'


def added_cases():
    if subprocess.check_output(['git','diff',OLD,SOURCE,'--',':(glob)src/*/src/test/**'],cwd=ROOT):
        raise ValueError('all3973 Test/oracle source unchanged;no synthetic new cases or aliases')
    return []


def payload(data):
    raw=previous.payload(data).replace('PG5944','PG6014')
    if 'PG5944'in raw or 'Popen'in raw:raise ValueError('original6014 artifact projection only')
    compile(raw,'<original6014 complete case projection>','exec')
    return raw


def operator_source():
    raw=inspect.getsource(engine.main)
    changes={'pg5930-current3973-projection-v1':'pg6022-current3973-projection-v1','PG5930-case-reader-v1':'PG6022-case-reader-v1',
             "public = base/'PG5926-current3973-cases'":"public = base/'PG6014-current3973-cases'",
             'PG5886-current3973-cases':'PG5944-current3973-cases','2045f1a9eb4eb60f2f470442bfbd3774f2925ce17cc88b5875d16f1163778d7f':'6370d6c31b7ac1124c6cb3abce653f7441ce0fa87b291f948cef5ddcb2977225',
             "allSeventeenTargetFour100=q['allSeventeenTargetFour100']":"changed67ActualFour100=q['changed67ActualFour100']"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact original6014 projection binding: '+old)
        raw=raw.replace(old,new,1)
    compile(raw,'<original6014 qualification receipt/projection>','exec')
    return raw


def main():
    scope={**vars(engine),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'QUALIFIED':QUALIFIED,'added_cases':added_cases,'payload':payload}
    exec(compile(operator_source(),'<original6014 read-only projection>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
