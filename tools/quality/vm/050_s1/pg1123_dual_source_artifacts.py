"""Independent old-preservation/current-BOM oracle; no source-result borrowing.

SS343/353/SSC249; BUG1032/YKT801; PT-DEP-1123001..003.
"""
import hashlib
import json
import re
from pathlib import PurePosixPath


def require(ok):
    if not ok:raise ValueError('dual source artifact qualification refused')


def relative(name):
    require(type(name)is str and name and not PurePosixPath(name).is_absolute()
            and str(PurePosixPath(name))==name and '..'not in PurePosixPath(name).parts)
    return name


def qualify(old,before,now,manifest,read_old,read_current,source,digest,count=187):
    require(type(old)is dict and len(old)==count)
    for name,wanted in old.items():
        relative(name);require(type(wanted)is str and re.fullmatch('[0-9a-f]{64}',wanted)is not None)
        require(hashlib.sha256(read_old(name)).hexdigest()==wanted)
    require(type(manifest)is bytes and hashlib.sha256(manifest).hexdigest()==digest)
    bom=json.loads(manifest)
    require(type(bom)is dict and bom['source']['commit']==source and type(bom['artifacts'])is list
            and len(bom['artifacts'])==count)
    hashes={}
    for row in bom['artifacts']:
        require(type(row)is dict and set(row)=={'path','size','sha256'})
        name=relative(row['path']);require(name not in hashes and type(row['size'])is int and row['size']>=0)
        require(type(row['sha256'])is str and re.fullmatch('[0-9a-f]{64}',row['sha256'])is not None)
        raw=read_current(name)
        require(type(raw)is bytes and len(raw)==row['size']and hashlib.sha256(raw).hexdigest()==row['sha256'])
        hashes[name]=row['sha256']
    require(type(before)is dict and type(now)is dict and set(before)==set(now))
    for name,wanted in before.items():
        require(type(wanted)is dict and set(wanted)=={'metadata','acl','sha256','target'}
                and not wanted['acl']and wanted['target']is None)
        require(now[name]=={'metadata':wanted['metadata'],'sha256':wanted['sha256']})
    # Snapshot closure must consist of the signed payload, its exact ancestors,
    # and the two canonical release-control files, not arbitrary extra entries.
    paths=set(hashes)|{'RELEASE-MANIFEST.json','SHA256SUMS'}
    closed={''}
    for name in paths:
        closed.add(name)
        closed.update(str(p)for p in PurePosixPath(name).parents if str(p)!='.')
    require(set(now)==closed)
    require(now['RELEASE-MANIFEST.json']['sha256']==digest)
    return {'oldArtifactsPreserved':count,'currentArtifactsVerified':count,
            'currentSource':source,'currentBomSha256':digest,'currentArtifactHashes':hashes,
            'sourceScopesSeparated':True,'formalAccepted':False}
