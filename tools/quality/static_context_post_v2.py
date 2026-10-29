"""V2 adds immutable raw-manifest schema; v1 pure parser/truth and original qualification retained."""
from collections import Counter
import copy
import json
import re
import xml.etree.ElementTree as ET
import static_context_reader_v1 as selected
from static_context_post_v1 import preserved_truth,independent_location
from host_tool_invocation import capture,verify

def validate_manifest(raw,plan,rows,measured_source):
    ids=selected.validate_plan(plan)
    selected.require(isinstance(raw,dict) and isinstance(rows,list),'raw manifest and explicit rows')
    selected.require(len(rows)==len(ids) and {r.get('id') for r in rows}==ids and {r.get('path') for r in rows}==set(plan['targets']),'exact original ID and source path sets')
    for key,value in [('actualExit',0),('sourceContexts',len(rows)),('sourceFiles',len(plan['targets'])),('rawRetained',len(rows)),('productTestsExecuted',0),('newAccepted',0)]:
        selected.require(type(raw.get(key)) is int and raw[key]==value,'raw count must match exact set and integer type: '+key)
    for key in ['sourceChanged','wholeCurrentStaticMeasurement','nativeQualification','qualityGatePass','formalUpdated','wholeF03Accepted','whole451Accepted']:
        selected.require(key in raw and raw[key] is False,'explicit false quality/runtime field: '+key)
    for key in ['coverage','effortPercent']:
        selected.require(key in raw and raw[key] is None,'explicit unmeasured field: '+key)
    selected.require(raw.get('source')==selected.cfg.SOURCE and raw.get('normalManifestSha256')==selected.NORMAL_SHA,'actual normal source/domain')
    selected.require(raw.get('planSha256')==selected.data.sha(selected.wire(plan).encode()) and selected.digest(raw.get('reviewSha256')),'exact frozen plan and review digest')
    selected.require(raw.get('measurementReference')==list(selected.MEASURED) and raw.get('measurementSource')==measured_source,'historical measurement reference, not current whole static success')

