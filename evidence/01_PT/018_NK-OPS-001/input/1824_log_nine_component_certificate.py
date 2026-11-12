"""Whole four Java sources include all nine nested physical classes; full220 report is retained."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));ld=lambda p:json.loads(p.read_text());post=B/'evidence/PG27804-log-whole40-independent-v1/manifest.json';m=ld(post);prepare=B/'evidence/PG27796-log-whole40-normal-v1/manifest.json';p=ld(prepare);xml=post.parent/'original-coverage.xml';assert sha(xml)==m['files']['original-coverage.xml'];r=ET.parse(xml).getroot();classes={x.get('name'):x for x in r.findall('.//class')};names={n.removesuffix('.class') for n in p['mainClassHashes']};assert len(names)==9 and len(p['apiMainSources'])==4
assert names=={n for n in classes if n.startswith(('dev/codex/schubert/nk/web/form/LogSearchForm','dev/codex/schubert/nk/web/view/LogSearchResultsViewModel','dev/codex/schubert/nk/web/view/LogSearchViewModel','dev/codex/schubert/nk/web/view/PageViewModel'))}
rows={n:{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in classes[n].findall('counter')} for n in names};assert all(v['missed']==0 for row in rows.values() for v in row.values());aggregate={}
for row in rows.values():
 for kind,v in row.items():
  aggregate.setdefault(kind,dict(covered=0,missed=0))
  for key in ['covered','missed']:aggregate[kind][key]+=v[key]
assert all(aggregate[k]['covered']>0 and aggregate[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']);O=B/'evidence/PG27808-log-four-source-nine-component-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,source=m['source'],productionCoreMain=m['productionCoreMain'],run=m['run'],post=ref(post),prepare=ref(prepare),allFourNewCompiledSources=p['apiMainSources'],allNinePhysicalClassHashes=p['mainClassHashes'],componentCounters=rows,componentAggregate=aggregate,componentScopeFour100=True,whole220Four100=False,full220CoverageAndMissesUnchanged=True,manualExclusions=[],oldExecUnion=False,additionalProductTestsExecuted=0,newAcceptance=0,actualBusinessDbAuthOrChrAccepted=False,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
root=R/'evidence/01_PT/016_NK-WEB-002';text='同exec補足PG27808: 今回compileしたLogForm/LogResults/LogView/Pageの4sourceはnested/enumを含む全9physicalを明示し、全9の全counter missed0・aggregate四100。full220原report/未網羅は不変更、追加実行/手動除外0。元P01614のcontroller/facade/config/実業務/CHR/451は別未受入。manifest SHA256 '+sha(O/'manifest.json')+'。'
for n in ['4147_P01614原Log四十単体仕様.md','4148_P01614原Log四十単体結果.md']:
 f=root/n;f.write_text(f.read_text()+'\n\n'+text+'\n')
print(json.dumps(dict(actualExit=0,wholeComponentPhysical=9,aggregate=aggregate,manifest=ref(O/'manifest.json'))))
