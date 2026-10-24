"""Four native failure-frame catch spans individually joined to current raw XML/source/PT."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg9156_api_observation_context_host_v5 as selected
from host_tool_invocation import capture, verify

host=selected.run.host
OUT=host.BASE/'PG9157-api-observation-context-review-v1'
STATIC=host.BASE/'PG9155-api-observation-context-static-v4/manifest.json'
STATIC_SHA='94cc1a6c840b15672d13478cb5b81e579ffa52960b5b22b55509e5684fa94059'
HOST=host.W/'pg9156-api-observation-context-host-v4/manifest.safe.json'
HOST_SHA='cc25b55bda084d954b75a1000720e78eef582c83d08f028915f9d2f2a4903584'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContext.java'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'

def contract(rows,text):
    assert Counter(row['rule'] for row in rows)==Counter(AvoidCatchingGenericException=4)
    assert 'private final ApiMetricContext<?> metricContext;' in text and 'return metricContext;' in text
    assert 'catch (IOException | RuntimeException | Error primary)' in text
    assert 'catch (RuntimeException | Error diagnostic)' in text
    assert text.index('awaitStopped(remainingNanos)')<text.index('metricContext.close();')
    assert 'unconfirmed.set(true);' in text and 'onUnconfirmed.accept(primary);' in text
    assert 'TemporaryInfrastructureException.attachSecondary(primary, diagnostic);' in text
    assert 'TemporaryInfrastructureException.preserveFatal(primary);' in text and 'throw primary;' in text
    assert 'getConnection(' not in text and 'Duration.ofSeconds' not in text
    lines=text.splitlines()
    for row in rows:
        assert row['class']=='ApiObservationContext' and row['method']=='close'
        assert row['package']=='dev.codex.schubert.nk.api.monitoring'
        line=lines[int(row['beginline'])-1]; column=int(row['begincolumn'])-1
        assert 'catch (' in line and line[column:].startswith(('RuntimeException','Error'))

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    assert host.sha(STATIC)==STATIC_SHA and host.sha(HOST)==HOST_SHA
    raw=json.loads(STATIC.read_bytes()); actual=json.loads(HOST.read_bytes())
    assert raw['source']==actual['source']==selected.SOURCE and actual['actualExit']==0
    assert len(actual['cases'])==26 and all(row['result']=='PASS' and not row['nonPass'] for row in actual['cases'])
    names=[]
    for file in (HOST.parent/'xml').glob('TEST-*.xml'):
        assert actual['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case); names.append(case.get('name'))
    assert set(names)=={'obsCtx'+str(i).zfill(3) for i in range(1,27)}
    for name in ('checkstyle','spotbugs'):
        row=raw['static'][name]; assert row['receipt']['actualExit']==0 and row['receipt']['timedOut'] is False
        assert row['findings']==row['processingErrors']==0
    pmd=raw['static']['pmd']; assert pmd['receipt']['actualExit']==4 and pmd['findings']==4 and pmd['processingErrors']==0
    xml=host.W/'pg9155-api-observation-context-static-v4/pmd.xml'; assert host.sha(xml)==pmd['reportSha256']
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
    for name,mutate in (
      ('unknown-rule',lambda values,source: (list(values[:-1])+[dict(values[-1],rule='UNKNOWN')],source)),
      ('missing-current-row',lambda values,source: (values[:-1],source)),
      ('renewed-budget',lambda values,source: (values,source+' Duration.ofSeconds')),
      ('primary-normalized',lambda values,source: (values,source.replace('throw primary;','return;',1))),
      ('diagnostic-discarded',lambda values,source: (values,source.replace('TemporaryInfrastructureException.attachSecondary(primary, diagnostic);','',1))),
      ('sdk-before-drain',lambda values,source: (values,source.replace('awaitStopped(remainingNanos)','awaitUnknown(remainingNanos)',1)))):
        wrong,body=mutate(copy.deepcopy(rows),text)
        try: contract(wrong,body)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('bad failure-frame metadata accepted')
    decisions=[]
    for row in rows:
        primary='primary)' in text.splitlines()[int(row['beginline'])-1]
        reason=('Close must mark permanent UNKNOWN before a prebuilt policy. Same primary IOException/Runtime/Error is retained and rethrown; OBSCTX016..019/022..026 assert no downstream SDK/Pool success, compound cause/fatal not normalized.'
          if primary else 'A policy failure cannot skip original UNKNOWN state or lose a nested/direct fatal. Attach diagnostic then classify the original complete graph; OBSCTX020/021 assert original/suppressed identity and fatal priority, never a normal NPE catch.')
        decisions.append(dict(raw=row,classification='NECESSARY_FAILURE_FRAME_CONTRACT_REVIEWED',reason=reason,
          sourcePath=MAIN,sourceSha256=source_sha,sourceOrRulesChanged=False,suppressionAdded=False,
          ordinaryTestWitness='PG9156-api-observation-context-host-v4:OBSCTX001..026'))
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,currentHostManifestSha256=HOST_SHA,rawStaticManifestSha256=STATIC_SHA,
      staticDispositions=decisions,rawPmd=4,checkstyle=0,spotbugs=0,unclassified=0,actualViolationsOutstanding=0,
      formalDesignSource=FORMAL,formalDesignSha256=host.sha(host.ROOT/SS),metadataCounterexamples=rejected,
      productTestsExecuted=0,oldSourceResultsTransferred=False,suppressionsAdded=False,formalUpdated=False,newAccepted=0,actualMainNativePt='UNRUN_HOLD'))
    print(json.dumps(dict(actualExit=0,reviewedPmd=4,unclassified=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
