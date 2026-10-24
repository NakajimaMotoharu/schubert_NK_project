"""Public numbered-evidence follow-up index; candidate lookup, never acceptance or permission."""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import unittest
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'evidence/01_PT/018_NK-OPS-001'
OUT=DOCS/'evidence/provisional/PG8150-evidence-followup-guard-v1'
NAME=re.compile(r'([0-9]{3,4})_[^/\\]+\.md')


def query_value(query):
    if not isinstance(query,str) or not query.strip() or len(query)>128 or any(ord(c)<32 for c in query):
        raise ValueError('bounded nonempty public evidence literal required')
    return query.casefold()


def eligible(name):
    return isinstance(name,str) and NAME.fullmatch(name) is not None and '.private.' not in name.casefold()


def index_entries(query,entries):
    needle=query_value(query)
    rows=[]
    for name,body in entries:
        if not eligible(name):
            continue
        if not isinstance(body,str):
            raise ValueError('public UTF8 evidence body required')
        if needle not in (name+'\n'+body).casefold():
            continue
        number=int(NAME.fullmatch(name).group(1))
        title=body.splitlines()[0] if body.splitlines() else ''
        rows.append(dict(number=number,name=name,title=title,sha256=hashlib.sha256(body.encode()).hexdigest()))
    return sorted(rows,key=lambda row:(-row['number'],row['name']))


def corpus():
    result=[]
    for file in DOCS.iterdir():
        if not eligible(file.name):
            continue
        if file.is_symlink() or not file.is_file() or file.stat().st_size>1024*1024:
            raise ValueError('only bounded regular public numbered evidence files')
        result.append((file.name,file.read_text()))
    return result


class FollowupTest(unittest.TestCase):
    def test_FOLLOWUP001_number_order_not_modification_or_acceptance(self):
        rows=index_entries('C02',[('1520_old.md','# C02 old gap'),('1555_result.md','# C02 result'),
                                   ('1733_repeat.md','# C02 repeat'),('1553_spec.md','# C02 spec')])
        self.assertEqual([1733,1555,1553,1520],[r['number'] for r in rows])
        self.assertTrue(all(set(r)=={'number','name','title','sha256'} for r in rows))
        self.assertEqual('1555_result.md',rows[1]['name'])

    def test_FOLLOWUP002_literal_unicode_and_case(self):
        entries=[('1734_索引.md','# C02 contract.* [literal]'),('1557_result.md','# C06')]
        self.assertEqual(['1734_索引.md'],[r['name'] for r in index_entries('c02',entries)])
        self.assertEqual(['1734_索引.md'],[r['name'] for r in index_entries('.*',entries)])
        self.assertEqual([],index_entries('C0[26]',entries))
        self.assertEqual([],index_entries('missing',entries))
        self.assertEqual('# C02 contract.* [literal]',index_entries('c02',entries)[0]['title'])

    def test_FOLLOWUP003_invalid_query_and_metadata(self):
        for value in (None,False,0,'','  ','x'*129,'C02\n','C02\x00'):
            with self.assertRaises(ValueError):
                index_entries(value,[])
        with self.assertRaises(ValueError):
            index_entries('C02',[('1734_public.md',None)])

    def test_FOLLOWUP004_private_and_path_scope_not_authority(self):
        entries=[('1734_public.md','# C02'),('1734_public.private.md','# C02'),
                 ('../../1734_public.md','# C02'),('private/1734_public.md','# C02'),
                 ('untracked.md','# C02'),('17340_public.md','# C02')]
        rows=index_entries('C02',entries)
        self.assertEqual(['1734_public.md'],[r['name'] for r in rows])
        self.assertFalse(any('accepted' in key.lower() or 'allowed' in key.lower() for row in rows for key in row))


