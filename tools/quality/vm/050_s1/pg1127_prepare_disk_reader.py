"""Pin operator-only read-only QCOW/GPT/extfs libraries outside Git.

No system/pip changes, VM/device attachment, original disk writes, or full copy.
Downloaded wheels are verified against pinned official PyPI SHA256.
"""
import datetime
import hashlib
import json
import os
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

OUT=Path('/home/mini/codex/project1/work/toolchain/dissect-backup-readonly-20261010')
PACKAGES=[
    ('dissect.hypervisor','3.21','fd845a3e7bc20efca575d4cfbb49a21ca53e8d89efb8afeec180de8a6b62fd2f'),
    ('dissect.volume','3.18','f8f321adccacbd948c503cf14a14d4a6626d1b86ddcbe55c532b59caad833d79'),
    ('dissect.extfs','3.15','9c67e64552eedc58ecbbdda82287a6c8fbf8b29d99a7b55073d838233d6dfcab'),
    ('dissect.util','3.24','031f91d7523818a3aced4d17594996bcc39bc4d93ffacc0b15a7b718c9b437cb'),
    ('dissect.cstruct','4.7','0427621ce67baa3106df2dc63a320d0a7f5c2da88ba3faf2ef5886a1a6b458fd'),
    ('defusedxml','0.7.1','a352e7e428770286cc899e2542b6cdaedb2b4953ff269a210103ec58f6198a61'),
]


def main():
    if OUT.exists():raise ValueError('existing tool install preserved')
    os.umask(0o077);OUT.mkdir(mode=0o700);runtime=OUT/'runtime';runtime.mkdir(mode=0o700)
    records=[]
    for package,version,digest in PACKAGES:
        metadata='https://pypi.org/pypi/'+package+'/'+version+'/json'
        with urllib.request.urlopen(metadata,timeout=20)as f:info=json.load(f)
        files=[x for x in info['urls']if x['filename'].endswith('none-any.whl')
               and x['digests']['sha256']==digest]
        if len(files)!=1:raise ValueError('pinned official wheel unavailable')
        item=files[0]
        if not item['url'].startswith('https://files.pythonhosted.org/'):
            raise ValueError('wheel source refused')
        with urllib.request.urlopen(item['url'],timeout=30)as f:raw=f.read(20*1024*1024+1)
        if len(raw)>20*1024*1024 or hashlib.sha256(raw).hexdigest()!=digest:
            raise ValueError('wheel digest refused')
        wheel=OUT/item['filename']
        with wheel.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
        with zipfile.ZipFile(wheel)as z:
            for name in z.namelist():
                p=PurePosixPath(name)
                if p.is_absolute()or '..'in p.parts:raise ValueError('wheel entry refused')
                if (runtime/name).is_file():raise ValueError('overlapping wheel file refused')
            z.extractall(runtime)
        records.append(dict(package=package,version=version,metadataUrl=metadata,
                            wheelUrl=item['url'],sha256=digest,bytes=len(raw),
                            requiresDist=info['info'].get('requires_dist'),
                            license=info['info'].get('license')))
    manifest=dict(scope='OPERATOR_READONLY_BACKUP_PRESERVATION_ONLY',
                  productionDependency=False,systemModified=False,vmModified=False,
                  installedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  packages=records,runtime=str(runtime))
    with(OUT/'manifest.json').open('x')as f:json.dump(manifest,f,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'packages':[r['package']+'=='+r['version']for r in records],
                      'manifest':str(OUT/'manifest.json'),'manifestSha256':hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),
                      'downloadBytes':sum(r['bytes']for r in records),'systemVmModified0':True}))


if __name__=='__main__':main()
