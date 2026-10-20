"""Current850 Main-only type facts, pending original3955; never invoke Production code."""
import json
import os
from pathlib import Path
import types
import pg5766_reference_identity_facts as previous
from pg5808_rollback_whole import SOURCE,ROOT,W
from pg5540_snapshot_scratch_selected import sha
from pg5584_field_accessor_inspection import compile_only_artifacts


def inputs():
    public=previous.BASE/'PG5810-rollback-static-reauth-v1/manifest.json'
    if sha(public)!='68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23':raise ValueError('current Main static source/byte reauthentication')
    private=W/'pg5810-rollback-static-reauth-v1/manifest.safe.json'
    if sha(private)!=json.loads(public.read_bytes())['privateManifestSha256']:raise ValueError('actual current850/1665 maps')
    proof=json.loads(private.read_bytes());snapshot=W/'pg5800-rollback-selected54-v5/source'
    current={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')};mirrored={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=850 or current!=mirrored or current!=proof['allSourceHashes']or proof['source']!=SOURCE or proof['actualExit']!=0:raise ValueError('all850 actual immutable Main parser inputs')
    roots=[snapshot/('src/schubert-nk-'+m+'/target/classes')for m in('protocol','storage','bootstrap','api','web','batch')]
    physical={root.parts[-3].removeprefix('schubert-nk-')+':'+p.relative_to(root).as_posix():sha(p)for root in roots for p in root.rglob('*.class')}
    if len(physical)!=1665 or physical!=proof['auxClassHashes']:raise ValueError('all1665 current actual type resolution classes')
    release=W/'pg5430-release-v1';bom=release/'RELEASE-MANIFEST.json'
    if sha(bom)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('unchanged third-party BOM only')
    jars={}
    for row in json.loads(bom.read_bytes())['artifacts']:
        p=Path(row['path'])
        if '/lib/'not in row['path']or p.suffix!='.jar'or p.name.startswith('schubert-nk-'):continue
        target=release/p
        if target.is_symlink()or sha(target)!=row['sha256']:raise ValueError('actual immutable third-party jar')
        jars.setdefault(row['sha256'],target)
    provided,metadata=compile_only_artifacts()
    return snapshot,os.pathsep.join(map(str,[*roots,*jars.values(),*provided])),{'sourceHashes':current,'physicalMainSha256':physical,'qualifiedWholeSha256':None,'currentWholeQualificationPending':True,'currentActualSourceByteProofSha256':sha(private),'thirdPartyJarSha256':list(jars),'providedAnnotations':metadata}


def namespace():
    return {**vars(previous),'SOURCE':SOURCE,'SLOT':'pg5818-current-reference-facts-v1','inputs':inputs}


def main():
    # Reuse the already independently tested parser/fixture, not a historical type or PT result.
    return types.FunctionType(previous.main.__code__,namespace(),'current850_reference_facts')()


if __name__=='__main__':raise SystemExit(main())
