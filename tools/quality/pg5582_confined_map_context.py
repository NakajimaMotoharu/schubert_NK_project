"""Individual Map contexts only. Fresh diagnostic/whole binding remains an explicit second step."""
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SOURCE='2fc563a5f2fba4cfaf6f7a5bd56fe8909c1910ad'
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG5582-confined-map-context-v1'
# Exact individual findings reviewed, not an automatic exemption for other HashMaps.
SPEC={
 'AssetChecksumManifest.java':([37],['this.hashes = Map.copyOf(hashes);'],'AssetChecksumManifestTest','local parser map becomes a defensive immutable manifest'),
 'AuthContextCodec.java':([60],['keys = Map.copyOf(copies);','copies.put(currentVersion, currentKey.clone());'],'AuthContextCodecTest','constructor-local map is copied; secret byte arrays remain private under the existing state lock'),
 'BackupArtifactVerifier.java':([180,181,478,479],['files = Map.copyOf(files);','contents = Map.copyOf(contents);','return new PendingDigests(','return new BundleSnapshot('],'BackupArtifactVerifierTest','per-invocation maps in synchronous held-inode callbacks; only individual digest values or defensive BundleSnapshot copies leave'),
 'MaintenanceRunFiles.java':([1037,1038,1039,1040,1126,1127,1128],['runs = Map.copyOf(runs);','begins = Map.copyOf(begins);','done = Map.copyOf(done);','plans = Map.copyOf(plans);','return graph(runs, begins, done, active);'],'MaintenanceRunFilesTest','local scan/retirement maps enter private immutable Inventory or defensive graph snapshots'),
 'InspectorUnitSnapshot.java':([104],['this.values = Map.copyOf(values);'],'InspectorUnitSnapshotTest','local strict parser map is copied before publication'),
 'MaintenanceStopSnapshot.java':([43],['this.fields = Map.copyOf(fields);'],'MaintenanceStopSnapshotTest','local strict parser map is copied before publication'),
 'MaintenanceUnitStopPolicy.java':([53],['private static void parse(MaintenanceUnit unit, byte[] bytes)','fields.putIfAbsent(key, lines[i].substring(separator + 1))'],'MaintenanceUnitStopPolicyTest','method-local validation scratch map; void parse does not publish the map'),
 'ReleasePayloadVerification.java':([49,50,297],['final class ReleasePayloadVerification {','return new JarValue(Set.copyOf(classes), Map.copyOf(sql));'],'ReleasePayloadVerificationTest','two private fields belong to a new single-use nonescaping verifier; local archive SQL map is copied into JarValue'),
 'PayloadCodec.java':([169],['return new FieldValueSet(values);'],'PayloadGoldenVectorTest','per-call ordered decode map goes through the defensive immutable FieldValueSet boundary'),
 'MediaRangeService.java':([96],['response.begin(status, Map.copyOf(headers));'],'MediaRangeServiceTest','response receives an immutable copy of per-call header scratch')}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def context_rows(baseline,physical,old):
    rows=[];seen={};witnesses={}
    for row in baseline['findings']:
        if row['rule']!='UseConcurrentHashMap':continue
        relative=row['sourcePath'];path=ROOT/relative
        if not path.resolve().is_relative_to(ROOT/'src')or'/src/main/java/'not in relative:raise ValueError('known production source path only')
        if path.name not in SPEC:raise ValueError('unknown Map requires individual review, never blanket rule waiver')
        lines,required,test,basis=SPEC[path.name];raw=path.read_bytes();source=raw.decode();line=int(row['beginline'])
        if sha(raw)!=row['sourceSha256']or line not in lines or any(fact not in source for fact in required):raise ValueError('each explicitly reviewed current source fact must match')
        text=source.splitlines(keepends=True)[line-1]
        declaration=re.fullmatch(r'\s*(private final )?Map<[^;]+> (\w+) = new (?:HashMap|LinkedHashMap)<>\(\);\s*',text)
        if not declaration:raise ValueError('one exact local or private-final HashMap allocation')
        field=declaration[1]is not None
        if field!=(path.name=='ReleasePayloadVerification.java'and line in(49,50)):raise ValueError('only the two explicitly single-use verifier fields are allowed')
        module=relative.split('/')[1].removeprefix('schubert-nk-');class_path=relative.split('/src/main/java/',1)[1][:-5]
        prefix=module+':'+class_path;keys={k for k in physical if k==prefix+'.class'or k.startswith(prefix+'$')}
        if not keys or any(physical[k]!=old[k]for k in keys):raise ValueError('all current compiled classes for reviewed file must equal their immutable a19 base bytes')
        seen.setdefault(path.name,set()).add(line)
        witnesses[relative]={'sourceSha256':sha(raw),'requiredReviewedSnippetSha256':[sha(s.encode())for s in required],
            'actualCompiledClassSha256':{k:physical[k]for k in sorted(keys)}}
        rows.append({k:row[k]for k in('findingId','rule','sourcePath','sourceSha256','beginline','endline','priority')}|
            {'sourceSpanSha256':sha(text.encode()),'mapVariable':declaration[2],'kind':'SINGLE_USE_VERIFIER_FIELD'if field else'LOCAL_SCRATCH',
                'basis':basis,'relatedTestClass':test,'rawWarningRetained':True,'currentDiagnosticAndWholeBindingPending':True,
                'assessmentScope':'CONCURRENCY_PREMISE_ONLY_NOT_FUNCTIONAL_CERTIFICATION'})
    if len(rows)!=21 or seen!={name:set(value[0])for name,value in SPEC.items()}or sum(r['kind']=='SINGLE_USE_VERIFIER_FIELD'for r in rows)!=2:
        raise ValueError('all21 exact contexts:19 locals/two single-use fields, none omitted')
    callers=ROOT/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/StartupReleaseManifest.java'
    source=callers.read_text()
    expression=r'new ReleasePayloadVerification\(this, group, io, security\)\s*\.verify\(release, version, approval\)'
    if len(re.findall(expression,source))!=2 or source.count('new ReleasePayloadVerification(')!=2:raise ValueError('both actual construction sites must immediately call verify without exposing verifier')
    uses=[p for p in ROOT.glob('src/*/src/main/java/**/*.java')if 'ReleasePayloadVerification'in p.read_text()]
    if {p.name for p in uses}!={'StartupReleaseManifest.java','ReleasePayloadVerification.java'}:raise ValueError('no new verifier sharing or registration caller')
    immutable=ROOT/'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/FieldValueSet.java'
    value=immutable.read_text()
    if 'LinkedHashMap<String, FieldValue> copy = new LinkedHashMap<>();'not in value or'values = Collections.unmodifiableMap(copy);'not in value:raise ValueError('decode map must cross an independent-copy immutable boundary')
    witnesses[str(callers.relative_to(ROOT))]={'sourceSha256':sha(callers.read_bytes()),'singleUseImmediateVerifySites':2}
    witnesses[str(immutable.relative_to(ROOT))]={'sourceSha256':sha(immutable.read_bytes()),'defensiveOrderedImmutableSink':True}
    return rows,witnesses


