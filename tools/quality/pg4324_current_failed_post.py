"""Separate fresh current failed-DONE post; before SQL/image and native export oracles remain independent."""
import ast
import base64
import hashlib
import json
import os
import sys
from pyflakes.api import check
import pg4316_current_failed_dispatch as recovery
import pg4322_current_post_profile_compile as profile
from pg4166_partial_recovery_sources import archived,inject_declarations
from pg4260_stable_admission_image import execute
from pg1446_current_cold_stage import W

SLOT='pg4324-current-failed-independent-post-v1'
ARTIFACT=W/'pg4326-current-failed-post-artifact-v1'


def payload():
    raw=archived('pg4150-failed-done-post-artifact-v1/post.private.py','a89c7dfa784be50951614441b1fa674125d7f3dde32b79cffef5ebaea88361ad')
    raw=recovery.role.bind_instance(raw)
    for old,new in [('pg4148-failed-done-independent-post-v1',SLOT),('pg4146-complete-signed-owned-recovery-v1',recovery.SLOT),
       ('pg4112-canonical-epoch-owned-tools-v1',recovery.role.TOOLS),('pg4060-original-read-profile-v1',profile.SLOT),
       ('pg4080-failed-ordinary-full-capture-v1','pg4306-current-failed-authority-read-v1'),
       ('fd1177d10f2713596a32de536a3c71d592563cc3b6decb7194bc6c68ea6c21d8','63269de90bc6bb554e73bde70dcb44bb8e844424c7b364f6597ed1d08aaaf1fd'),
       ('pg4072-failed-parent-pid1-read-v1','pg4302-current-failed-parent-read-v1'),
       ('4b930e614069ccaee34382ba14d84efaf1274dafd262749c5a77d61accb10f38','24e22836fdc96b970a551f2e406e5888d70ea472c930133904cb4a63f9552475'),
       ('128735401165','149622262076'),('130545470134','151432334917'),('all33StartupEntriesPreserved','all37StartupEntriesPreserved')]:raw=raw.replace(old,new)
    new=json.loads((W/(profile.SLOT+'-compile')/'manifest.safe.json').read_bytes())
    if new['actualExit']!=0 or new['result']['actualExit']!=0:raise ValueError('actual current-only post profile compile required')
    old=json.loads((W/'pg4060-original-read-profile-v1-compile/manifest.safe.json').read_bytes())['result']['classHashes']
    nodes=[]
    for n in ast.walk(ast.parse(raw)):
        if isinstance(n,ast.Dict):
            try:value=ast.literal_eval(n)
            except (ValueError,TypeError):continue
            if value==old:nodes.append(n)
    if len(nodes)!=2:raise ValueError('both complete profile class dictionary pins required')
    for text in {ast.get_source_segment(raw,n)for n in nodes}:raw=raw.replace(text,repr(new['result']['classHashes']))
    raw=recovery.constant(raw,'JAVA_B64',base64.b64encode(profile.java().encode()).decode())
    raw=recovery.constant(raw,'HELPERS',recovery.compiled()['inputFileHashes'])
    raw=recovery.constant(raw,'PARENT_SOURCE',recovery.parent_source())
    raw=inject_declarations(raw)
    if check(raw,'<whole new current independent post>'):raise ValueError('complete independent post static0 required')
    compile(raw,'<independent new-current post>','exec');return raw


def freeze():
    os.umask(0o077);ARTIFACT.mkdir(mode=0o700);raw=payload().encode();p=ARTIFACT/'post.private.py'
    with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    p.chmod(0o400)
    recovery.durable(ARTIFACT/'manifest.safe.json',{'payloadSha256':hashlib.sha256(raw).hexdigest(),'source':recovery.role.SOURCE,'operationsIssued':0})
    print(json.dumps({'actualExit':0,'payloadSha256':hashlib.sha256(raw).hexdigest(),'postNotRun':True}));return 0


def main():
    v=json.loads((W/(recovery.SLOT+'-recover')/'manifest.safe.json').read_bytes())
    if v['actualExit']!=0 or v['source']!=recovery.role.SOURCE or v['result']['newScopeNormalClose']is not True or v['result']['all37StartupEntriesPreserved']is not True:raise ValueError('actual complete current recovery required')
    raw=(ARTIFACT/'post.private.py').read_bytes();pin=json.loads((ARTIFACT/'manifest.safe.json').read_bytes())
    if raw!=payload().encode()or hashlib.sha256(raw).hexdigest()!=pin['payloadSha256']:raise ValueError('same fixed independent post required')
    return execute(SLOT,raw.decode(),200)


if __name__=='__main__':
    if sys.argv[1:]==['freeze']:raise SystemExit(freeze())
    if sys.argv[1:]==['run']:raise SystemExit(main())
    raise SystemExit('freeze or run only after current normal recovery')
