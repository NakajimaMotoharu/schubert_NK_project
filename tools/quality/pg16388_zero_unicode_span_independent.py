"""Independent regex/parity and original XML/byte verification; never import Product or execute Java."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RAW=('PG16386-zero-unicode-span-qualification-v1','a867f250314fe3d1a670f09e85e15d3e82067a125bcd2e94e90dc1a746d568a0')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
OUT=data.BASE/'PG16388-zero-unicode-span-independent-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m,baseline=[read(v) for v in (RAW,BASE)]
    rows=data.read_checked(data.BASE/RAW[0]/'spans.json',m['spansSha256'])
    original=data.read_checked(data.BASE/BASE[0]/'findings.json',baseline['findingsSha256'])
    index={(v['path'],wire(v['attributes'])):v for v in original if v['path'] in m['sourceProofs'] and v['rule']=='AvoidCatchingGenericException'}
    xml=(data.BASE/BASE[0]/'pmd.xml').read_bytes();require(data.sha(xml)==baseline['reports']['pmd']['sha256'] and baseline['processingErrors']==[],'original complete XML')
    xml_index={}
    for node in ET.fromstring(xml):
        tag=node.tag.rpartition('}')[2];require(tag not in {'error','configerror'},'no hidden analyzer errors')
        if tag!='file':continue
        path='src/schubert-nk-'+node.get('name').split('/src/schubert-nk-',1)[1]
        if path not in m['sourceProofs']:continue
        for item in node:xml_index[path,wire(dict(item.attrib))]=''.join(item.itertext()).strip()
    require(len(index)==len(rows)==22 and len(m['sourceProofs'])==3,'three whole Sources/22 diagnostics')
    texts={};proofs={}
    for p in m['sourceProofs']:
        blob=(data.ROOT/p).read_bytes();text=blob.decode();texts[p]=text
        require(not any(c in text for c in ('\r','\0','\v','\f','\x1c','\x1d','\x1e','\x85','\u2028','\u2029','\x1a')),'unambiguous LF')
        runs=re.findall(r'(\\+)u',text);require(all(len(run)%2==0 for run in runs),'independent raw-run regex proves no eligible marker')
        proofs[p]=dict(sourceSha256=data.sha(blob),ineligibleUnicodeMarkers=len(runs),eligibleUnicodeEscapes=0)
    seen=set()
    for row in rows:
        key=row['path'],wire(row['attributes']);require(key not in seen and key in index and key in xml_index,'each original row exactly once');seen.add(key)
        old=index[key];require(old['message']==xml_index[key] and old['sourceSha256']==row['sourceSha256']==proofs[row['path']]['sourceSha256']
            and row['originalDiagnosticRowSha256']==data.sha(wire(old)),'whole Source and complete original row')
        attrs=row['attributes'];lines=texts[row['path']].split('\n')
        a,b=int(attrs['beginline'])-1,int(attrs['endline'])-1;c,e=int(attrs['begincolumn'])-1,int(attrs['endcolumn'])-1
        require(a==b and lines[a].isascii() and '\t' not in lines[a],'ASCII single target line')
        start=sum(len(line.encode())+1 for line in lines[:a])+c;end=start+e-c
        token=texts[row['path']].encode()[start:end]
        require(row['canonicalSpanStart']==start and row['canonicalSpanEndExclusive']==end and token in {b'RuntimeException',b'Error'}
                and row['canonicalSpanSha256']==data.sha(token) and row['token']==token.decode(),'independent UTF8 offsets/token')
    require(seen==set(index),'no omitted original warning')
    helper_hash=data.sha((data.ROOT/m['helper']).read_bytes())
    def contract(v):
        for key in ['actualExit','zeroTranslationPositiveVectors','zeroTranslationNegativeVectors','bytePositiveVectors','coordinateNegativeVectors','targetWarningRows','semanticPurposeReviewsAdded','productTestsExecuted','externalActions','newAccepted']:
            require(type(v[key]) is int,'integer evidence count')
        require(v['actualExit']==0 and v['source']==SOURCE and v['baselineManifestSha256']==BASE[1] and v['coordinateToolManifestSha256']=='657a60a441c8a3424422b39f97a54b15326164a5954097c4a51e5ec349de49f1','source and qualified original tools')
        require(v['helper']=='tools/quality/pmd_source_span_no_unicode_translation.py' and v['helperSha256']==helper_hash and v['sourceProofs']==proofs and v['spansSha256']==m['spansSha256'],'same unchanged Source/helper/spans')
        require((v['zeroTranslationPositiveVectors'],v['zeroTranslationNegativeVectors'],v['bytePositiveVectors'],v['coordinateNegativeVectors'],v['targetWarningRows'],v['semanticPurposeReviewsAdded'])==(7,20,3,8,22,0),'bounded metadata qualification only')
        require(v['productTestsExecuted']==v['externalActions']==v['newAccepted']==0 and v['effortPercent'] is None,'no invented runtime/effort')
        require(all(v[k] is False for k in ['sourceChanged','ptExecutionExempt','whole451Accepted','wholeF03Accepted','formalUpdated']),'no silent acceptance')
    contract(m);negative=[]
    for key,value in [('actualExit',True),('source','OLD'),('helperSha256','0'*64),('sourceProofs',{}),('spansSha256','0'*64),('baselineManifestSha256','0'*64),('coordinateToolManifestSha256','0'*64),('targetWarningRows',21),('zeroTranslationNegativeVectors',19),('semanticPurposeReviewsAdded',22),('productTestsExecuted',22),('externalActions',1),('ptExecutionExempt',True),('wholeF03Accepted',True),('effortPercent',100)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false qualification '+key)
    for p,text in texts.items():require(data.sha((data.ROOT/p).read_bytes())==data.sha(text.encode()),'Source stable after independent read')
    for v in (m,baseline):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=RAW[1],
        helperSha256=helper_hash,sourceProofs=proofs,originalXmlSha256=data.sha(xml),independentMetadataNegativeVectors=len(negative),negativeLabels=negative,
        targetWarningRows=22,semanticPurposeReviewsAdded=0,productTestsExecuted=0,externalActions=0,sourceChanged=False,ptExecutionExempt=False,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
