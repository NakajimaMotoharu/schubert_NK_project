"""Same Main2741 ordinary9 + separately qualified API5, not fresh all3597."""
import pg1709_new_source_native_qualification as prior

def source():
    raw=prior.source().replace('pg1708-new-source-native-catalog-v1','pg1732-current-bootstrap-native-catalog-v1').replace('pg1709-new-source-native-qualified-v1','pg1733-current-bootstrap-native-qualified-v1').replace('PG1709','PG1733')
    raw=raw.replace('len(catalog[\'selected\'])!=8','len(catalog[\'selected\'])!=9').replace("'streams':8", "'streams':9")
    raw=raw.replace('8*16777216','9*16777216').replace('1683dd9f6de00e71d2317d9af3cd50400a37bf4e','b67cf7814e9e39818b5c4ec4817f1679a00fb59b')
    compile(raw,'<current Main9-native transport>','exec');return raw

def server():
    raw=prior.server().replace('PG1709','PG1733').replace("len(v['selected'])==8", "len(v['selected'])==9").replace("'currentNativeStreams':8", "'currentNativeStreams':9").replace("'remainingBootstrapCurrent':True", "'remainingBootstrapCurrent':False")
    marker='local={};host={};union={};gain={};xml_hashes={};gaps={};'
    if raw.count(marker)!=1:raise ValueError('one independent Main coverage union boundary required')
    extra="""
api_qualification=B/'runs/PG1717-selected-qualification-v1/manifest.safe.json'
require(sha(api_qualification)=='dab6f2d5c4c4823da3bf5a1cff3ef4b786e4e72985c84e595b0831d5d90d223c')
q=json.loads(api_qualification.read_bytes());require(q['actualExit']==0 and q['source']==v['productionSource']and q['results']['1716']['tests']==5 and q['results']['1716']['FESAbortedNotRun']==0)
api=B/'runs/PG1716-selected-v1';m=json.loads((api/'manifest.safe.json').read_bytes());aq=q['results']['1716']
require(sha(api/'manifest.safe.json')==aq['originalManifestSha256']and sha(api/'tests.xml')==aq['originalXmlSha256']and sha(api/'selected.exec')==aq['originalExecSha256']and aq['testSource']=='b67cf7814e9e39818b5c4ec4817f1679a00fb59b')
require(m['productionSource']==v['productionSource']and m['testSource']==aq['testSource'])
executions.append(api/'selected.exec')
"""
    # Keep historical per-module local counters compared with qualified1633;
    # append only to host/global union after that byte-qualified input capture.
    raw=raw.replace(marker,extra+'\n'+marker)
    raw=raw.replace("'qualified1633Tests':3596", "'qualified1633Tests':3596,'qualifiedCurrentApiSelectedTests':5,'freshAll3597Executed':False")
    compile(raw,'<currentMain9 plus independently qualified selected5>','exec');return raw

def main():
    engine=prior.prior.prior.prior.prior.prior
    ns={**engine.__dict__,'CODE':server(),'SOURCE':prior.SOURCE}
    exec(compile(source(),'<currentMain9-native qualification>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