def qualify():
    invocation=capture(Path(__file__))
    if OUT.exists():
        raise ValueError('new-only follow-up guard evidence, no replay')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FollowupTest))
    entries=corpus()
    snapshots={}
    for query,required in (
        ('C02','1555_C02四設定_実行結果.md'),
        ('C06','1557_C06_Batch既定値・非秘密設定境界_実行結果.md'),
        ('WebDbPool','1728_WebPool観測結線_単体テスト仕様書.md'),
        ('Prometheus','1730_Prometheus配布設定_単体テスト仕様書.md')):
        rows=index_entries(query,entries)
        prior=[row for row in rows if row['name']==required]
        if len(prior)!=1:
            raise ValueError('required actual prior follow-up must be visible before selecting next work')
        snapshots[query]=dict(matches=len(rows),newest=rows[:10],mandatoryPrior=prior[0],
                              acceptanceInferred=False,readPriorBodyBeforeSelectingNext=True)
    witnesses={}
    for name in ('PG7036-c02-four-template-host-v1','PG7038-c02-four-template-post-v1',
                 'PG7040-c06-config-template-host-v1','PG7042-c06-config-template-post-v1',
                 'PG8134-web-pool-qualification-v1','PG8140-prometheus-config-pt-v1',
                 'PG8146-c02-four-profiles-pt-v1'):
        file=DOCS/'evidence/provisional'/name/'manifest.json'
        item=json.loads(file.read_bytes())
        if item['actualExit']!=0:
            raise ValueError('actual existing success receipt required, not begin')
        witnesses[name]=dict(path=str(file.relative_to(ROOT)),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                             source=item.get('source'),actualExit=item['actualExit'],reexecuted=False)
    introductions={}
    for file in (
        'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricRecorder.java',
        'src/deployment/monitoring/prometheus/debug.yml.template'):
        introductions[file]=subprocess.check_output(['git','log','--diff-filter=A','--format=%H','--',file],
                                                     cwd=ROOT,text=True).splitlines()
        if len(introductions[file])!=1:
            raise ValueError('unique actual first introduction, not inferred manufacture')
    static=subprocess.run([sys.executable,'-B','-m','pyflakes',str(Path(__file__))],
                          cwd=ROOT,text=True,capture_output=True,check=False)
    actual=0 if result.wasSuccessful() and result.testsRun==4 and not result.skipped and static.returncode==0 else 1
    verify(invocation)
    value=dict(actualExit=actual,source=source,invocation=invocation,
        timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),startUTC=started,
        environment=dict(os=platform.platform(),python=sys.version),
        testsRun=result.testsRun,failed=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
        static=dict(actualExit=static.returncode,command=static.args,stdout=static.stdout,stderr=static.stderr),
        log=log.getvalue(),queries=snapshots,originalWitnesses=witnesses,firstIntroductions=introductions,
        publicCorpusFileCount=len(entries),bugs=['BUG1686'],horizontal=['YKT1437'],
        correctedEvents=['PGPT-20261008-1959','PGPT-20261008-1960'],
        originalEstimateUnchanged=dict(low=.5,base=1.5,high=4),
        plannedManufactureDelta=0,plannedContractCompletionDelta=0,additionalVerificationCases=12,
        repeatGroupReclassified='SELECTION_REWORK_DUPLICATE_CONFIRMATION_NOT_NEW_PLANNED_PROGRESS',
        originalResultsRetained=True,productTestsExecutedByGuard=0,actualVmActions=0,
        actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,effortPercent=None,
        whole451Accepted=False,noApprovalInferredFromIndex=True)
    os.umask(0o077)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as handle:
        json.dump(value,handle,ensure_ascii=False,sort_keys=True,indent=2)
        handle.write('\n')
    print(json.dumps(dict(actualExit=actual,tests=result.testsRun,corpus=len(entries),
                         manifestSha256=hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest())))
    raise SystemExit(actual)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query')
    args=parser.parse_args()
    if args.query is not None:
        rows=index_entries(args.query,corpus())
        print(json.dumps(dict(query=args.query,totalMatches=len(rows),newest=rows[:15],acceptanceInferred=False),ensure_ascii=False))
    else:
        parser.error('explicit bounded query required; qualification uses no-argument pg8150 entrypoint')