def run(plan,pin,outname):
    invocation=capture(__file__);ids=selected.validate_plan(plan)
    selected.require(selected.digest(pin) and selected.output_name(outname) and outname!=plan['out'],'distinct independently pinned original and output')
    out=selected.data.BASE/outname;selected.require(not out.exists(),'new-only independent post')
    raw=selected.data.read_checked(selected.data.BASE/plan['out']/'manifest.json',pin);verify(raw['invocation'])
    selected.require(type(raw['actualExit']) is int and raw['actualExit']==0 and raw['source']==selected.cfg.SOURCE,'genuine fixed source context result')
    selected.require(raw['planSha256']==selected.data.sha(selected.wire(plan).encode()),'actual frozen configuration')
    review=selected.data.read_checked(selected.data.BASE/plan['out']/'review.json',raw['reviewSha256']);actual=review['rows']
    selected.require(len(actual)==len(ids) and {r['id'] for r in actual}==ids,'complete unique original ID set')
    measured=selected.data.read_checked(selected.data.BASE/selected.MEASURED[0]/'manifest.json',selected.MEASURED[1])
    validate_manifest(raw,plan,actual,measured['source'])
    xml=(selected.data.BASE/selected.MEASURED[0]/'pmd.xml').read_bytes();selected.require(selected.data.sha(xml)==measured['reports']['pmd']['sha256'],'original actual XML')
    original=selected.data.read_checked(selected.data.BASE/selected.ORIGINAL[0],selected.ORIGINAL[1]);catalog={r['id']:r for r in original}
    normal,normal_pin=selected.cfg.normal();selected.require(normal_pin==selected.NORMAL_SHA,'same frozen normal domain');hashes=normal['begin']['inputHashes']
    logical={r['path']:r for r in json.loads((selected.data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    seen=Counter()
    for row in actual:
        target=plan['targets'][row['path']];old=catalog[row['id']]
        text=selected.read_known(row['path'],hashes).decode()
        selected.require(selected.data.sha(text.encode())==target['sha256']==row['sourceSha256']==old['inputSha256'],'exact original/current source')
        selected.require(row['source']==selected.cfg.SOURCE and row['rule']==plan['rule'] and row['reason']==target['reason'],'specific source/rule/manual reason')
        selected.require(old['attributes']==row['attributes'] and old['rowSha256']==row['originalRowSha256'],'exact original attributes and raw occurrence')
        file,=[v for v in ET.fromstring(xml) if v.tag.rpartition('}')[2]=='file' and v.get('name').endswith('/'+row['path'])]
        nodes=[v for v in file if v.attrib==old['attributes']];key=(row['path'],selected.wire(old['attributes']))
        selected.require(len(nodes)==row['rawDiagnosticMultiplicity'] and len(nodes)>0 and type(row['occurrenceOrdinal']) is int and row['occurrenceOrdinal']==seen[key],'no deduplication or fabricated occurrence')
        seen[key]+=1
        attr=old['attributes'];lines=text.splitlines(keepends=True)
        start,end,token=independent_location(text,attr,target['prefixLines'],target['prefixSha256'])
        selected.require((start,end,selected.data.sha(token.encode()))==(row['spanStart'],row['spanEndExclusive'],row['spanSha256']) and token==row['typeToken'],'independent raw offsets/token')
        if plan['rule']=='AvoidSynchronizedStatement':
            selected.require(row['typeToken']=='synchronized' and text[end:].startswith(' ('+target['monitor']+')') and row['monitor']==target['monitor'],'explicit monitor token')
        else:selected.require(row['typeToken'] in {'Exception','RuntimeException','Throwable','Error','NullPointerException'},'bounded generic catch token')
        n=target['prefixLines']
        scope=dict(prefixLines=n,prefixSha256=target['prefixSha256'],wholeJavaUnicodeTranslationValidated=False)
        selected.require(selected.wire(row['coordinateScope'])==selected.wire(scope),'prefix-only scope never whole Unicode parser')
        if n is not None:
            prefix=''.join(lines[:n]);selected.require(chr(92)+'u' not in prefix and selected.data.sha(prefix.encode())==target['prefixSha256'] and int(attr['endline'])<=n,'original no-escape selected prefix')
        else:selected.require(chr(92)+'u' not in text,'ordinary whole-source span domain')
        selected.require(row['canonicalOwner']==row['canonicalCostOwner']==target['owner'],'canonical source owner, not change group inference')
        ownership=selected.canonical(row['path'],logical)
        selected.require(all(row[k]==v for k,v in ownership.items()),'independent canonical owner/basis lookup')
        preserved_truth(row)
    selected.require(all(seen[k]==next(r['rawDiagnosticMultiplicity'] for r in actual if (r['path'],selected.wire(r['attributes']))==k) for k in seen),'all raw duplicate occurrences consumed')
    selected.require(set(review['directNkRelatedSourceScope'])==set(plan['targets']) and review['importsAreNotRuntimeAllowlist'] is True,'complete source import map, never runtime permission')
    for path,imports in review['directNkRelatedSourceScope'].items():
        text=selected.read_known(path,hashes).decode();declared=re.findall(r'^import (?:static )?(dev\.codex\.schubert\.nk\.[A-Za-z0-9_.]+);$',text,re.M)
        selected.require(sorted(declared)==sorted(imports),'complete direct source import scope')
        for name,binding in imports.items():
            selected.read_known(binding['path'],hashes)
            typename=binding['path'].split('/src/main/java/',1)[1].removesuffix('.java').replace('/','.')
            selected.require((name==typename or name.startswith(typename+'.')) and hashes[binding['path']]==binding['sha256'] and binding['qualification']=='SOURCE_HASH_ONLY_NOT_WHOLE_REVIEW_OR_EXECUTION','only bound related source, never runtime allowlist')
    expected=selected.wire(actual)
    def strict(v):selected.require(selected.wire(v)==expected,'immutable exact typed source review required')
    labels=[]
    for key,value in [('id','UNKNOWN'),('source','0'*40),('sourceSha256','0'*64),('spanStart',-1),('spanEndExclusive',-1),('spanSha256','0'*64),('rawDiagnosticMultiplicity',0),('occurrenceOrdinal',-1),('canonicalOwner','UNKNOWN'),('canonicalCostOwner','UNKNOWN'),('ownershipStatus','FORGED'),('basis',''),('rawRetained',False),('rawRetained',0),('sourceChanged',True),('nativeRuntimeProven',True),('qualityGatePass',True),('productTestsExecuted',False)]:
        bad=copy.deepcopy(actual);bad[0][key]=value;selected.require(selected.wire(bad)!=expected,'negative must differ')
        try:strict(bad)
        except ValueError:labels.append(key+':'+type(value).__name__)
        else:raise AssertionError('altered metadata accepted')
    source_negatives=0
    for path,target in plan['targets'].items():
        text=selected.read_known(path,hashes).decode();selected.guard_text(target,text)
        for phrase in target['guards']:
            selected.require(phrase in text,'actual guard phrase')
            try:selected.guard_text(target,text.replace(phrase,'REMOVED_EXPECTED_CONTRACT'))
            except (ValueError,AssertionError):source_negatives+=1
            else:raise AssertionError('removed source contract accepted')
    for name in hashes:selected.read_known(name,hashes)
    verify(raw['invocation']);verify(invocation);out.mkdir()
    selected.data.write(out/'manifest.json',dict(actualExit=0,source=selected.cfg.SOURCE,invocation=invocation,reviewManifestSha256=pin,reviewSha256=raw['reviewSha256'],planSha256=raw['planSha256'],sourceContexts=len(actual),sourceFiles=len(plan['targets']),rawRetained=len(actual),metadataNegativeVectors=len(labels),labels=labels,sourceGuardNegativeVectors=source_negatives,independentOriginalXmlAndOffsets=True,directImportScopeConfirmed=True,productTestsExecuted=0,coverage=None,nativeRuntimeProven=False,qualityGatePass=False,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False))
    print(selected.data.sha((out/'manifest.json').read_bytes()))
