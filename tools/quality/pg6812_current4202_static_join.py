"""Retain all1405 raw findings; current Web18 spans and early preparation individually verified."""
import copy
import inspect
import pg6790_current4197_web_static_join as prior
from pg6804_original4202_artifacts import read_whole
from pg6796_web_early_cleanup_proof import verify_source

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
OLD='3c5f03d4aca569e4f5e722d7357e04749ad0998c'
PRIOR=BASE/'PG6790-current4197-web-static-join-v1/manifest.json'
PRIOR_SHA='37e63758cbf53f3b220adca6968661c72efb82ce4261baea8525a3ac658742bb'
QSHA='ad152991b2814cafd19cd68df220dad45b90d9acc6d9467ab0d3559bfacca31b'
EXPECTED_RAW=1405
EXPECTED_PAIRS=1387
SUPPLEMENT={k:list(v)for k,v in prior.SUPPLEMENT.items()}
SPANS={(70 if line==69 else line,rule):v for (line,rule),v in prior.SPANS.items()}


def bindings():
    scope={**vars(prior.base),'OLD':OLD,'PRIOR':PRIOR,'SUPPLEMENT':SUPPLEMENT}
    exec(compile(inspect.getsource(prior.base.bindings),'<current4202 bindings>','exec'),scope);return scope['bindings']()


def review_changed(row):
    if row['sourcePath']!=prior.MAIN or row['sourceSha256']!='e9e2b3332067db3cf2dda2422106a5003d8de7d46c9a38020253534a2ce8f9b2':raise ValueError('one exact early-preparation Web Main')
    item=SPANS.get((int(row['beginline']),row['rule']))
    if item is None:raise ValueError('one explicitly listed current Web span')
    expected,status,reason=item;lines=(ROOT/prior.MAIN).read_text().splitlines();at=int(row['beginline'])-1
    if lines[at].strip()!=expected:raise ValueError('exact current statement')
    verify_source();value=copy.deepcopy(row)
    value.update(status=status,reason='1490/PG-D504 current early-preparation review: '+reason+' Initial typed-result empty and fixed diagnostic now both precede bind; late-initialization variant is rejected.',
      reviewedSourceSnippet=' | '.join(lines[max(0,at-1):min(len(lines),int(row['endline'])+2)]),rawWarningRetained=True,
      reviewMethod='EXACT_CURRENT_SPAN_EARLY_PREPARATION_STATE_AND_EXCEPTION_REGIONS',formalAccepted=False,ptAlternativeCompleted=0,
      relatedQualityEvidence='1490/1491 current original48 and original4202; structural pre-acquisition proof, not dynamic heap-exhaustion causality')
    return value


def definition():
    raw=inspect.getsource(prior.base.main)
    for before,after in (('PG6712-broker-parent-qualification-v3','PG6808-web-correlation-original-v2'),('pg6712-broker-parent-qualification-v3','pg6808-web-correlation-original-v2'),
      ('PG6716-current4184-static-join-v1','PG6812-current4202-static-join-v1'),('pg6716_current4184_static_join.py','pg6812_current4202_static_join.py'),('all8511667','all8511669')):raw=raw.replace(before,after)
    scope={**vars(prior.base),'OLD':OLD,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'QSHA':QSHA,'EXPECTED_RAW':EXPECTED_RAW,'EXPECTED_PAIRS':EXPECTED_PAIRS,
      'read_whole':read_whole,'bindings':bindings,'review_changed':review_changed}
    exec(compile(raw,'<current4202 raw1405 join>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
