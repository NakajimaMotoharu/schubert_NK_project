"""Independent18 exact raw/source/design/PT reason join; proposed reasons do not pass the raw gate."""
from collections import Counter
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
REVIEW=('PG14665-storage-resource-eighteen-context-review-v1','cfa9dd6df1b5dba34bec67b2d922e5073a2a5342477e217645f919eff9a485fd')
OUT=data.BASE/'PG14667-storage-resource-eighteen-context-post-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent review')
    m=data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1])
    a=data.read_checked(data.BASE/'PG14664-storage-two-qualified-main-static-v1/manifest.json','4fb789834a8906d782f42acda3d8dc8a41cf403be5bb9938dbdfeacc025100a2')
    p=data.read_checked(data.BASE/'PG14666-storage-two-static-post-v1/manifest.json','63a7b7f43111d1f4b71fb280b114302cc205f601cf9ea2dc6b65abf7d1a4af15')
    pt=data.read_checked(data.BASE/'PG14654-storage-resource-whole-twenty-six-post-v1/manifest.json','64716d82a4588387921fc49a0cdb423c79b661c22429a7a5662ab56edcac5a5f')
    require(all(v['source']==SOURCE and v['actualExit']==0 for v in (m,a,p,pt)),'same genuine source')
    require(p['analysisManifestSha256']=='4fb789834a8906d782f42acda3d8dc8a41cf403be5bb9938dbdfeacc025100a2' and p['metadataNegativeVectors']==10,'independent raw XML provenance')
    raw=data.read_checked(data.BASE/'PG14664-storage-two-qualified-main-static-v1/findings.json',a['findingsSha256'])
    rows=data.read_checked(data.BASE/REVIEW[0]/'review.json',m['reviewSha256'])
    main_path='src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'
    source=(data.ROOT/main_path).read_bytes();source_pin=data.sha(source);lines=source.decode().splitlines()
    require(source_pin=='639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf','whole source fixed')
    design_path='documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md'
    design=subprocess.check_output(['git','show','8b91944df5820535e23ba2469740f1c0aa94c447:'+design_path],cwd=data.ROOT)
    require(design==(data.ROOT/design_path).read_bytes() and data.sha(design)==m['designSha256'],'approved design bytes')
    cases={(v['classname'],v['name'].split('(',1)[0]) for v in pt['cases']}
    require(len(cases)==26 and pt['targetUnitFour100'] and pt['singleSession'] and pt['crcMismatch']==0,'actual ordinary26 not review-generated PASS')
    def contract(value,items):
        expected=dict(source=SOURCE,actualExit=0,rawFindingRows=18,uniqueFindingSignatures=14,duplicateRawOccurrencesRetained=4,sourceProgramsWithFindings=1,reviewedRows=18,rawQualityGateExit=1,actualApplicableViolations=None,qualityGatePass=False,currentWholeJoinPending=True,wholeF03Accepted=False,whole451Accepted=False,productionChanged=False,rulesOrSuppressionChanged=False,productTestsExecuted=0,analyzersReexecuted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
        require(all(json.dumps(value.get(k),sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in expected.items()),'exact review not quality/effort promotion')
        require(len(items)==18 and [v['raw'] for v in items]==raw,'all original raw occurrences retained in order')
        seen=Counter()
        for index,(item,original) in enumerate(zip(items,raw),1):
            attr=original['attributes'];line_number=int(attr['beginline']);column=int(attr['begincolumn']);end=int(attr['endcolumn'])
            line=lines[line_number-1];token=line[column-1:end-1]
            require(original['path']==main_path and original['sourceSha256']==source_pin and line_number==int(attr['endline']),'exact typed source site')
            key=(original['rule'],line_number,column);seen[key]+=1
            require(item['id']==f'STO14664-{index:03d}' and item['rawOccurrence']==seen[key] and item['sourceToken']==token and item['sourceMethod']==attr['method'],'row identity/site/method exact')
            if original['rule']=='AvoidCatchingGenericException':
                require(token in ['RuntimeException','Error'],'actual generic catch token')
                role=('PRIMARY_' if ' primary)' in line else 'SECONDARY_')+('RUNTIME' if token=='RuntimeException' else 'ERROR')
            else:
                require(original['rule']=='AvoidInstanceofChecksInCatchClause','no foreign rule')
                if token=='StorageIoException':
                    role='REASON_SANITIZATION';require('getSuppressed().length == 0' in line,'reason contract checks prior suppression')
                else:
                    require(token=='IOException','actual IO priority discriminator')
                    role='PRIMARY_IO_PRIORITY' if line[:column-1].endswith('primary instanceof ') else 'SECONDARY_IO_PRIORITY'
                    require(line[:column-1].endswith(('primary instanceof ','secondary instanceof ')),'actual exception variable')
            require(item['semanticRole']==role and item['contextLines']==lines[max(0,line_number-4):line_number+3],'independently derived semantic role/context')
            d=item['designReference'];require(d['path']==design_path and d['originMain']=='8b91944df5820535e23ba2469740f1c0aa94c447' and d['sha256']==data.sha(design) and d['sections']==['SSC063','SSC308'],'approved exact design')
            require(bool(item['rationale']) and bool(item['testReferences']) and all((v['classname'],v['method']) in cases and v['postSha256']=='64716d82a4588387921fc49a0cdb423c79b661c22429a7a5662ab56edcac5a5f' for v in item['testReferences']),'actual relevant PT references, not new execution')
            require(item['proposedDisposition']=='REVIEWED_DESIGN_REQUIRED_BOUNDARY_RAW_RETAINED' and item['rawRetained'] is True and item['qualityGatePass'] is False and item['currentWholeJoinPending'] is True and item['applicabilityAcceptedByWholeGate'] is False and item['productionChanged'] is False and item['rulesOrSuppressionChanged'] is False and type(item['productTestsExecutedByReview']) is int and item['productTestsExecutedByReview']==0,'no suppression/whole gate inflation')
        require(len(seen)==14 and sum(seen.values())==18 and sum(v-1 for v in seen.values())==4,'duplicates preserved, not made into fewer warnings')
    contract(m,rows);labels=[]
    vectors=[('source',lambda v,r:v.update(source='0'*40)),('raw-erased',lambda v,r:r.pop()),('duplicate-substitution',lambda v,r:r.__setitem__(1,copy.deepcopy(r[0]))),('wrong-token',lambda v,r:r[0].update(sourceToken='IOException')),('wrong-role',lambda v,r:r[0].update(semanticRole='SECONDARY_RUNTIME')),('invented-PT',lambda v,r:r[0]['testReferences'][0].update(method='notRun')),('suppression',lambda v,r:v.update(rulesOrSuppressionChanged=True)),('raw-gate-zero',lambda v,r:v.update(rawQualityGateExit=0)),('whole-pending-erased',lambda v,r:r[0].update(currentWholeJoinPending=False)),('bool-count',lambda v,r:v.update(reviewedRows=True))]
    for label,change in vectors:
        wrong,changed=copy.deepcopy(m),copy.deepcopy(rows);change(wrong,changed)
        try:contract(wrong,changed)
        except ValueError:labels.append(label)
        else:raise ValueError('false source review accepted')
    verify(m['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=REVIEW[1],reviewSha256=m['reviewSha256'],rawFindingRows=18,uniqueFindingSignatures=14,duplicateRawOccurrencesRetained=4,reviewedRows=18,metadataNegativeVectors=len(labels),nonVacuousLabels=labels,sourceRoleDerivedIndependently=True,rawQualityGateExit=1,actualApplicableViolations=None,qualityGatePass=False,currentWholeJoinPending=True,productTestsExecuted=0,analyzersReexecuted=False,sourceOrRulesChanged=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
