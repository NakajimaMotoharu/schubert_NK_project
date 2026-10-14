"""Fresh a79/current and042 resource candidate roles; source factory, not operator."""
import json
import re
from pyflakes.api import check
import pg2516_current_strict_candidate_sources as previous
from pg2554_strict_current_owned_sources import sources as current_owners
from pg2650_operation_post_full_six import SOURCE
from pg1446_current_cold_stage import W

CURRENT=previous.SOURCE
CURRENT_BOM='2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f'
BEFORE='dc4a639f173b2f4b8f4c3aa3b187ef0105d7d50df87e788030a9a446a53f23a7'
BOOT=previous.BOOT
TOOLS='pg2658-operation-unused-tools-v1';SAVE='pg2662-operation-unused-placement-v1'
ARCHIVE='pg2660-operation-release-v1.tar';REMOTE='/home/ubuntu/pg2660-operation-input-v1'


def production():return SOURCE


def bind(raw):
    raw=raw.replace(previous.SOURCE,'__OPERATION_CANDIDATE__').replace(previous.CURRENT,CURRENT).replace('__OPERATION_CANDIDATE__',SOURCE)
    raw=raw.replace('PG2512','__OPERATION_RELEASE__').replace('pg2512','__OPERATION_RELEASE_LOWER__').replace('PG2428','PG2512').replace('pg2428','pg2512').replace('__OPERATION_RELEASE__','PG2654').replace('__OPERATION_RELEASE_LOWER__','pg2654')
    for a,b in [(previous.CURRENT_BOM,CURRENT_BOM),(previous.BEFORE,BEFORE),
      ('pg2514-current-cdbc-before-v2','pg2656-current-a79-before-v1'),
      ('06236d14-a6f8-4d05-a6ff-49c713cc2647','b29fb3e5-2c46-4eac-b8f3-d03b986338e3'),
      ('c347b14a-2e59-41e6-993c-a07e537cbd00','d0219581-24e4-4136-ac90-39d54e704378'),
      ('2026-10-13T21:16:10.125382Z','2026-10-14T00:36:06.976135Z'),
      ('2026-10-13T21:44:13.530366Z','2026-10-14T01:04:03.525607Z'),
      ('9024d0364d07478d9237b6941d725208','bab15677a060455482b670f6ae1dbd0b'),
      (previous.TOOLS,TOOLS),(previous.SAVE,SAVE),(previous.ARCHIVE,ARCHIVE),(previous.REMOTE,REMOTE),
      ('pg2516','pg2658'),('Pg2516','Pg2658'),('PG2516','PG2658'),
      ('pg2517','pg2659'),('pg2518','pg2660'),('PG2518','PG2660'),('pg2520','pg2662'),('PG2520','PG2662')]:raw=raw.replace(a,b)
    for a,b in [('29104365495','41101204300'),('30827355356','42816406603'),('194154','287080')]:raw=re.sub(r'\b'+a+r'\b',b,raw)
    return raw


def sources(bom,before=BEFORE):
    receipt=json.loads((W/'pg2656-current-a79-before-v1/manifest.safe.json').read_bytes())
    expected={'actualExit':0,'productionSource':CURRENT,'privateBeforeSha256':BEFORE,'runtimeAlreadyRetired':True,
      'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True}
    if before!=BEFORE or any(type(receipt.get(k))is not type(v)or receipt[k]!=v for k,v in expected.items()):raise ValueError('actual fresh a79 before required')
    values={bind(n):bind(raw)for n,raw in previous.sources(bom).items()}
    owners=current_owners()
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:values['pg2658_'+suffix]=owners['pg2554_'+suffix]
    for name,raw in values.items():
        if '__OPERATION_'in raw:raise ValueError('unbound role refused')
        if name.endswith('.py'):
            prelude="BUNDLE_HASH='pending-real-bundle'\n"if name in {'pg2658_native_refs.py','pg2658_input_preflight.py'}else ''
            if check(prelude+raw,'<whole new operation roles>'):raise ValueError('whole generated namespace required')
            compile(raw,'<fresh operation candidate roles>','exec')
    return values


if __name__=='__main__':raise SystemExit('source factory only; no VM action')
