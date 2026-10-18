"""Hash-bound current residuals; source/test text references are hints, never acceptance."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
SOURCE='a2ecc77ca312c383246c94ea692c4db7487112cd'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5112-corrected-bootstrap-native-v1'
OUT=PUBLIC.parent/'PG5118-batch-residual-map-v1'
COUNTERS=('LINE','METHOD','CLASS','BRANCH')
MANIFEST_SHA='60dadc92cf4fa7ff66427348675d0b9ad2f9e1d9b3f34e29d19d95868f105773'


def counters(element):
    result={k:{'missed':0,'covered':0}for k in COUNTERS}
    seen=set()
    for n in element.findall('counter'):
        k=n.attrib['type']
        if k not in result:continue
        if k in seen:raise ValueError('one exact counter per kind')
        seen.add(k)
        value={a:int(n.attrib[a])for a in ('missed','covered')}
        if any(v<0 for v in value.values()):raise ValueError('nonnegative actual counters required')
        result[k]=value
    return result


def parse_report(raw):
    root=ET.fromstring(raw)
    if root.tag!='report':raise ValueError('one JaCoCo report required')
    total=counters(root);sums={k:{'missed':0,'covered':0}for k in COUNTERS}
    rows=[];seen=set();source_lines={'missed':0,'covered':0};source_seen=set()
    for package in root.findall('package'):
        for source in package.findall('sourcefile'):
            key=(package.attrib.get('name'),source.attrib['name'])
            if key in source_seen:raise ValueError('unique sourcefile within package required')
            source_seen.add(key)
            lines_seen=set();actual={'missed':0,'covered':0}
            for line in source.findall('line'):
                nr,mi,ci=(int(line.attrib[k])for k in ('nr','mi','ci'))
                if nr<=0 or nr in lines_seen or min(mi,ci)<0 or mi+ci==0:
                    raise ValueError('unique positive source line and instruction counts required')
                lines_seen.add(nr)
                actual['covered'if ci>0 else'missed']+=1
            if actual!=counters(source)['LINE']:
                raise ValueError('source line instructions reconcile to declared LINE')
            for field in source_lines:source_lines[field]+=actual[field]
        for cls in package.findall('class'):
            name=cls.attrib['name'];source=cls.attrib.get('sourcefilename')
            if name in seen or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$/]*',name)or any(not part for part in name.split('/')):
                raise ValueError('unique canonical physical class required')
            seen.add(name)
            if source is not None and not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*\.java',source):
                raise ValueError('canonical source filename required')
            count=counters(cls)
            for k in COUNTERS:
                for a in ('missed','covered'):sums[k][a]+=count[k][a]
            if not any(count[k]['missed']for k in COUNTERS):continue
            methods=[];identities=set()
            for method in cls.findall('method'):
                identity=(method.attrib['name'],method.attrib['desc'])
                if identity in identities:raise ValueError('unique method descriptor required')
                identities.add(identity)
                m=counters(method)
                if any(m[k]['missed']for k in COUNTERS):
                    methods.append({'name':identity[0],'descriptor':identity[1],
                                    'line':int(method.attrib['line'])if'line'in method.attrib else None,
                                    'counters':m,'branchOutcome':'UNKNOWN_REQUIRES_CODE_OR_BYTECODE_AND_INDEPENDENT_PT'})
            rows.append({'class':name,'sourceFilename':source,'counters':count,'methods':methods})
    if source_lines!=total['LINE']or any(sums[k]!=total[k]for k in COUNTERS if k!='LINE'):
        raise ValueError('source LINE and additive class counters reconcile with immutable root counters')
    if any(sums['LINE'][k]<source_lines[k]for k in source_lines):
        raise ValueError('class LINE occurrences cannot be below unique source lines')
    return {'counters':total,'classes':sorted(rows,key=lambda v:(-v['counters']['LINE']['missed'],v['class'])),
            'physicalReportedCodeClasses':len(seen),'affectedClasses':len(rows),
            'affectedMethods':sum(len(r['methods'])for r in rows),'counterReconciled':True,
            'lineReconciliation':{'sourceUnique':source_lines,'classOccurrences':sums['LINE'],
                                  'classOverlapDelta':{k:sums['LINE'][k]-source_lines[k]for k in source_lines}}}


def source_hints(row,tests):
    filename=row['sourceFilename']
    if filename is None:
        return {'source':None,'traceStatus':'MISSING_SOURCE_FILENAME','possibleTests':[]}
    relative=Path('src/schubert-nk-batch/src/main/java')/row['class'].rpartition('/')[0]/filename
    path=ROOT/relative
    if path.is_symlink()or not path.resolve().is_relative_to(ROOT/'src/schubert-nk-batch/src/main/java')or not path.is_file():
        raise ValueError('actual source within current batch module required')
    raw=path.read_bytes();simple=row['class'].rpartition('/')[2].split('$')[0]
    refs=[name for name,text in tests.items()if re.search(r'\b'+re.escape(simple)+r'\b',text)]
    tags=sorted(set(re.findall(r'\b(?:SS[0-9]{3}|SSC[0-9]{3}|UI[0-9]{3}|OPS[0-9]{3}|PT-[A-Za-z0-9_.-]+|PT[0-9]{3,})\b',raw.decode())))
    return {'source':relative.as_posix(),'sourceSha256':hashlib.sha256(raw).hexdigest(),
            'sourceReferenceHints':tags,'possibleTests':sorted(refs),
            'traceStatus':'TEXT_HINTS_ONLY_NEEDS_SEMANTIC_REQUIREMENT_AND_TESTID_MAPPING',
            'testReferenceIsExecutionProof':False}


def main():
    if (subprocess.check_output(['git','diff',SOURCE,'HEAD','--','src','pom.xml','.mvn','mvnw','program/characterization'])
            or subprocess.check_output(['git','diff','HEAD','--','src','pom.xml','.mvn','mvnw','program/characterization'])):
        raise ValueError('same current source/Test/settings first')
    manifest_raw=(PUBLIC/'manifest.json').read_bytes();manifest=json.loads(manifest_raw)
    module=next(v for v in manifest['modules']if v['module']=='batch')
    raw=(PUBLIC/'coverage/batch/site/jacoco/jacoco.xml').read_bytes()
    if (hashlib.sha256(manifest_raw).hexdigest()!=MANIFEST_SHA or manifest['productionSource']!=SOURCE
            or manifest.get('oldSourceNativeImported')is not False
            or (manifest.get('tests'),manifest.get('suites'),manifest.get('mainClasses'))!=(3791,553,1650)):
        raise ValueError('same production source measurement first')
    if hashlib.sha256(raw).hexdigest()!=module['coverageXmlSha256']:
        raise ValueError('hash-qualified public current XML required')
    report=parse_report(raw)
    if report['counters']!=manifest['moduleCounters']['batch']:
        raise ValueError('root matches actual native measurement counters')
    tests={p.relative_to(ROOT).as_posix():p.read_text()for p in(ROOT/'src/schubert-nk-batch/src/test/java').rglob('*.java')}
    for row in report['classes']:row.update(source_hints(row,tests))
    value={'schema':'PG5118_RESIDUAL_MAP_V1','productionSource':SOURCE,
           'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           'nativePublicManifestSha256':hashlib.sha256(manifest_raw).hexdigest(),
           'coverageXmlSha256':hashlib.sha256(raw).hexdigest(),'report':report,
           'coverageExclusionsAdded':False,'unknownBranchesClosed':False,'testsExecuted':0,
           'vmActions':0,'acceptedLeafDelta':0,'effortPercent':None,'formalAccepted':False}
    OUT.mkdir(mode=0o700)
    with(OUT/'report.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'reportSha256':hashlib.sha256((OUT/'report.json').read_bytes()).hexdigest(),
                      'affectedClasses':report['affectedClasses'],'affectedMethods':report['affectedMethods'],
                      'missed':{k:report['counters'][k]['missed']for k in COUNTERS},'testsExecuted':0,'formalAccepted':False}))
    return 0


if __name__=='__main__':raise SystemExit(main())
