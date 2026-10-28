"""Fixed-source static/class metadata only for bounded literal-only Test batches; no target execution."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import original_value, prior_normal, inverse, negative, out
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts
from pg13139_private_constant_metadata import remove_constant, selftest
import pg9666_pagination_static as runner

def read_normal(cfg,source,pin):
    value = data.read_checked(out(cfg,cfg.NORMAL_NUMBER)/'manifest.json',pin)
    assert value['source'] == source and value['actualExit'] == value['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in value['begin']['inputHashes'].items())
    return value

def static(cfg,source,normal_pin,preflight):
    invocation = capture(__file__);target = out(cfg,cfg.STATIC_NUMBER);slot = data.ROOT.parent/'pgpt-runs/PG379'/target.name.lower()
    assert not target.exists() and not slot.exists();n = read_normal(cfg,source,normal_pin)
    p = data.read_checked(data.BASE/preflight[0]/'manifest.json',preflight[1])
    assert p['actualExit'] == p['productTestsExecuted'] == 0
    assert len(p['removedFindingIds']) == cfg.EXPECTED_CORRECTIONS
    assert set(p['candidateSourceHashes']) == set(cfg.PATHS)
    assert all(n['begin']['inputHashes'][path] == sha for path,sha in p['candidateSourceHashes'].items())
    for name,sha in p['reports'].items():assert data.sha((data.BASE/preflight[0]/(name+'.xml')).read_bytes()) == sha
    jars = {item['path']:item['sha256'] for item in n['jars'].values()};assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in jars.items())
    slot.mkdir();runner.SLOT = slot;snapshot = Path(n['jars']['bootstrap']['path']).parents[3]
    mvn = runner.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    stage = runner.step('spotbugs-six',[str(mvn),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(runner.TC/'m2/repository'),'-pl',','.join('src/schubert-nk-'+r for r in ['protocol','storage','bootstrap','api','web','batch']),'-am','-DskipTests=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],snapshot,timeout=600)
    assert stage['actualExit'] == 0 and not stage['timedOut'];reports = {}
    for role,item in n['jars'].items():
        raw = (Path(item['path']).parent/'spotbugsXml.xml').read_bytes();root = ET.fromstring(raw)
        assert not [node for node in root.iter() if node.tag in ['BugInstance','MissingClass','Error']];reports[role] = data.sha(raw)
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in jars.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in n['begin']['inputHashes'].items())
    verify(invocation);target.mkdir()
    data.write(target/'manifest.json',dict(actualExit=0,source=source,invocation=invocation,normalManifestSha256=normal_pin,preflightManifestSha256=preflight[1],sourceHashes=p['candidateSourceHashes'],
        originalStaticReportsReboundWithoutReplay=True,rawStatic=p['rawStatic'],rawStaticGateExit=p['rawStaticGateExit'],spotbugsSixExit=0,spotbugsSixReports=reports,stages=[stage],
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',newAccepted=0,whole451Accepted=False))
    print(data.sha((target/'manifest.json').read_bytes()))

def shape(model):
    result = copy.deepcopy(model)
    for method in result['methods']:method.pop('codeLength')
    return result

def post(cfg,source,normal_pin,static_pin,preflight):
    invocation = capture(__file__);target = out(cfg,cfg.POST_NUMBER);slot = data.ROOT.parent/'pgpt-runs/PG379'/target.name.lower()
    assert not target.exists() and not slot.exists();n = read_normal(cfg,source,normal_pin);old = prior_normal(cfg);original = original_value(cfg)
    s = data.read_checked(out(cfg,cfg.STATIC_NUMBER)/'manifest.json',static_pin);p = data.read_checked(data.BASE/preflight[0]/'manifest.json',preflight[1])
    assert s['source'] == source and s['actualExit'] == s['productTestsExecuted'] == s['spotbugsSixExit'] == 0
    assert s['normalManifestSha256'] == normal_pin and s['preflightManifestSha256'] == preflight[1]
    assert s['rawStatic'] == p['rawStatic'] and s['rawStaticGateExit'] == p['rawStaticGateExit']
    assert old['begin']['inputHashes'].keys() == n['begin']['inputHashes'].keys()
    assert {path for path in n['begin']['inputHashes'] if old['begin']['inputHashes'][path] != n['begin']['inputHashes'][path]} == set(cfg.PATHS)
    for row in original['sources']:
        text = (data.ROOT/row['path']).read_text()
        assert inverse(row['text'],text,row['mapping']) == p['originalTokenInverses'][row['path']]
        assert negative(row['text'],text,row['mapping']) == p['negativeVectors'][row['path']]
    before,after = jar_classes(old),jar_classes(n);assert before == after and len(after) == 1843
    a,b = test_classes(old),test_classes(n);assert a.keys() == b.keys() and len(b) == 1974
    roots = {}
    for row in original['sources']:
        path = row['path'];role = path.split('/')[1].removeprefix('schubert-nk-');entry = path.split('/src/test/java/')[1][:-5]
        roots[(role,entry)] = row
    closure = {key for key in a if any(key[0] == role and (key[1] == root+'.class' or key[1].startswith(root+'$')) for role,root in roots)}
    changed = {key for key in a if a[key] != b[key]};assert changed and changed <= closure
    metadata = []
    for role,entry in sorted(closure):
        x,y = [parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry) for normal in [old,n]]
        expected = shape(x['model']);row = roots.get((role,entry[:-6]))
        if row:expected['fields'] += len(row['mapping'])
        assert shape(y['model']) == expected and x['model']['sourceFile'] == y['model']['sourceFile']
        metadata.append(dict(module=role,entry=entry,byteChanged=(role,entry) in changed,oldClassSha256=a[(role,entry)],newClassSha256=b[(role,entry)],
            oldFields=x['model']['fields'],newFields=y['model']['fields'],methodShapesUnchanged=True,
            rawCodeRepresentationEqual=x['rawCodeRepresentationSha256'] == y['rawCodeRepresentationSha256'],debugTablesEqual=x['debugTablesSha256'] == y['debugTablesSha256']))
    slot.mkdir();runner.SLOT = slot;javap = runner.TC/'jdk-25.0.4/bin/javap';javap_hash = data.sha(javap.read_bytes());stages = [];abi = {}
    for i,((role,root),row) in enumerate(roots.items()):
        outputs = []
        for label,normal in [('old',old),('new',n)]:
            cp = str(Path(normal['jars'][role]['path']).parent/'test-classes');name = str(i)+'-'+label+'-metadata'
            stage = runner.step(name,[str(javap),'-p','-constants','-s','-classpath',cp,root.replace('/','.')],slot,timeout=120)
            assert stage['actualExit'] == 0 and not stage['timedOut'];stages.append(stage);outputs.append((slot/(name+'.stdout')).read_text())
        stripped = outputs[1]
        for literal in row['mapping']:stripped = remove_constant(stripped,'private static final java.lang.String '+literal['name']+' = '+literal['literal']+';','Ljava/lang/String;')
        assert stripped == outputs[0]
        abi[row['path']] = dict(constantsAdded=len(row['mapping']),allOtherPrivatePublicMetadataUnchanged=True,oldOutputSha256=data.sha(outputs[0].encode()),newOutputSha256=data.sha(outputs[1].encode()))
    assert data.sha(javap.read_bytes()) == javap_hash and jar_classes(n) == after and test_classes(n) == b
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in n['begin']['inputHashes'].items())
    verify(invocation);target.mkdir()
    data.write(target/'manifest.json',dict(actualExit=0,source=source,invocation=invocation,normalManifestSha256=normal_pin,staticManifestSha256=static_pin,preflightManifestSha256=preflight[1],stages=stages,
        allMainPhysicalUnchanged=len(after),previousTestPhysical=len(a),currentTestPhysical=len(b),changedTestPhysical=len(changed),oldTestPhysicalUnchanged=len(a)-len(changed),newTestPhysical=0,
        sourceFileClosureClasses=len(closure),classMetadata=metadata,privateConstantsAdded=cfg.EXPECTED_CORRECTIONS,privateMetadata=abi,javapSha256=javap_hash,metadataFieldVectors=selftest(),
        originalTokenInverses=p['originalTokenInverses'],tokenInverseNegativeVectors=sum(p['negativeVectors'].values()),removedFindingIds=p['removedFindingIds'],rawStatic=p['rawStatic'],rawStaticGateExit=p['rawStaticGateExit'],spotbugsSixReports=s['spotbugsSixReports'],
        productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',oldPtQualificationTransferred=False,rawCodeHashIsNotSemanticProof=True,
        newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((target/'manifest.json').read_bytes()))
