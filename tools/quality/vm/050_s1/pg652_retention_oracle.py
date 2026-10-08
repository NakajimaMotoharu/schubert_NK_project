"""SS331/341 independent new-success/skip and two-oldest retention oracle."""
import datetime
import hashlib
import json
import re
import uuid

STEPS=('BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY')
COLUMNS=set('attempt business_date byte_count ended_at error_code error_summary expiry_after_count expiry_before_count expiry_cutoff_at failure_count id run_id started_at status step success_count target_count'.split())
ROOT='/srv/schubert-nk/backup'


def require(ok):
    if not ok:raise ValueError('independent new-success retention post rejected')


def stamp(v):
    require(type(v)is str);t=datetime.datetime.fromisoformat(v.replace('Z','+00:00'));require(t.tzinfo is not None);return t


def validate(old,new,old_backup,new_backup,expected,raw_manifest,files,anchor,bounds):
    require(type(old)is dict and type(new)is dict and len(old)==24 and set(old)==set(new))
    for table in old.keys()-{'schubert.batch_runs'}:require(old[table]==new[table])
    before=old['schubert.batch_runs'];after=new['schubert.batch_runs'];require(len(before)==504 and len(after)==514)
    prior={r['id']:r for r in before};actual={r['id']:r for r in after}
    require(len(prior)==504 and len(actual)==514 and all(actual.get(k)==v for k,v in prior.items()))
    added=[r for k,r in actual.items()if k not in prior]
    require(len(added)==10 and {r['step']for r in added}==set(STEPS)and len({r['run_id']for r in added})==1)
    run=added[0]['run_id'];identifier=uuid.UUID(run);require(str(identifier)==run and identifier.version==4 and run not in {r['run_id']for r in before})
    require(type(anchor)is bytes and len(anchor)==72 and anchor.endswith(b'\n'))
    parts=anchor.decode('ascii').splitlines();require(len(parts)==3 and parts[:2]==['NKRUN1',run]);cutoff=parts[2]
    require(stamp(bounds['lower'])<=stamp(cutoff)<=stamp(bounds['upper']))
    require(type(raw_manifest)is bytes and 0<len(raw_manifest)<=4096)
    def unique(items):
        result={}
        for k,v in items:require(k not in result);result[k]=v
        return result
    m=json.loads(raw_manifest,object_pairs_hook=unique)
    require(list(m)==['format','database','runId','cutoff','startedAt','contentFinishedAt','databaseStep','configurationStep','versions','recipientSha256','files'])
    versions={'host':'pgpt-r2','app':'0.1.0-SNAPSHOT','schema':'028','os':'ubuntu-26.04','jdk':'25.0.4','postgresql':'18.6','artemis':'2.56.0','age':'1.2.1'}
    require(m['format']=='NKBACKUP1'and m['database']=='schubert_nk'and m['runId']==run and m['cutoff']==cutoff and m['versions']==versions and list(m['versions'])==list(versions))
    require(raw_manifest==(json.dumps(m,ensure_ascii=True,separators=(',',':'))+'\n').encode('ascii'))
    require(type(m['recipientSha256'])is str and re.fullmatch('[0-9a-f]{64}',m['recipientSha256'])is not None)
    require(type(files)is dict and set(files)=={'schubert_nk.dump','config.tar','credentials.tar.age'}and list(m['files'])==['schubert_nk.dump','config.tar','credentials.tar.age'])
    for name,raw in files.items():
        require(type(raw)is bytes and len(raw)>0 and m['files'][name]=={'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    start,finish=stamp(m['startedAt']),stamp(m['contentFinishedAt']);require(stamp(cutoff)<=start<=finish)
    by_step={r['step']:r for r in added}
    for step,r in by_step.items():
        require(set(r)==COLUMNS and r['business_date']=='2026-10-09')
        previous=[s for s in before if s['step']==step and s['business_date']=='2026-10-09']
        require(type(r['attempt'])is int and r['attempt']==max(s['attempt']for s in previous)+1)
        require(all(type(r[k])is int for k in ('target_count','success_count','failure_count','byte_count'))and r['failure_count']==0)
        require(all(r[k]is None for k in ('expiry_cutoff_at','expiry_before_count','expiry_after_count')))
        require(stamp(cutoff)<=stamp(r['started_at'])<=stamp(r['ended_at']))
        if step in STEPS[:2]:
            claim=m['databaseStep'if step=='BACKUP_DB'else'configurationStep']
            require(list(claim)==['id','attempt','startedAt']and claim['id']==r['id']and claim['attempt']==r['attempt']and stamp(claim['startedAt'])==stamp(r['started_at'])and stamp(r['started_at'])<=start and finish<=stamp(r['ended_at']))
            count,size=(1,len(files['schubert_nk.dump']))if step=='BACKUP_DB'else(2,len(files['config.tar'])+len(files['credentials.tar.age']))
            require(r['status']=='SUCCESS'and r['error_code']is None and r['error_summary']is None and (r['target_count'],r['success_count'],r['byte_count'])==(count,count,size))
        else:
            require(r['status']=='SKIPPED'and r['error_code']=='ALREADY_SUCCESSFUL'and r['error_summary']=='step already successful for business date'
                    and r['ended_at']==r['started_at']and all(r[k]==0 for k in ('target_count','success_count','byte_count')))
            successes=[s for s in previous if s['status']=='SUCCESS'];require(len(successes)==1 and successes[0]['run_id']=='3a53b979-fa01-47dd-92a6-7b26affcfb5c')
    require(expected['eligibleUpperBound']==8 and expected['maximumEligibleAfterNew']==9 and expected['retentionLimit']==7 and expected['expectedRetentionDeletes']==2)
    deleted=expected['expectedDeleted'];require(type(deleted)is list and len(deleted)==2 and len(set(deleted))==2)
    removed={k for k in old_backup if any(k==ROOT+'/'+name or k.startswith(ROOT+'/'+name+'/')for name in deleted)}
    require(len(removed)==10 and not removed.intersection(new_backup))
    for k,v in old_backup.items():
        if k not in removed and k!=ROOT:require(new_backup.get(k)==v)
    a,b=old_backup[ROOT]['metadata'],new_backup[ROOT]['metadata']
    require(a[:5]==b[:5]and b[5]==a[5]-1 and new_backup[ROOT]['sha256']is None)
    bundle=stamp(m['startedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')+'-'+run
    new_entries=set(new_backup)-(set(old_backup)-removed)
    require(new_entries=={ROOT+'/'+bundle}|{ROOT+'/'+bundle+'/'+name for name in ('MANIFEST.json',*files)})
    for name,raw in {'MANIFEST.json':raw_manifest,**files}.items():
        v=new_backup[ROOT+'/'+bundle+'/'+name];require(v['sha256']==hashlib.sha256(raw).hexdigest()and v['metadata'][6]==len(raw))
    return {'oldRowsPreserved':504,'newBackupSuccess':2,'newOtherSkipped':8,'retentionDeleted':2,'eligibleAfter':7,'protectedPreserved':5,'remainingOldBackupBytesUnchanged':True,'runId':run,'cutoff':cutoff,'parentDoneAccepted':False,'formalAccepted':False}
