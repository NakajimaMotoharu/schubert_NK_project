"""Four native failure-frame catch spans individually joined to current raw XML/source/PT."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg9170_api_stop_budget_host as selected
from host_tool_invocation import capture, verify

host=selected.run.host
OUT=host.BASE/'PG9171-api-stop-budget-review-v1'
STATIC=host.BASE/'PG9169-api-stop-budget-static-v1/manifest.json'
STATIC_SHA='96659b9a7b2fd6281d5e6a576cc5da71eb46b4880c593871da226265e45b5a31'
HOST=host.W/'pg9170-api-stop-budget-host-v1/manifest.safe.json'
HOST_SHA='3c87169aa7d90537c2d8524ef63fd07b42a063af588011b51899d675ea5a699b'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'

def contract(rows,text):
    assert Counter(row['rule'] for row in rows)==Counter(AvoidSynchronizedStatement=2)
    for token in ('private final Object lock = new Object();','TimeUnit.SECONDS.toNanos(60)',
        'if (begun) return;','begun = true;','began = time();','if (expired) return 0;',
        'long elapsed = time() - began;','elapsed < 0 || elapsed >= LIMIT_NANOS',
        'return LIMIT_NANOS - elapsed;','if (!returned) expired = true;'):
        assert token in text
    assert text.index('begun = true;')<text.index('began = time();')
    assert text.count('synchronized (lock)')==2
    for forbidden in ('new Thread','getConnection(','.close(','.start(','catch (NullPointerException'):
        assert forbidden not in text
    for row in rows:
        assert row['class']=='ApiStopBudget' and row['method'] in ('begin','remainingNanos')
        assert row['package']=='dev.codex.schubert.nk.api.bootstrap'
        line=text.splitlines()[int(row['beginline'])-1]; column=int(row['begincolumn'])-1
        assert line[column:].startswith('synchronized (lock)')

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    assert host.sha(STATIC)==STATIC_SHA and host.sha(HOST)==HOST_SHA
    raw=json.loads(STATIC.read_bytes()); actual=json.loads(HOST.read_bytes())
    assert raw['source']==actual['source']==selected.SOURCE and actual['actualExit']==0
    assert len(actual['cases'])==18 and all(row['result']=='PASS' and not row['nonPass'] for row in actual['cases'])
    names=[]
    for file in (HOST.parent/'xml').glob('TEST-*.xml'):
        assert actual['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case); names.append(case.get('name'))
    assert set(names)=={'apiStop'+str(i).zfill(3) for i in range(1,19)}
    for name in ('checkstyle','spotbugs'):
        row=raw['static'][name]; assert row['receipt']['actualExit']==0 and row['receipt']['timedOut'] is False
        assert row['findings']==row['processingErrors']==0
    pmd=raw['static']['pmd']; assert pmd['receipt']['actualExit']==4 and pmd['findings']==2 and pmd['processingErrors']==0
    xml=host.W/'pg9169-api-stop-budget-static-v1/pmd.xml'; assert host.sha(xml)==pmd['reportSha256']
    rows=[dict(node.attrib,message=' '.join(''.join(node.itertext()).split())) for node in ET.parse(xml).getroot().findall('.//{*}violation')]
    canonical=lambda values: Counter(json.dumps(value,sort_keys=True) for value in values)
    assert canonical(rows)==canonical(pmd['rawFindings'])
    text=(host.ROOT/MAIN).read_text(); source_sha=host.sha(host.ROOT/MAIN)
    normal=json.loads((selected.COMPILE/'manifest.safe.json').read_bytes())
    assert host.sha(selected.COMPILE/'manifest.safe.json')==selected.COMPILE_SHA
    assert normal['begin']['inputHashes'][MAIN]==raw['sourceHashes'][MAIN]==source_sha
    assert all(host.sha(Path(path))==digest for path,digest in raw['toolHashes'].items())
    assert subprocess.check_output(['git','show',FORMAL+':'+SS],cwd=host.ROOT)==(host.ROOT/SS).read_bytes()
    contract(rows,text); rejected=[]
    for name,old,new in (
      ('claim-after-clock','begun = true;','begun = false;'),
      ('renewed-limit','TimeUnit.SECONDS.toNanos(60)','TimeUnit.SECONDS.toNanos(120)'),
      ('revived-expiry','if (expired) return 0;','if (expired) return 1;'),
      ('clock-failure-normalized','if (!returned) expired = true;',''),
      ('wrong-lock','synchronized (lock)','synchronized (this)')):
        changed=text.replace(old,new,1); assert changed!=text
        try: contract(rows,changed)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('bad stop budget accepted')
    unknown=copy.deepcopy(rows); unknown[0]['rule']='UNKNOWN'
    try: contract(unknown,text)
    except AssertionError: rejected.append('unknown-rule')
    else: raise AssertionError('unknown rule accepted')
    decisions=[dict(raw=row,classification='NECESSARY_PRIVATE_STOP_BUDGET_LOCK_REVIEWED',
      reason='Only the private final primitive-state/monotonic-clock owner is locked: begin claims once before time; remaining sees the same sticky expiry and elapsed value. Current APISTOP004..018 assert literal60s, signed wrap, first claim, clock failure, no renewal and finite concurrent ownership. No resource/SQL/worker/provider acquisition under this lock; actual caller/native remains HOLD.',
      sourcePath=MAIN,sourceSha256=source_sha,sourceOrRulesChanged=False,suppressionAdded=False,
      ordinaryTestWitness='PG9170-api-stop-budget-host-v1:APISTOP001..018') for row in rows]
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,currentHostManifestSha256=HOST_SHA,rawStaticManifestSha256=STATIC_SHA,
      staticDispositions=decisions,rawPmd=2,checkstyle=0,spotbugs=0,unclassified=0,actualViolationsOutstanding=0,
      formalDesignSource=FORMAL,formalDesignSha256=host.sha(host.ROOT/SS),metadataCounterexamples=rejected,
      productTestsExecuted=0,oldSourceResultsTransferred=False,suppressionsAdded=False,formalUpdated=False,newAccepted=0,actualMainNativePt='UNRUN_HOLD'))
    print(json.dumps(dict(actualExit=0,reviewedPmd=2,unclassified=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
