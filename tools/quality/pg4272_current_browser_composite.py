"""Immutable Root/Browser/all24 chain; keep nested historical data byte-for-byte."""
import json
import types
import pg3592_current_browser_composite_seal as previous
import pg4252_current_independent_acceptance as root
import pg4270_current_same_owner_browser as actual
from pg4260_stable_admission_image import SOURCE,BOM,live,before,execute
from pg1446_current_cold_stage import W

SLOT='pg4272-current-browser-composite-v1'


def compose(raw,chain,digest):
    ns={**vars(previous),'root':types.SimpleNamespace(SEAL=root.SEAL),'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT}
    return types.FunctionType(previous.compose.__code__,ns)(raw,chain,digest)


def payload(binding):
    v=json.loads((W/actual.SLOT/'manifest.safe.json').read_bytes())
    if not(v['actualExit']==0 and v['productionSource']==SOURCE and v['sourceQualified']and v['passedCases']==12 and v['all24IndependentPost']and v['sameFourOrdinaryOwnersBeforeAfter']):raise ValueError('actual complete same-owner Browser required')
    cases=W/actual.SLOT/'cases'
    chain={key:json.loads((cases/name).read_bytes())for key,name in [('before','before-rows.private.json'),('after','after-rows.private.json'),('context','context.private.json')]}
    context=chain['context'];previous.template.browser.qualify(chain['before'],chain['after'],context['owner'],context['lower'],context['upper'])
    accepted=actual.receipt(root.SEAL)
    return compose(root.seal_payload(binding,before()),chain,accepted['privateBeforeSha256'])


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live()),90))
