"""Current completed-resume native eligibility; all40 before copies remain protected."""
import inspect
import json
import types
from pyflakes.api import check
import pg3530_outbox_current_native_catalog as template
import pg3858_current_resume_acceptance as root
from pg3876_current_resume_owned_sources import SOURCE,BOM,TOOLS
from pg3854_current_completed_resume_once import SLOT as ONCE
from pg3844_current_resume_sources import BOOT,RUN
from pg1446_current_cold_stage import W

SLOT='pg3890-current-resume-native-catalog-v1'


def current(binding,end):
    live=root.live();term=json.loads((W/root.TERM/'manifest.safe.json').read_bytes())
    if binding!=live['binding']or term['actualExit']!=0 or term['productionSource']!=SOURCE or not term['genuineParentDone']or type(end)is not int or end!=term['endMonotonicUs']:
        raise ValueError('same actual current resume Root and genuine terminal required')


def catalog_source(receipt,binding,end):
    fn=template.catalog_source
    values={**fn.__globals__,'current':current,'SOURCE':SOURCE,'BOM':BOM,'BOOT':BOOT,'TOOLS':TOOLS,'ONCE':ONCE,'before':root.before}
    raw=types.FunctionType(fn.__code__,values)(receipt,binding,end)
    old="require(len(frozen['native'])==35 and sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==22)"
    new="require(sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==40 and all(pathlib.Path(p).is_relative_to('/run/schubert-nk/pt-coverage')for p in frozen['native']))"
    if raw.count(old)!=1:raise ValueError('one exact original native admission')
    raw=raw.replace(old,new).replace('require(len(old)==22)','require(len(old)==40)')
    old="issued['ordinaryNoargs']is True and issued['oldCompletedRunNotResumed']is True"
    new="issued['freshCompletedRunResume']is True and issued['newActivationByProduction']is True and issued['selectedRun']=="+repr(RUN)
    if raw.count(old)!=1:raise ValueError('one explicit completed-resume admission')
    raw=raw.replace(old,new).replace('pg3520','pg3876').replace('Pg3520','Pg3876').replace('PG3520','PG3876').replace('oldSource22CopiesPreserved','all40BeforeCopiesPreserved')
    if SOURCE not in raw or BOM not in raw:raise ValueError('exact same source/BOM catalog')
    if check('SEALS={}\n'+raw,'<current completed-resume native eligibility>'):raise ValueError('complete catalog globals')
    compile(raw,'<current completed-resume native physical eligibility>','exec');return raw


def main():
    live=root.live();term=json.loads((W/root.TERM/'manifest.safe.json').read_bytes());current(live['binding'],term['endMonotonicUs'])
    raw=inspect.getsource(template.transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg3882-current-resume-owned-post-v1').replace('pg2030_parent_receipt.py','pg3876_parent_receipt.py')
    values={**template.transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<current resume native read-only transport>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
