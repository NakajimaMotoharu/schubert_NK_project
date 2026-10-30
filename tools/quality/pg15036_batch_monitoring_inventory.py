"""Passive full-package inventory: original41 suites/40 Code Sources plus explicit package metadata."""
import copy
import json
import re
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

OUT=data.BASE/'PG15036-batch-monitoring-inventory-v1'
REG=('PG15026-current1319-batch-standard-registry-v1','4b1299e57ecb5616727e338e0ef8bc080e5b38fb70c61bd1789df696aebbfbe0')
REG_POST=('PG15028-current1319-batch-standard-registry-post-v1','e7fcc951b33f0ca4dbbbc46ace25e41377a5c81033cdee70a657c0edc7846892')
PROOFS=[
 ('PG14930-monitoring-pure-fifty-five-post-v1','431b26429dbe7d2e83789988d7fdb8b71c40048c52dd85b81ced32330330e1ea','PG14932-monitoring-pure-independent-v1','9136a5f42d2ec889e6c5c0ffb0199a6375dab9663a9aee6f52053e67d2c228be',55),
 ('PG14948-timed-threshold-pure-forty-four-post-v1','096655b397d39cddaf0fb347b2bd9c9babee76eafeaece41e1df492852c8afa6','PG14950-timed-threshold-pure-independent-v1','e61bd1a37df52b73065bda2c523f1620175a20150526b7a8ba51090a664f2afe',44),
 ('PG14966-fake-source-clock-fifty-seven-post-v1','a182513b3388ad70a7d02b3057365f4ebef7805b4e68360f4f6fbe8e12c8e176','PG14968-fake-source-clock-independent-v1','400fd583e176179976e4c38fa7da54d349cb3fed6bf38b73afb21f27cfc9ae17',57),
 ('PG14984-supplied-health-monitors-eighty-one-post-v1','0dcffdc4bc4465258531ff6ac5a70eaea7d9a8e2f40bd166874283fc809193ce','PG14986-supplied-health-independent-v1','b1a4ca65086c1f27aa4961bd3e235ed19da60b1052a9630f024763d66b3ef828',81),
 ('PG15002-batch-meter-contracts-thirty-eight-post-v1','575f5f18519002b094537f0fb5145ab9d79a59c5639aae30d9eee96fb21cb695','PG15004-batch-meter-contracts-independent-v1','1cde8b756eb3d73b6dc550ed15288271954cd9bb4b68cb62dbff3ce179776533',38),
 ('PG15020-batch-standard-sdk-one-hundred-ten-post-v1','f0c735deb6be7e65561c9d0ee28861d554b76ad1d546935ef1970618b10d5e60','PG15022-batch-standard-sdk-independent-v1','8407a340eee0ca56a268c7c42c94a58ad56764b82623ef9f764ae983eab43cb0',110)]
