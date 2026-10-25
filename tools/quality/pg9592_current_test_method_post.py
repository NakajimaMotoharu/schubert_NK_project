"""Independent classfile annotations versus source declarations; not JUnit discovery or execution."""
from collections import Counter,defaultdict
import copy
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
SUBJECT=BASE/'PG9590-current-test-method-inventory-v1'
SUBJECT_SHA='0ecd6877f4666d4cd42d15b4af80d1a18681403766be221377bb842998906a9e'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9592-current-test-method-post-v1'
OUT=BASE/'PG9592-current-test-method-post-v1'
HELPER=ROOT/'tools/quality/architecture/PublicTestMethodMetadataAudit.java'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1944_G13TestMethodInventory_現source分母仕様.md'
SPEC_SHA='54118e47ab989b30faa6073be88de5f07a70207c56e11fd2dbdc2268f17325b6'

def source_key(row):
    module=row['path'].split('/')[1].removeprefix('schubert-nk-')
    return (module,row['className'].replace('.','/'),row['method'],row['parameterCount'])

def validate(observed,expected):
    if observed!=expected:raise ValueError('exact independent source/class/annotation/descriptor binding required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    assert data.sha(SPEC.read_bytes())==SPEC_SHA
    subject=data.read_checked(SUBJECT/'manifest.json',SUBJECT_SHA)
    assert subject['actualExit']==0 and subject['source']==SOURCE and subject['sourceFiles']==824
    declarations=data.read_checked(SUBJECT/'test-method-declarations.json',subject['methodDeclarationsSha256'])
    sources=data.read_checked(SUBJECT/'test-source-counts.json',subject['sourceCountsSha256'])
    assert len(declarations)==subject['methodDeclarations']==5622 and len(sources)==824
    normal=data.read_checked(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json',data.PINS['normal'][1])
    graph=data.read_checked(BASE/'PG9386-composite-reference-graph-v3/manifest.json',data.PINS['graph'][1])
    metadata=data.read_checked(BASE/'PG9386-composite-reference-graph-v3/test-class-metadata.json',graph['testMetadataSha256'])
    assert len(metadata)==1910 and graph['source']==normal['source']==SOURCE
    hashes={p:h for p,h in normal['begin']['inputHashes'].items() if '/src/test/java/' in p and p.endswith('.java')}
    assert subject['sourceHashes']==hashes and len(hashes)==824
    for path,digest in hashes.items():assert data.sha((ROOT/path).read_bytes())==data.sha((data.NORMAL/path).read_bytes())==digest
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    source_counts=Counter(r['path'] for r in declarations)
    assert sources==[dict(path=p,sourceSha256=hashes[p],ordinaryTestDeclarations=source_counts[p]) for p in sorted(hashes)]
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'reader';classes.mkdir();catalog=SLOT/'normal-test-classes.tsv'
    expected_classes={};physical_paths={}
    for row in metadata:
        module=row['module'];name=row['className'];key=(module,name)
        path=data.NORMAL/('src/schubert-nk-'+module)/'target/test-classes'/row['entry']
        assert path.resolve()==path and not path.is_symlink() and path.is_file()
        assert row['entry']==name+'.class' and data.sha(path.read_bytes())==row['sha256'] and key not in expected_classes
        expected_classes[key]=row;physical_paths[key]=path
    with catalog.open('x') as stream:
        for key,path in sorted(physical_paths.items()):stream.write(key[0]+'\t'+str(path)+'\n')
    helper_sha=data.sha(HELPER.read_bytes());steps.SLOT=SLOT;tc=ROOT.parent/'toolchain'
    stages=[steps.step('compile-class-method-reader',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(HELPER)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    stages.append(steps.step('read-class-method-annotations',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(classes),HELPER.stem,str(data.NORMAL),str(catalog)]))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'read-class-method-annotations.stdout').read_text().splitlines();assert lines[0]=='SELFTEST\t6'
    actual_classes={};method_rows=[]
    for line in lines[1:]:
        fields=line.split('\t')
        if fields[0]=='CLASS':
            _,module,name,sourcefile,digest=fields;key=(module,name);assert key not in actual_classes
            reference=expected_classes[key]
            path='src/schubert-nk-'+module+'/src/test/java/'+name.rpartition('/')[0]+'/'+sourcefile
            assert path==reference['path'] and sourcefile==reference['sourceFile'] and digest==reference['sha256'] and path in hashes
            actual_classes[key]=dict(module=module,className=name,path=path,sourceFile=sourcefile,sha256=digest)
        else:
            assert fields[0]=='TEST' and len(fields)==7
            _,module,name,method,descriptor,count,annotation=fields;key=(module,name);assert key in actual_classes
            method_rows.append(dict(module=module,className=name,method=method,descriptor=descriptor,
              parameterCount=int(count),annotationKind=annotation,path=actual_classes[key]['path']))
    assert set(actual_classes)==set(expected_classes)
    assert all(data.sha(path.read_bytes())==expected_classes[key]['sha256'] for key,path in physical_paths.items())
    ordinary=[r for r in method_rows if r['annotationKind']=='org.junit.jupiter.api.Test']
    other=[r for r in method_rows if r['annotationKind']!='org.junit.jupiter.api.Test']
    source_map=defaultdict(list);class_map=defaultdict(list)
    for r in declarations:source_map[source_key(r)].append(r)
    for r in ordinary:class_map[(r['module'],r['className'],r['method'],r['parameterCount'])].append(r)
    all_keys=set(source_map)|set(class_map);bound=[];unmatched=[]
    for key in sorted(all_keys):
        source=source_map[key];compiled=class_map[key]
        if len(source)!=1 or len(compiled)!=1:
            unmatched.append(dict(module=key[0],className=key[1],method=key[2],parameterCount=key[3],sourceDeclarations=len(source),byteDeclarations=len(compiled),
              reason='MISSING_OR_OVERLOADED_AMBIGUOUS_BINDING_NO_INFERENCE'));continue
        original=source[0];physical=compiled[0]
        assert original['path']==physical['path'] and original['sourceSha256']==hashes[physical['path']]
        bound.append(dict(**original,compiledDescriptor=physical['descriptor'],physicalClassSha256=actual_classes[(key[0],key[1])]['sha256'],
          declarationBinding='SOURCE_AST_AND_JDK_CLASSFILE_JUNIT_ANNOTATION_EXACT_NOT_EXECUTED',methodOracleNotQualifiedByThisBinding=True))
    assert len(bound)+sum(r['sourceDeclarations'] for r in unmatched)==len(declarations)
    rejected=[]
    for label,edit in (('missing',lambda x:x.pop()),('duplicate',lambda x:x.append(copy.deepcopy(x[0]))),
      ('source',lambda x:x[0].update(sourceSha256='0'*64)),('class',lambda x:x[0].update(className='Other')),
      ('descriptor',lambda x:x[0].update(compiledDescriptor='(I)V')),('parameter-count',lambda x:x[0].update(parameterCount=99)),
      ('annotation',lambda x:x[0].update(annotationKind='other.Test')),('invented-execution',lambda x:x[0].update(productExecutedByThisInventory=True))):
        changed=copy.deepcopy(bound);edit(changed)
        try:validate(changed,bound)
        except ValueError:rejected.append(label)
        else:raise AssertionError('unproved method binding accepted')
    assert data.sha(HELPER.read_bytes())==helper_sha and all(p.name.startswith(HELPER.stem) for p in classes.rglob('*.class'))
    verify(invocation);OUT.mkdir();data.write(OUT/'method-declaration-bindings.json',bound)
    data.write(OUT/'unmatched-method-declarations.json',unmatched);data.write(OUT/'other-test-annotations-unqualified.json',other)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      subjectManifestSha256=SUBJECT_SHA,specSha256=SPEC_SHA,normalManifestSha256=data.PINS['normal'][1],graphManifestSha256=data.PINS['graph'][1],
      helperSha256=helper_sha,helperStages=stages,classFileAnnotationVectors=6,metadataCounterexamples=rejected,
      sourceFiles=824,physicalTestClasses=1910,sourceOrdinaryDeclarations=len(declarations),classOrdinaryDeclarations=len(ordinary),
      exactDeclarationBindings=len(bound),unmatchedKeys=len(unmatched),otherTestAnnotationDeclarations=len(other),
      repeatedOrParameterizedInvocationsNotExpanded=True,independentMethodOracleQualificationInferred=False,
      bindingsSha256=data.sha((OUT/'method-declaration-bindings.json').read_bytes()),unmatchedSha256=data.sha((OUT/'unmatched-method-declarations.json').read_bytes()),
      otherAnnotationsSha256=data.sha((OUT/'other-test-annotations-unqualified.json').read_bytes()),
      targetClassesCompiled=0,targetClassLoading=0,targetRuntimeInvocations=0,productTestsExecuted=0,newTestIds=0,newMain=0,
      coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False)
    data.write(SLOT/'manifest.safe.json',value);data.write(OUT/'manifest.json',value)
    print(json.dumps({k:value[k] for k in ('actualExit','sourceOrdinaryDeclarations','classOrdinaryDeclarations','exactDeclarationBindings','unmatchedKeys','otherTestAnnotationDeclarations')}))
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
