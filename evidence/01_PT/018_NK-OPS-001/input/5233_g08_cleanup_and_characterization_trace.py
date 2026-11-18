"""Trace two JDBC classes and two offline tool classes to their independently fixed case IDs."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import runpy

HERE=Path(__file__)
A=runpy.run_path(str(HERE.with_name('5215_g08_four_source_test_ids.py')))
E,D=map(A.get,('E','D'))
read,sha,ref,git,checked=map(A.get,('read','sha','ref','git','checked'))
START=D/'601_WBS66短期実行_20261117/511_G08Cleanupと比較工具のtrace開始.json'
BAT=Path('evidence/01_PT/017_NK-BAT-001')
CHR=Path('evidence/01_PT/020_NK-CHR-001')
SSCHR=Path('documents/300_SS/350_運用・品質/355_Characterization Test実行準備・PG開始gate.md')
UICHR=next(Path('documents/200_UI').rglob('264_*.md'))


def bind_source(proof_path,current,run,hashes):
    path=Path(proof_path)
    assert sha(git('show',f'{run}:{path}'))==hashes[str(path)]
    assert git('show',f'{current}:{path}')==path.read_bytes()==git('show',f'{run}:{path}')
    return ref(path)


def cases(xml):
    rows=ET.parse(xml).getroot().findall('testcase')
    assert not any(k.tag in ('failure','error','skipped') for r in rows for k in r)
    keyed={(r.get('classname'),r.get('name')) for r in rows}
    assert len(rows)==len(keyed)
    return keyed


def original_ids(file,test_name):
    values=re.findall(r'\|(CLN(?:QUERY|PORT)\d{3})\|'+test_name+r'\.(\w+)\|',file.read_text())
    assert len(values)==9
    return values


def link_tests(mapping,classname,xml,source):
    assert len(mapping)==len(dict(mapping))
    def bind(ident,name):
        assert (classname,name+'()') in xml
        assert re.search(r'\bvoid\s+'+re.escape(name)+r'\s*\(',source.read_text())
        return dict(testId=ident,method=name)
    return [bind(ident,name) for ident,name in mapping]


def docs(main,owner):
    assert owner[str(main)]['path']==str(main)
    tracks=owner[str(main)]
    return dict(owner=tracks['owner'],costOwner=tracks['costOwner'],qualifiedClass=tracks['class'].replace('/','.'))


def sql_trace(proof_path,m,head,owner,canonical_docs):
    post_path=checked(m['proofs']['post'])
    post=read(post_path)
    profile=read(checked(post['config']))
    xml=post_path.with_name('original-TEST-junit-jupiter.xml')
    assert post['files'][xml.name]==ref(xml)['sha256'] and post['tests']==18
    assert ref(post_path.with_name('jacoco.exec'))['sha256']==post['files']['jacoco.exec']
    methods=cases(xml)
    assert len(methods)==18
    sql_doc=Path(A['SS'])
    details=[('CleanupRepository','CleanupQueryPortTest','705_Cleanup基底query_単体テスト仕様書.md'),
             ('CleanupStepRepository','CleanupStepPortTest','703_Cleanupステップ_単体テスト仕様書.md')]
    modified=BAT/'4695_CleanupRepository固定statement表の単体仕様.md'
    assert 'PG-D-1186' in A['LOCAL'].read_text()
    records=[]
    for main,test,table in details:
        [prod]=[Path(name) for name in profile['mainSources'] if name.endswith('/'+main+'.java')]
        [fixture]=[Path(r['path']) for r in profile['testSources'] if r['path'].endswith('/'+test+'.java')]
        run=post['source']
        product_pin,fixture_pin=[bind_source(i,head,run,post['inputHashes']) for i in (prod,fixture)]
        classname=docs(prod,owner)['qualifiedClass']
        ids=link_tests(original_ids(BAT/table,test),classname.rsplit('.',1)[0]+'.'+test,methods,fixture)
        crc=post['classIds'][classname.replace('.','/')]
        coverage=m['measurement']['target'][classname.replace('.','/')]
        assert all(counter['missed']==0 for counter in coverage.values())
        records.append(dict(main=product_pin,test=fixture_pin,owner=docs(prod,owner),
             spec=[ref(BAT/table),ref(modified),canonical_docs[str(sql_doc)]],decision='PG-D-1186',related=['BUG-3237','YKT-2683'],
             currentXml=ref(xml),singleExec=ref(post_path.with_name('jacoco.exec')),
             scopeEvidence=ref(proof_path),run=post['run'],unitSource=run,crc=crc,tests=ids))
    return records


def tool_trace(proof_path,p,head,owner,canonical_docs):
    unit_path=checked(p['unit'])
    unit=read(unit_path)
    xml=unit_path.parent/'xml/TEST-junit-jupiter.xml'
    assert unit['xmlHashes'][xml.name]==ref(xml)['sha256']
    methods=cases(xml)
    assert len(methods)==144
    spec=CHR/'032_比較定義一意性の単体仕様.md'
    test_base=Path('program/characterization/tests/java/dev/codex/schubert/characterization')
    prod_base=Path('program/characterization/src/main/java/dev/codex/schubert/characterization')
    definitions=[
      ('ArtifactComparator',[('PT-CHR-DEF015','rejectsRepeatedCaseDefinitionEvenWhenTwentyFourCasesStillCompare'),
                              ('PT-CHR-DEF016','rejectsRepeatedDifferenceDefinitionEvenWhenSixteenRulesStillMatch')],
        'PG-D-1187',['BUG-3308','YKT-2696']),
      ('GateCli',[('PT-CHR-PRE001','preflightValidatesFilesPermissionsStorageNetworkAndPorts')],
        'PG-D-1188',['BUG-3309','BUG-3310','BUG-3311','YKT-2697'])]
    raw=checked(p['raw']['evidence'])
    report={bits[1]:bits for row in raw.read_text().splitlines()
            if (bits:=row.split('\t')) and bits[0]=='CLASS'}
    rows=[]
    for name,ids,decision,issues in definitions:
        main,test=prod_base/(name+'.java'),test_base/(name+'Test.java')
        main_pin,test_pin=[bind_source(i,head,unit['source'],unit['inputHashes']) for i in (main,test)]
        meta=docs(main,owner)
        java=meta['qualifiedClass']
        row=report[java.replace('.','/')]
        assert row[3]=='true' and decision in A['LOCAL'].read_text()
        assert all(n in spec.read_text() for n,_ in ids)
        coverage={k:dict(missed=int(miss),covered=int(hit)) for k,miss,hit in
                  (item.split(':') for item in row[6:])}
        assert bool(coverage['METHOD']['missed'])==(name=='GateCli')
        rows.append(dict(main=main_pin,test=test_pin,owner=meta,
            spec=[ref(spec),canonical_docs[str(SSCHR)],canonical_docs[str(UICHR)]],decision=decision,related=issues,
            currentXml=ref(xml),singleExec=ref(unit_path.with_name('jacoco.exec')),
            scopeEvidence=ref(proof_path),run=unit['run'],unitSource=unit['source'],
            crc=row[2],tests=link_tests(ids,java+'Test',methods,test),rawTarget=coverage))
    return rows


def main():
    start=read(START)
    v=start['values']
    head=v['source']
    assert git('rev-parse','HEAD').decode().strip()==head
    assert git('rev-parse','origin/dev-foundation').decode().strip()==head
    first,second,scan=map(checked,v['oracleReferences'])
    assert read(scan)['qualifiedRangeOnly'] and read(scan)['throughCommit']==git('rev-parse','HEAD^').decode().strip()
    canonical=git('rev-parse','origin/main').decode().strip()
    canonical_docs={}
    for doc in (Path(A['SS']),SSCHR,UICHR):
        canonical_bytes=git('show',f'{canonical}:{doc}')
        parent=git('show',f'{head}:{doc}')
        assert parent==doc.read_bytes()
        if canonical_bytes!=parent:
            patch=git('diff','-U0',head,canonical,'--',str(doc)).decode()
            assert doc==Path(A['SS']) and patch.count('@@')==2 and 'SSC427' in patch
            assert not re.search(r'(?im)^[+-][^+-].*cleanup',patch)
        canonical_docs[str(doc)]=dict(path=str(doc),sha256=sha(canonical_bytes),commit=canonical,
                                      sameLocalBytes=canonical_bytes==parent)
    owner={p['path']:p for p in read(A['REGISTRY'])['artifacts']}
    rows=sql_trace(first,read(first),head,owner,canonical_docs)+tool_trace(second,read(second),head,owner,canonical_docs)
    assert len({test['testId'] for row in rows for test in row['tests']})==21
    assert len({row['run'] for row in rows})==2
    bug_text,ykt_text=A['LEDGER'].read_text(),A['YKT'].read_text()
    assert all(issue in (bug_text if issue.startswith('BUG-') else ykt_text)
               for row in rows for issue in row['related'])
    out=E/v['run']/'manifest.json'
    value=dict(actualExit=0,source=head,canonicalDesign=canonical,currentCore=v['productionCoreMain'],
       startEvent=start['eventId'],ownerRegistry=ref(A['REGISTRY']),mappedMain=4,mappedTestIds=21,
       distinctOriginalExecs=2,rows=rows,oldDefinitionsMapped=19,newDefinitionsMapped=2,
       reusedOriginalJdbc18=True,actualTestInvocations=0,coverageAdded=0,execUnion=False,
       productOrBusinessActions=0,wholeG08Accepted=False,newAcceptance=0,verifier=ref(HERE),
       terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with out.open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(ref(out))


if __name__=='__main__':
    main()
