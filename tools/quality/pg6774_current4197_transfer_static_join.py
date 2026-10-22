"""Raw1405 retained; one new explicit calendar lower-bound finding, all prior held scopes held."""
import inspect
import copy
import pg6716_current4184_static_join as prior
from pg6770_original4197_transfer_artifacts import read_whole

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
OLD='bad7b45337d10341e9972cc9b3f7a0b43d21e465'
PRIOR=BASE/'PG6754-current4189-owned-static-join-v1/manifest.json'
PRIOR_SHA='068a2d32c5af2dba53eb196f765d421912511062b26c1197591d7b1729e2f162'
QSHA='ca1b4171ac208630189b42c6aa54f4d89b7306e29d73433c8ed55b202ba0535d'
EXPECTED_RAW=1405
EXPECTED_PAIRS=1404
SUPPLEMENT={k:list(v)for k,v in prior.SUPPLEMENT.items()}
SUPPLEMENT.setdefault('TransferCleanup',[]).extend(['batch.file.TransferIoBoundaryTest','batch.file.TransferCleanupFailureTest'])


def bindings():
    scope={**vars(prior),'OLD':OLD,'PRIOR':PRIOR,'SUPPLEMENT':SUPPLEMENT}
    exec(compile(inspect.getsource(prior.bindings),'<Transfer4197 bindings>','exec'),scope);return scope['bindings']()


def review_changed(row):
    from pg6760_transfer_io_selected import MAIN
    if row['sourcePath']!=MAIN or row['rule']!='AvoidLiteralsInIfCondition':raise ValueError('only one explicit canonical year minimum finding')
    lines=(ROOT/MAIN).read_text().splitlines();at=int(row['beginline'])-1
    if lines[at].strip()!='if (date.getYear() < 1) {':raise ValueError('exact current year1 lower bound, no blanket literal approval')
    value=copy.deepcopy(row)
    value.update(status='REQUIRED_CONTRACT',reason='SS33312/SSC118 canonical yyyyMMdd excludes year0000 and starts at0001. After fixed8 ASCII digits/strict adjacent parser, year1 is an approved immutable protocol boundary, not an operator setting. Old3048002 independently preserves00000101/deletes00010101 and99991231; new grammar/leap vectors preserve invalid names. No source expectation or raw warning removed.',
      reviewedSourceSnippet=' | '.join(lines[max(0,at-1):at+4]),rawWarningRetained=True,ptAlternativeCompleted=0,
      reviewMethod='EXACT_CURRENT_CALENDAR_DOMAIN_AND_INDEPENDENT_LITERAL_ORACLE',formalAccepted=False,
      relatedQualityEvidence='1483/1484 and current original27/full4197; related regression, not per-site fault causality')
    return value


def definition():
    raw=inspect.getsource(prior.main)
    for before,after in (('PG6712-broker-parent-qualification-v3','PG6766-transfer-io-original-v2'),
      ('pg6712-broker-parent-qualification-v3','pg6766-transfer-io-original-v2'),
      ('PG6716-current4184-static-join-v1','PG6774-current4197-transfer-static-join-v1'),
      ('pg6716_current4184_static_join.py','pg6774_current4197_transfer_static_join.py'),
      ('all8511667','all8511669')):raw=raw.replace(before,after)
    scope={**vars(prior),'OLD':OLD,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'QSHA':QSHA,'EXPECTED_RAW':EXPECTED_RAW,'EXPECTED_PAIRS':EXPECTED_PAIRS,
      'read_whole':read_whole,'bindings':bindings,'review_changed':review_changed}
    exec(compile(raw,'<Transfer4197 raw1405 join>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
