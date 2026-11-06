"""Independent static DOM URL post for BUG2349; no Java, backend or test invocation."""
from pathlib import Path
import json,hashlib,subprocess
from html.parser import HTMLParser
R=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head='51d5defeca20d873e12a45dd3aa3c4d4add4d6fa'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
class Links(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.append(dict(attrs))
rows=[]
for name,count,expected in [('PG20678-scenario-detail-resource-eight-v1',23,8),('PG20684-search-route-corrected-eight-v1',22,115)]:
 p=R/'evidence/01_PT/016_NK-WEB-002/evidence'/name/'manifest.json';m=json.loads(p.read_text());assert m['actualExit']==0 and m['source']==head and m['snapshotCount']==count
 docs=sorted((p.parent/'output').glob('*.html'));assert len(docs)==count;links=[];pins={}
 for doc in docs:
  assert m['files']['output/'+doc.name]==sha(doc);parser=Links();parser.feed(doc.read_text());parser.close();pins[doc.name]=sha(doc)
  for a in parser.links:
   href=a.get('href','')
   if href.startswith('/scenario'):assert href=='/scenarios' or href.startswith('/scenarios/')
   if name.startswith('PG20684') and 'scenario-open' in a.get('class','').split():assert href=='/scenarios/17#entry-9';links.append(href)
   elif name.startswith('PG20678') and href in {'/scenarios/16','/scenarios/18'}:links.append(href)
 assert len(links)==expected
 rows.append(dict(manifest=str(p.relative_to(R)),sha256=sha(p),domCount=count,canonicalScenarioLinks=len(links),allScenarioPrefixesApproved=True,outputHashes=pins))
design='documents/200_UI/220_画面・認証/221_画面一覧・画面遷移設計.md';ref=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();data=subprocess.check_output(['git','show',ref+':'+design]);assert b'/scenarios/{id}' in data
out=R/'evidence/01_PT/016_NK-WEB-002/evidence/PG20690-scenario-search-route-post-v1';assert not out.exists();out.mkdir();m=dict(actualExit=0,metadataOnly=True,runtimeSource=head,producerPath=str(Path(__file__).relative_to(R)),producerSha256=sha(Path(__file__)),producerGitBinding='PENDING_NEXT_PUBLICATION_NO_SOURCE_RELABEL',design=dict(source=ref,path=design,sha256=hashlib.sha256(data).hexdigest(),expectedPattern='/scenarios/{id}'),independentParser='Python standard-library HTMLParser; fixed counts8 and115 from case matrix, no production method',rows=rows,productTestsReexecuted=0,newProductTests=0,newWbsAccepted=0,formalUpdated=False,bugs=['BUG-2349','YKT-2094']);(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(postExit=0,domCount=45,canonicalLinks=[x['canonicalScenarioLinks'] for x in rows],manifestSha256=sha(out/'manifest.json')))
