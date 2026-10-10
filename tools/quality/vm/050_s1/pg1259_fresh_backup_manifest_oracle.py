"""SS3416.4 independent canonical manifest/file/complete DB-step oracle, no I/O."""
import datetime
import json
import re
import uuid

TOP=['format','database','runId','cutoff','startedAt','contentFinishedAt','databaseStep','configurationStep','versions','recipientSha256','files']
VERSIONS=['host','app','schema','os','jdk','postgresql','artemis','age']
FILES=['schubert_nk.dump','config.tar','credentials.tar.age']

def require(ok):
    if not ok:raise ValueError('independent fresh Backup contract refused')

def pairs(values):
    result={}
    for k,v in values:
        require(k not in result);result[k]=v
    return result

def utc6(value):
    require(type(value)is str and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z',value)is not None)
    return datetime.datetime.fromisoformat(value.replace('Z','+00:00'))

def positive(value,maximum):
    require(type(value)is int and 1<=value<=maximum)

def hash64(value):
    require(type(value)is str and re.fullmatch('[0-9a-f]{64}',value)is not None)

def verify(raw,physical,profile,rows,run,cutoff,recipient_sha):
    require(type(raw)is bytes and 0<len(raw)<=4096 and raw.isascii()and raw.endswith(b'\n'))
    m=json.loads(raw.decode('ascii'),object_pairs_hook=pairs)
    require(type(m)is dict and list(m)==TOP and m['format']=='NKBACKUP1'and m['database']=='schubert_nk')
    require((json.dumps(m,separators=(',',':'),ensure_ascii=True)+'\n').encode('ascii')==raw)
    require(type(run)is str and str(uuid.UUID(run))==run and uuid.UUID(run).version==4 and m['runId']==run)
    require(utc6(m['cutoff'])==utc6(cutoff))
    start,finish=utc6(m['startedAt']),utc6(m['contentFinishedAt']);require(start<=finish)
    require(type(m['versions'])is dict and list(m['versions'])==VERSIONS and type(profile)is dict)
    for key,value in m['versions'].items():
        pattern=r'[0-9]{3}'if key=='schema'else r'[A-Za-z0-9][A-Za-z0-9._+\-]{0,127}'
        require(type(value)is str and re.fullmatch(pattern,value)is not None and value==profile[key])
    require(m['versions']['schema']!='000')
    hash64(m['recipientSha256']);hash64(recipient_sha);require(m['recipientSha256']==recipient_sha)
    require(type(physical)is dict and set(physical)==set(FILES)and type(m['files'])is dict and list(m['files'])==FILES)
    for name in FILES:
        claim=m['files'][name];require(type(claim)is dict and list(claim)==['size','sha256'])
        positive(claim['size'],9223372036854775807);hash64(claim['sha256'])
        require(type(physical[name])is dict and set(physical[name])=={'size','sha256'}and physical[name]==claim)
    require(sum(m['files'][n]['size']for n in FILES)<=9223372036854775807)
    require(type(rows)is list and all(type(row)is dict for row in rows))
    selected={}
    for key,step,count,byte_count in [('databaseStep','BACKUP_DB',1,physical[FILES[0]]['size']),('configurationStep','BACKUP_CONFIG',2,sum(physical[n]['size']for n in FILES[1:]))]:
        handle=m[key];require(type(handle)is dict and list(handle)==['id','attempt','startedAt'])
        positive(handle['id'],999999999999);positive(handle['attempt'],99)
        began=utc6(handle['startedAt']);require(utc6(cutoff)<=began<=start)
        matched=[row for row in rows if row['run_id']==run and row['step']==step]
        require(len(matched)==1);row=matched[0]
        require(type(row['id'])is int and type(row['attempt'])is int and row['id']==handle['id']and row['attempt']==handle['attempt']and row['business_date']==utc6(cutoff).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat())
        # V003 batch_runs has no cutoff column; immutable same-run anchor is
        # verified by the collector. Never invent a DB cutoff field.
        require(datetime.datetime.fromisoformat(row['started_at'])==began and datetime.datetime.fromisoformat(row['ended_at'])>=finish)
        require(row['status']=='SUCCESS'and row['error_code']is None and row['error_summary']is None)
        require(all(type(row[k])is int and row[k]==value for k,value in [('target_count',count),('success_count',count),('failure_count',0),('byte_count',byte_count)]))
        selected[step]=handle['id']
    require(len(set(selected.values()))==2)
    name=start.astimezone(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y%m%d-%H%M%S')+'-'+run
    return {'directoryName':name,'independentCanonicalManifestVerified':True,'physicalThreeArchiveHashesMatched':True,'twoCompleteDbHandlesAndCountBytesMatched':True,'configurationBytes':sum(physical[n]['size']for n in FILES[1:]),'totalArchiveBytes':sum(physical[n]['size']for n in FILES),'generationPruneRestoreAccepted':False,'formalAccepted':False}
