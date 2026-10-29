"""Metadata-only enum role correction; no Product execution, cast, reflection fixture or original witness retry."""
import copy
import json
from pathlib import Path
import re
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg9666_pagination_static as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL_PIN='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
OUT=data.BASE/'PG14586-animation-category-type-role-audit-v1'
SLOT=run.WORK/'pg14586-animation-category-type-role-audit-v1'
EXPECTED={'AnimationListCategory':['MAIN','OVA'],'AnimationCategory':['MAIN','SUBTRACK','OVA'],'VideoCategory':['MAIN','SUBTRACK','OVA','OPENING']}
PREFIX='dev.codex.schubert.nk.protocol.layout.semantic.'

def contract(value,expected):
    if json.dumps(value,sort_keys=True)!=json.dumps(expected,sort_keys=True):raise ValueError('enum roles and compiler stop must remain distinct')

def main():
    invocation=capture(__file__);assert not OUT.exists() and not SLOT.exists()
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',NORMAL_PIN)
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    jar=Path(normal['jars']['protocol']['path']);assert data.sha(jar.read_bytes())==normal['jars']['protocol']['sha256']
    stop=data.read_checked(data.BASE/'PG14585-animation-category-compile-stop-v1/manifest.json','ca80d8e80a67ba57fc0a4cdc2f6c4d181d7e122efef9180e07575836ef33d9ed')
    assert stop['compilerActualExit']==1 and stop['productJvmStarted'] is False and stop['productTestsExecuted']==0 and stop['productBugReproduced'] is False
    source_roles={};source_hashes={};class_hashes={}
    with zipfile.ZipFile(jar) as z:
        for name in EXPECTED:
            path='src/schubert-nk-protocol/src/main/java/'+PREFIX.replace('.','/')+name+'.java'
            raw=(data.ROOT/path).read_bytes();assert data.sha(raw)==hashes[path]
            source_roles[name]=re.findall(r'^  ([A-Z_]+)\("',raw.decode(),re.M)
            source_hashes[path]=data.sha(raw);class_hashes[name]=data.sha(z.read(PREFIX.replace('.','/')+name+'.class'))
    assert source_roles==EXPECTED
    records={}
    for name,expected_type in [('AnimationRecord','AnimationCategory'),('VideoDescriptorResponseData','VideoCategory')]:
        path='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/media/'+name+'.java'
        raw=(data.ROOT/path).read_bytes();assert data.sha(raw)==hashes[path]
        text=raw.decode();types=re.findall(r'\b(\w+) category[,)]',text)
        assert types==[expected_type] and 'Objects.requireNonNull(category, "category")' in text
        records[name]=types[0];source_hashes[path]=data.sha(raw)
    SLOT.mkdir();run.SLOT=SLOT
    stage=run.step('javap-enum-roles',[str(run.TC/'jdk-25.0.4/bin/javap'),'-public','-classpath',str(jar),*[PREFIX+n for n in EXPECTED]],SLOT)
    assert stage['actualExit']==0 and not stage['timedOut']
    output=(SLOT/'javap-enum-roles.stdout').read_text()
    class_roles={name:re.findall('public static final '+re.escape(PREFIX+name)+r' ([A-Z_]+);',output) for name in EXPECTED}
    assert class_roles==EXPECTED
    facts=dict(enumRoles=class_roles,recordCategoryTypes=records,compilerActualExit=1,productJvmStarted=False,productTestsExecuted=0,productBugReproduced=False)
    expected=dict(enumRoles=EXPECTED,recordCategoryTypes={'AnimationRecord':'AnimationCategory','VideoDescriptorResponseData':'VideoCategory'},compilerActualExit=1,productJvmStarted=False,productTestsExecuted=0,productBugReproduced=False)
    contract(facts,expected);labels=[]
    for label,change in [('role-swapped',lambda v:v['recordCategoryTypes'].update(AnimationRecord='VideoCategory')),('opening-in-list',lambda v:v['enumRoles']['AnimationCategory'].append('OPENING')),('opening-erased-video',lambda v:v['enumRoles']['VideoCategory'].remove('OPENING')),('compiler-as-product',lambda v:v.update(productJvmStarted=True)),('compiler-as-pass',lambda v:v.update(compilerActualExit=0))]:
        wrong=copy.deepcopy(facts);change(wrong)
        try:contract(wrong,expected)
        except ValueError:labels.append(label)
        else:raise ValueError('conflated roles accepted')
    matrix=[dict(request=r,record=c,expected=(r,c) in {('MAIN','MAIN'),('MAIN','SUBTRACK'),('OVA','OVA')},actualStaticPredicate=(r=='OVA')==(c=='OVA')) for r in EXPECTED['AnimationListCategory'] for c in EXPECTED['AnimationCategory']]
    assert len(matrix)==6 and all(v['expected']==v['actualStaticPredicate'] for v in matrix)
    assert data.sha(jar.read_bytes())==normal['jars']['protocol']['sha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_PIN,facts=facts,sourceHashes=source_hashes,enumClassHashes=class_hashes,javapStage=stage,staticDomainMatrix=matrix,metadataNegativeVectors=len(labels),negativeLabels=labels,productTestsExecuted=0,productBugReproduced=False,originalFailedWitnessNotReexecuted=True,typeCircumventionAttempted=False,productionChanged=False,formalUpdated=False,newAccepted=0,bug='BUG-2104',ykt='YKT-1851',originalHypothesisResolution='BUG2103_NON_APPLICABLE_ENUM_ROLES_DISTINCT'))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
