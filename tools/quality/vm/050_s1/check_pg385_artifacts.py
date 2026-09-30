"""Independent native backup oracle. Private archive/keys never emitted or committed."""
import pathlib, tarfile, io, json, hashlib, subprocess
root=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
with tarfile.open(root/'pg385-actual-backup.tar') as bundle:
    assert set(bundle.getnames())=={'MANIFEST.json','config.tar','credentials.tar.age','schubert_nk.dump'}
    values={n:bundle.extractfile(n).read() for n in bundle.getnames()}
    m=json.loads(values['MANIFEST.json'])
    assert m['format']=='NKBACKUP1' and m['runId']=='31100027-2222-4333-8444-555555555555'
    assert m['cutoff']=='2026-09-27T15:00:00.000000Z'
    assert m['database']=='schubert_nk' and m['startedAt']=='2026-09-30T03:00:30.080706Z'
    assert m['databaseStep']=={'attempt':3,'id':5,'startedAt':m['startedAt']}
    assert m['configurationStep']=={'attempt':3,'id':6,'startedAt':m['startedAt']}
    assert m['versions']=={'age':'1.2.1','app':'0.1.0-SNAPSHOT','artemis':'2.56.0','host':'pgpt-r2','jdk':'25.0.4','os':'ubuntu-26.04','postgresql':'18.6','schema':'023'}
    assert set(m['files'])=={'config.tar','credentials.tar.age','schubert_nk.dump'}
    for name,claim in m['files'].items():
        assert claim=={'size':len(values[name]),'sha256':hashlib.sha256(values[name]).hexdigest()}
    print(json.dumps({'manifest':m,'actualHashes':{n:hashlib.sha256(b).hexdigest() for n,b in values.items()},'sizes':{n:len(b) for n,b in values.items()}},sort_keys=True))
    with tarfile.open(fileobj=io.BytesIO(values['config.tar'])) as config:
        assert set(config.getnames())=={'common.yml','api.yml','web.yml','batch.yml','api.env','web.env','backup-profile.json'}
        assert all(e.isfile() and not e.issym() and not e.islnk() for e in config)
        print('CONFIG_MEMBERS exact7 regular=true')
    decrypted=subprocess.run(['/home/mini/codex/project1/work/toolchain/age-1.2.1/root/usr/bin/age','-d','-i',str(root/'pg381-backup-age.key')],input=values['credentials.tar.age'],capture_output=True,check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(decrypted)) as credentials:
        assert set(credentials.getnames())=={'db-api','db-web','db-batch','db-migration','backup-pgpass','mq-api','mq-web','mq-maintenance','mq-ops','api-context-aes-current','api-inbox-response-aes-current','operation-hmac-current','web-session-aes-current','web-revoke-aes-current','web-log-aes-current','artemis-users'}
        assert all(e.isfile() and not e.issym() and not e.islnk() for e in credentials)
        print('CREDENTIAL_MEMBERS decrypt=true exact16 regular=true valuesNotEmitted=true')
