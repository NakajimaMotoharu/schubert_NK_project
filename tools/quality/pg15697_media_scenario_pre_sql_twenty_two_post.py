"""Correct only an observed suite metadata error; retain original runtime and passive evidence."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15694_media_scenario_pre_sql_twenty_two_pt as original
import pg15696_media_scenario_pre_sql_twenty_two_post as previous
RAW=previous.RAW
RUN=previous.RUN
OUT=data.BASE/'PG15697-media-scenario-pre-sql-twenty-two-post-v2'
OLD='54747a8f073ae1a8136286374179519548753201ee1084f3e7a0c15c7726aa87'
def require(ok,label):
    if not ok:raise ValueError(label)
def assess(raw):previous.assess(raw)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old=data.read_checked(previous.OUT/'manifest.json',OLD)
    raw=data.read_checked(data.BASE/'PG15694-media-scenario-pre-sql-twenty-two-pt-v1/manifest.json',RAW);assess(raw)
    require(old['actualExit']==0 and old['source']==raw['source']==original.SOURCE and old['originalManifestSha256']==RAW and old['suites']==3,'observed old metadata only')
    cases=[];suites={}
    for filename,pin in raw['xmlHashes'].items():
        path=RUN/'xml'/filename;require(data.sha(path.read_bytes())==pin,'original XML bytes');root=ET.parse(path).getroot()
        suites[root.get('name')]={k:int(root.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for c in root.findall('testcase'):
            require(not list(c),'no failed/skipped case');cases.append((c.get('classname'),c.get('name')))
    require(suites==raw['suites'] and len(suites)==len(raw['xmlHashes'])==len(original.COUNTS)==2 and len(cases)==len(set(cases))==22,'actual22/two XML')
    require(set(cases)=={(c['classname'],c['name']) for c in old['cases']}=={(c['classname'],c['name']) for c in raw['cases']},'all original methods unchanged')
    result=copy.deepcopy(old);result.update(suites=len(suites),invocation=invocation,suiteMetadataCorrection=dict(oldPostSha256=OLD,oldSuites=3,effectiveSuites=2,bug='BUG2141',crossCheck='ORIGINAL_XML_RAW_SELECTED_SUITES'))
    def contract(v):
        require(type(v['suites']) is int and v['suites']==len(suites)==2,'true two suites')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in {'suites','invocation'}),'all old execution/coverage evidence unchanged')
    contract(result);negative=[]
    for value in [3,1,0,True,None]:
        bad=copy.deepcopy(result);bad['suites']=value
        try:contract(bad)
        except ValueError:negative.append(repr(value))
        else:raise ValueError('wrong suites accepted')
    result['suiteMetadataCorrection']['negativeValuesRejected']=negative
    verify(raw['begin']['invocation']);verify(old['invocation']);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
