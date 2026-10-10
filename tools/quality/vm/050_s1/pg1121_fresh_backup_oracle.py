"""Independent SS341 §§3,6.4/6.5 fresh Backup postconditions.

BUG1031/YKT800; bytes and DB values come from distinct retained inputs.
No production codec/method generates expected values; no DB/file writes.
"""
import datetime
import hashlib
import json
import re
import stat

FILES={'schubert_nk.dump','config.tar','credentials.tar.age','MANIFEST.json'}
VERSION_KEYS={'host','app','schema','os','jdk','postgresql','artemis','age'}
TOP_KEYS=['format','database','runId','cutoff','startedAt','contentFinishedAt',
          'databaseStep','configurationStep','versions','recipientSha256','files']


def require(ok):
    if not ok:raise ValueError('fresh Backup postcondition refused')


def instant(value):
    require(type(value)is str)
    parsed=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    require(parsed.tzinfo is not None)
    return parsed


def qualify(run,cutoff,old,current,rows,profile,recipient,owner,read):
    require(type(old)is dict and type(current)is dict and type(rows)is list and all(type(r)is dict for r in rows))
    require(type(owner)is tuple and len(owner)==2 and all(type(x)is int and x>0 for x in owner))
    require(type(profile)is dict and VERSION_KEYS<=set(profile)and type(recipient)is bytes)
    root='/srv/schubert-nk/backup'
    added=set(current)-set(old)
    directories=[name for name in added if '/'not in name[len(root)+1:]]
    require(len(directories)==1 and set(old)<=set(current))
    folder=directories[0];require(folder.startswith(root+'/'))
    require(added=={folder}|{folder+'/'+x for x in FILES})
    for name,value in old.items():
        now=current[name]
        if name==root:
            require(now['sha256']==value['sha256']and now['metadata'][:5]==value['metadata'][:5])
            require(now['metadata'][5]==value['metadata'][5]+1 and
                    all(now['metadata'][k]>=value['metadata'][k]for k in [6,7,8]))
        else:require(now==value)
    directory=current[folder]['metadata']
    require(directory[2:6]==[owner[0],owner[1],stat.S_IFDIR|0o700,2])
    for name in FILES:
        value=current[folder+'/'+name];m=value['metadata']
        pair=owner if name=='schubert_nk.dump'else(0,0)
        require(m[2:6]==[pair[0],pair[1],stat.S_IFREG|0o600,1]and m[6]>0)
        data=read(folder+'/'+name)
        require(type(data)is bytes and len(data)==m[6]and hashlib.sha256(data).hexdigest()==value['sha256'])
    raw=read(folder+'/MANIFEST.json')
    require(0<len(raw)<=4096 and raw.endswith(b'\n')and raw.isascii())
    manifest=json.loads(raw)
    require(type(manifest)is dict and list(manifest)==TOP_KEYS)
    # Independent JSON serialization, not Production's codec: no whitespace,
    # duplicate fields or trailing bytes can masquerade as canonical claims.
    require(raw==(json.dumps(manifest,separators=(',',':'),ensure_ascii=True)+'\n').encode('ascii'))
    require(manifest['format']=='NKBACKUP1'and manifest['database']=='schubert_nk'and
            manifest['runId']==run and manifest['cutoff']==cutoff)
    for key in ['cutoff','startedAt','contentFinishedAt']:
        require(type(manifest[key])is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z',manifest[key])is not None)
    started=instant(manifest['startedAt']);finished=instant(manifest['contentFinishedAt'])
    require(instant(cutoff)<=started<=finished)
    jst=started.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    require(folder==root+'/'+jst.strftime('%Y%m%d-%H%M%S')+'-'+run)
    require(type(manifest['versions'])is dict and set(manifest['versions'])==VERSION_KEYS and
            manifest['versions']=={k:profile[k]for k in VERSION_KEYS})
    require(manifest['recipientSha256']==hashlib.sha256(recipient.strip()).hexdigest())
    claims=manifest['files'];require(type(claims)is dict and set(claims)==FILES-{'MANIFEST.json'})
    for name,value in claims.items():
        actual=current[folder+'/'+name]
        require(type(value)is dict and list(value)==['size','sha256']and
                type(value['size'])is int and value['size']==actual['metadata'][6]and
                value['sha256']==actual['sha256'])
    require(read(folder+'/schubert_nk.dump').startswith(b'PGDMP'))
    require(read(folder+'/credentials.tar.age').startswith(b'age-encryption.org/v1\n'))
    pair={r['step']:r for r in rows if r.get('run_id')==run and r.get('step')in {'BACKUP_DB','BACKUP_CONFIG'}}
    require(len(pair)==2 and sum(r.get('run_id')==run and r.get('step')in pair for r in rows)==2)
    for step,key,count,names in [('BACKUP_DB','databaseStep',1,['schubert_nk.dump']),
                                 ('BACKUP_CONFIG','configurationStep',2,['config.tar','credentials.tar.age'])]:
        r=pair[step];claim=manifest[key]
        require(r['run_id']==run and r['business_date']==instant(cutoff).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat())
        require(r['status']=='SUCCESS'and r['error_code']is None and r['error_summary']is None)
        require(all(type(r[k])is int for k in ['target_count','success_count','failure_count','byte_count']))
        require(r['target_count']==r['success_count']==count and r['failure_count']==0 and
                r['byte_count']==sum(current[folder+'/'+n]['metadata'][6]for n in names))
        require(type(claim)is dict and list(claim)==['id','attempt','startedAt']and
                claim['id']==r['id']and claim['attempt']==r['attempt']and
                type(claim['id'])is int and 1<=claim['id']<=999999999999 and
                type(claim['attempt'])is int and 1<=claim['attempt']<=99)
        require(type(claim['startedAt'])is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z',claim['startedAt'])is not None)
        require(instant(claim['startedAt'])==instant(r['started_at'])and
                instant(cutoff)<=instant(r['started_at'])<=started<=finished<=instant(r['ended_at']))
    return {'freshBackupTwoSuccessVerified':True,'newBundleEntries':5,
            'oldBackupEntriesPreserved':len(old),'manifestSha256':hashlib.sha256(raw).hexdigest(),
            'contentDigestDbCountersBound':True,'formalAccepted':False}
