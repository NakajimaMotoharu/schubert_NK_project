"""Independent historical sets, current12-to0 XML/hash/three-source join and eight negatives."""
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from pg11662_current_db_pool_binding_fatal_case_delta_post import CHAIN

SOURCE='06685adcf32c8583c80cb9c3e4d06d547ada486c'
OUT=data.BASE/'PG11882-current-web-exporter-fixture-delta-post-v1'
PIN='b72c0cd9d6b7a16a261742b9e5403bcf7b3f9c027b1ee264998c9a9f9324fdd6'

def require(value,expected):
    if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('exact current12 corrections and all prior fixes/new8 required')

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical()
    chain=[*CHAIN,
      ('PG11660-current-db-pool-binding-fatal-case-delta-v1','dee8229dd3dbb1d2af8498d052beb3b1f9a814ba4718932e8fb01bf00e565eb8'),
      ('PG11690-current-standard-composition-literal-delta-v1','ccb7aeead6352e24366214aede9948d3bfda1c7bf649b9bbb70d18d6d7821695'),
      ('PG11720-current-jvm-system-literal-delta-v1','9034f7ef66b5b6a283df6f021e33aa2aed43dfe5b3817ce6f786c345b2871639'),
      ('PG11750-current-mq-recorder-literal-delta-v1','687847fc012bb9850865b0570ab427c1df3e687626a53a75bb774e813f2287f2'),
      ('PG11780-current-jdbc-collector-literal-delta-v1','37154957f609bd2a59fe16b9f6e413e10b88c964240a6c53dbf7fb5685a4320a'),
      ('PG11820-current-job-outbox-value-literal-delta-v1','2b0a3f645a9be16e1ce5267a5d9d2e8aa016dc9be0d1ab4d04b09fb44b1d878d'),
      ('PG11850-current-mq-media-collector-value-delta-v1','8a0764023d4bcf3d3a4781fc8f38450d11b98141ce5af6fdea33ff763e976e42')]
    for folder,pin in chain:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8791,3091,606]
    p=data.BASE/'PG11880-current-web-exporter-fixture-delta-v1/manifest.json';m=data.read_checked(p,PIN);d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);normal=data.read_checked(data.BASE/'PG11864-web-exporter-fixture-six-compile-v1/manifest.json','920dd983970da239050bc75e2f736650e4d5a6349aa5bff3d05e5203a40d2f2d');old=data.read_checked(data.BASE/'PG11834-mq-media-collector-value-six-compile-v1/manifest.json','878f67c2cd766901460e5a35ae4d2be7769778b3f8b775cc7fd6e03514aa561b');hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items());changed={path:h for path,h in hashes.items() if h!=old['begin']['inputHashes'][path]};assert changed==d['sourceInputDelta'] and len(changed)==3 and all('/src/test/' in path for path in changed)
    sp=data.BASE/'PG11868-web-exporter-fixture-static-v1';static=data.read_checked(sp/'manifest.json','3b08df0c3b89baf7b636f007498c861760492ed0b95056d9b324060fb2178ca5');assert static['source']==SOURCE and static['actualExit']==0 and static['sourceHashes']==changed
    for label in ('pmd','checkstyle'):
        raw=(sp/(label+'.xml')).read_bytes();assert data.sha(raw)==static['reports'][label]['sha256'];assert not any(n.tag.rpartition('}')[2] in ('violation','error','configerror') for n in ET.fromstring(raw).iter())
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[r for r in root if r['path'] in changed and r['id'] in ids];removed={r['id'] for r in rows};assert len(removed)==12 and removed==set(d['removedFindingIds']) and not d['freshRows'] and not d['addedFindingIds'] and not removed&(refs|pending);assert sum(r['rule']=='AvoidDuplicateLiterals' for r in rows)==11 and sum(r['rule']=='AvoidFieldNameMatchingMethodName' for r in rows)==1
    ids-=removed;assert len({r['id'] for r in root}-ids)==638 and len([i for i in ids if i.startswith('PMD-NEW-')])==8
    expected=dict(actualExit=0,source=SOURCE,sourceDerivedRaw=len(ids),totalPriorCorrections=638,totalIntroducedDiagnosticsRetained=8,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),actualViolationCount=None,wholeF03Accepted=False,newAccepted=0);require(m,expected);negatives=0
    for key,value in [('source','0'*40),('sourceDerivedRaw',8791),('totalPriorCorrections',626),('totalIntroducedDiagnosticsRetained',0),('joinedContextWarnings',3092),('sourceReboundCurrentWholePending',607),('actualViolationCount',0),('wholeF03Accepted',True)]:
        bad=dict(m);bad[key]=value;assert bad!=m
        try:require(bad,expected)
        except ValueError:negatives+=1
        else:raise AssertionError('incorrect current set metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=PIN,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),unreferenced=len(ids-refs),totalCorrections=638,allIntroducedDiagnosticsRetained=8,metadataNegativeVectors=negatives,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
