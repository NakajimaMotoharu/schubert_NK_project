"""Twelve real Browser cases under genuine current Root/four-owner/TLS guard, no restarts."""
import inspect
import json
import types
import pg3580_current_browser_actual as previous
import pg3808_hygiene_acceptance as accepted
import pg3800_hygiene_browser_ready as ready
from pg3804_hygiene_current_live_binding import SLOT as LIVE
from pg3798_hygiene_current_observer import SOURCE,BOM
from pg1446_current_cold_stage import W

SLOT='pg3814-hygiene-browser-business-actual-v1'


def live():
    result=json.loads((W/LIVE/'manifest.safe.json').read_bytes())
    if result.get('actualExit')!=0 or result.get('productionSource')!=SOURCE:raise ValueError('actual same-source Root generation required')
    return result


def guard(seal,terminal,binding):
    raw=previous.bind(previous.template.GUARD)
    for a,b in [('4856b3fcaeb4cae983d77757a38dc0bf56a693e2',SOURCE),('dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72',BOM),('PG3420','PG3748')]:
        if raw.count(a)!=1:raise ValueError('exact positive identity-only Browser guard')
        raw=raw.replace(a,b)
    function=previous.template.guard
    return types.FunctionType(function.__code__,{**function.__globals__,'SOURCE':SOURCE,'GUARD':raw})(seal,terminal,binding)


def main():
    values={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'guard':guard,'require_ready':ready.require_ready,'READY':ready.SLOT,'root':types.SimpleNamespace(SEAL=accepted.SEAL,TERM=accepted.TERM,live=live)}
    exec(compile(inspect.getsource(previous.main),'<current7fff real Browser and full24 observer>','exec'),values)
    return values['main']()


if __name__=='__main__':raise SystemExit(main())