def main():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','program/characterization'],cwd=ROOT):raise ValueError('fixed current source, no edits during whole')
    original=BASE/'PG5560-snapshot-static-findings-v1/manifest.json';raw=original.read_bytes()
    if sha(raw)!='7a7e73525d491875f74685208f07595500c448a9cd380a2f4d6590162f564740':raise ValueError('immutable actual a19 raw diagnostic/review, not a current diagnostic claim')
    w=ROOT.parent/'pgpt-runs/PG379';current=(w/'pg5566-private-monitor-green-v2/manifest.safe.json').read_bytes()
    if sha(current)!='27d1b35269b9a4e8848100565e7d6b901f425cd599805c6afe1031dc874ced50':raise ValueError('actual current71/all1664 compiled selection')
    selected=json.loads(current)
    if not(selected['sourceSnapshot']==SOURCE and selected['greenSelectedQualified']and selected['physicalMain']['count']==1664):raise ValueError('current compiled source first')
    previous=json.loads((BASE/'PG5550-current3900-cases/qualification.json').read_bytes())
    rows,witnesses=context_rows(json.loads(raw),selected['physicalMain']['sha256'],previous['allPhysicalMainSha256'])
    jar=ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    with zipfile.ZipFile(jar)as z:rules=z.read('category/java/multithreading.xml')
    rule=next(x for x in ET.fromstring(rules)if x.get('name')=='UseConcurrentHashMap')
    if 'and have concurrent access'not in rule.get('message',''):raise ValueError('installed primary rule explicitly requires concurrency premise')
    value={'actualExit':0,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceSnapshot':SOURCE,
        'rawDiagnosticBaselineSource':json.loads(raw)['source'],'rawDiagnosticBaselineSha256':sha(raw),'sourceContexts':rows,'witnesses':witnesses,
        'contextRows':21,'localMaps':19,'singleUseFields':2,'primaryRule':{'name':'UseConcurrentHashMap','version':'7.28.0','message':rule.get('message'),
            'definitionSha256':sha(ET.tostring(rule)),'jarSha256':sha(jar.read_bytes())},
        'freshCurrentDiagnosticClaimed':False,'freshWholeClaimed':False,'currentDiagnosticAndWholeBindingPending':True,
        'ruleSuppressionAdded':False,'threadSafetyCertified':False,'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'vmActions':0}
    os.umask(0o077);OUT.mkdir()
    with(OUT/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'sourceSnapshot':SOURCE,'contexts':21,'local':19,'singleUseFields':2,'sha256':sha((OUT/'manifest.json').read_bytes()),'currentDiagnosticAndWholeBindingPending':True,'F03Accepted':False}))


if __name__=='__main__':main()
