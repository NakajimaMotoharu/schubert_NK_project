"""Fresh current published/cohort/ordinary CLI preflight; no start or authority."""
import inspect
import pg1696_completed_publication_independent_post as previous

SLOT='pg1697-new-current-ordinary-before-v1'
EXTRA=r'''
parse_raw=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(parse_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
node=next(n for n in ast.parse(parse_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');scope={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<signed noargs declaration>','exec'),scope)
declaration=scope['exec_record'](after['configuration']['schubert-nk-morning-controller.service']['ExecStart'])
require(declaration is not None and declaration[1].endswith('dev.codex.schubert.nk.batch.file.MorningProcessMain')and '--resume'not in declaration[1])
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf').exists()and not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
require(os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize>=10737418240)
'''


def payload():
    raw=previous.payload().replace(previous.SLOT,SLOT)
    marker="save=base/'"+SLOT+"'"
    if raw.count(marker)!=1:raise ValueError('one current newstart before boundary required')
    raw=raw.replace(marker,EXTRA+'\n'+marker)
    raw=raw.replace("'rawExported':False", "'ordinaryNoargs':True,'originalBudgetSeconds':1800,'oldCompletedRunNotResumed':True,'authority':False,'rawExported':False")
    compile(raw,'<fresh current normal noargs before>','exec')
    return raw


def main():
    code=inspect.getsource(previous.prior.prior.main).replace('pg1639-completed-current-before-v1',SLOT)
    ns={**previous.prior.prior.__dict__,'payload':payload}
    exec(compile(code,'<new fresh ordinary before transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