PREFIX='dev/codex/schubert/nk/batch/monitoring/'
MAIN='src/schubert-nk-batch/src/main/java/'
TEST='src/schubert-nk-batch/src/test/java/'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(value):return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only metadata inventory')
    r,p=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [REG,REG_POST]]
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(r['actualExit']==p['actualExit']==normal['actualExit']==0 and r['source']==p['source']==normal['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' and p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==33,'genuine fixed source registry qualification')
    hashes=normal['begin']['inputHashes'];snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    main_paths={path:h for path,h in hashes.items() if path.startswith(MAIN+PREFIX)}
    test_paths={path:h for path,h in hashes.items() if path.startswith(TEST+PREFIX)}
    require(len(main_paths)==len(test_paths)==41,'all normal Main and Test files')
    for path,h in {**main_paths,**test_paths}.items():require(data.sha((data.ROOT/path).read_bytes())==data.sha((snapshot/path).read_bytes())==h,'all original current/snapshot inputs match')
    meta_name=PREFIX+'package-info';source_names={path[len(MAIN):-5] for path in main_paths};business=source_names-{meta_name}
    units={name:value for name,value in r['fullSourceUnits'].items() if name.startswith(PREFIX)}
    require(set(units)==business and len(business)==40,'every complete business Source, no parent helper promotion')
    declared={}
    for path in test_paths:
        text=(data.ROOT/path).read_text();suite=path[len(TEST):-5].replace('/','.')
        names=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\s*\(',text)
        require(text.count('@Test')==len(names)>0 and len(set(names))==len(names),'all original whole declarations')
        declared[suite]=names
    expected_cases={(suite,name) for suite,names in declared.items() for name in names}
    current_cases={(c['classname'],c['name']) for c in r['cases'] if c['classname'] in declared}
    require(expected_cases==current_cases and len(current_cases)==385,'all41 original suite385 methods present once')
    actual_cases=set();proof_sources=set();proofs=[];physical={};sessions=set();execs=set()
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,ind,ind_pin,count in PROOFS:
        post,independent=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [(folder,pin),(ind,ind_pin)]]
        require(post['actualExit']==independent['actualExit']==0 and post['source']==independent['source']==r['source'] and independent['postSha256']==pin and post['tests']==independent['tests']==count and post['singleSession'] is True and post['crcMismatch']==0 and post['coverageExecUnion'] is False,'six genuine qualified own execs, not a fabricated module run')
        new={(c['classname'],c['name']) for c in post['cases']};require(len(new)==count and not new&actual_cases and not post['fullSourceUnits'].keys()&proof_sources,'disjoint original methods and complete Sources');actual_cases|=new;proof_sources.update(post['fullSourceUnits'])
        xml_cases=set()
        for filename,h in post['xmlHashes'].items():
            value=(data.BASE/folder/filename).read_bytes();require(data.sha(value)==h,'original XML bytes');root=ET.fromstring(value);suite=root.get('name')
            require(suite in declared and int(root.get('tests'))==len(declared[suite]) and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'all original whole suites FES0')
            for c in root.findall('testcase'):
                require(not list(c),'actual PASS only');xml_cases.add((c.get('classname'),c.get('name')))
        require(xml_cases==new,'all post cases backed by actual XML')
        for name,u in post['fullSourceUnits'].items():
            value=units[name];require(value['post']==folder and value['postSha256']==pin and value['physical']==u['physical'] and value['counters']==u['totals'] and value['four100'] is u['four100'] and value['branchNaturallyZero'] is (u['branchNaturallyZero'] and u['threeCounter100']),'all final per-Source counter and original proof identities')
        for path,owned in post['owners'].items():
            if path in main_paths or path in test_paths:require(r['owners'][path]==owned and owned['sha256']==hashes[path] and all(owned[k]==v for k,v in canonical(path,logical).items()) and owned['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','owner role retained, not formal acceptance')
        require(not physical.keys()&post['physicalClasses'].keys(),'all Source physical classes disjoint');physical.update(post['physicalClasses']);sessions.add(post['sessionIdentity']);execs.add(post['execSha256'])
        for v in [post,independent]:verify(v['invocation'])
        proofs.append(dict(post=folder,sha256=pin,independent=ind,independentSha256=ind_pin,tests=count))
    require(actual_cases==expected_cases and proof_sources==business and len(sessions)==len(execs)==6,'six existing execs cover all declared package contracts without replay')
    class_inventory={}
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        all_classes={v[:-6] for v in jar.namelist() if v.startswith(PREFIX) and v.endswith('.class')}
        require(all_classes==set(physical)|{meta_name} and len(all_classes)==72,'all72 real Jar entries including annotation metadata')
        for name in all_classes:
            value=jar.read(name+'.class');parsed=code.decode(value,name+'.class');class_inventory[name]=dict(sha256=data.sha(value),**parsed)
            require(data.sha((snapshot/'src/schubert-nk-batch/target/classes'/(name+'.class')).read_bytes())==data.sha(value),'actual snapshot class equals Jar')
            if name==meta_name:require(parsed['sourceFile']=='package-info.java' and parsed['fields']==0 and parsed['methods']==[],'package annotation has no executable Code or counters')
            else:require(physical[name]==data.sha(value) and any(m['hasCode'] for m in parsed['methods']) and name.split('$',1)[0] in business,'all71 actual executable Code, no hidden exclusions')
    metadata_source=(data.ROOT/(MAIN+meta_name+'.java')).read_text()
    require('@org.jspecify.annotations.NullMarked' in metadata_source and 'package dev.codex.schubert.nk.batch.monitoring;' in metadata_source,'explicit null contract annotation, not discarded scope')
    totals={k:{role:sum(v['counters'][k][role] for v in units.values()) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==dict(LINE=dict(missed=0,covered=1166),METHOD=dict(missed=0,covered=263),CLASS=dict(missed=0,covered=71),BRANCH=dict(missed=0,covered=537)),'disjoint per-Source reference totals, never exec union')
    require(sum(v['four100'] for v in units.values())==36 and sum(v['branchNaturallyZero'] for v in units.values())==4 and all(v['four100'] or v['branchNaturallyZero'] for v in units.values()),'36 four100 and four natural B0 N/A, not40 four100')
    expected=dict(source=r['source'],tests=385,suites=41,normalMainSourceFiles=41,businessSourcePrograms=40,executablePhysical=71,normalPhysicalClasses=72,four100SourcePrograms=36,naturallyZeroBranchSourcePrograms=4,packageMetadataSources=1,packageMetadataPhysical=1,packageMetadataCounterStatus='ZERO_DENOMINATOR_NA_NOT_FOUR100',sourcePins=main_paths,testPins=test_paths,cases=[dict(classname=c,name=n) for c,n in sorted(expected_cases)],sourceUnits=units,classInventory=class_inventory,originalProofs=proofs,existingProductJvms=6,disjointSourceReferenceTotals=totals,sourceProofsRemainSeparateExecs=True,coverageExecUnion=False,productTestsExecutedByInventory=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,batchModuleAccepted=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,effortPercent=None)
    def contract(v):require(wire(v)==wire(expected),'all exact typed counts/scope/source/Code/proof/limits immutable')
    labels=[]
    for key,value in [('source','OLD'),('tests',384),('suites',40),('businessSourcePrograms',41),('executablePhysical',72),('normalPhysicalClasses',71),('four100SourcePrograms',40),('naturallyZeroBranchSourcePrograms',0),('packageMetadataSources',0),('packageMetadataCounterStatus','FOUR100'),('sourceUnits',{}),('classInventory',{}),('cases',[]),('testPins',{}),('sourceProofsRemainSeparateExecs',False),('coverageExecUnion',True),('productTestsExecutedByInventory',385),('newAccepted',1),('formalUpdated',True),('whole451Accepted',True),('batchModuleAccepted',True),('effortPercent',100)]:
        bad=copy.deepcopy(expected);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false full-package inventory accepted '+key)
    contract(expected)
    for v in [r,p]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,registryReference=list(REG),registryPostReference=list(REG_POST),semanticNegativeVectors=len(labels),negativeLabels=labels,**expected));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
