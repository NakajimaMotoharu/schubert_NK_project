"""Project only repo-known fixed string literals from already-saved original journals."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from pg4996_resume_connection import authenticate_host
from pg5638_new_normal_root_once import SSH,W

ROOT=Path(__file__).resolve().parents[2]
SLOT='pg5698-failed-journal-projection-v1'


def catalog():
    result=set()
    for path in ROOT.glob('src/*/src/main/java/**/*.java'):
        for raw in re.findall(r'"(?:\\.|[^"\\])*"',path.read_text()):
            try:value=json.loads(raw)
            except json.JSONDecodeError:continue
            if len(value)>=8 and '\n'not in value and '\r'not in value:result.add(value)
    return result


def project(raw,literals):
    rows=[json.loads(line)for line in raw.splitlines()];result=[]
    for i,row in enumerate(rows):
        message=row.get('MESSAGE','')
        if type(message)is not str:continue
        match=sorted((s for s in literals if message==s or message.startswith(s)),key=lambda s:(-len(s),s))
        result.append({'ordinal':i,'messageSha256':hashlib.sha256(message.encode()).hexdigest(),
          'knownFixedLiteral':match[0]if match else None,'completeLiteralMatch':message in literals,
          'timestamp':row.get('__REALTIME_TIMESTAMP'),'pid':row.get('_PID')})
    return result


def main():
    authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);literals=catalog();summaries={}
    for role,digest in(('root','577500d4fe618afa91c1c14d65228afc483bd74bb40fb5da0978c75507a658c3'),('api','c9e8c644f768937d074bd72cf83c14fb413a8b00498842518e9579cc7d9fe3d3')):
        path='/var/lib/pgpt-s1-preservation/pg5696-failed-root-readonly-v1/'+role+'-journal-stdout.private'
        r=subprocess.run(SSH+['sudo','-n','cat',path],capture_output=True,timeout=30)
        with(out/(role+'-journal.private.jsonl')).open('xb')as f:f.write(r.stdout);f.flush();os.fsync(f.fileno())
        if r.returncode or hashlib.sha256(r.stdout).hexdigest()!=digest:raise ValueError('original preserved journal/hash, no new journal query')
        summaries[role]=project(r.stdout,literals)
    value={'actualExit':0,'source':'0ea400109d79e47327d9fff105ff763f9310a31f','originalJournalsRequeried':False,'messagesNeverPublished':True,'fixedLiteralProjection':summaries,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'projections':{k:[r for r in v if r['knownFixedLiteral']is not None]for k,v in summaries.items()}}))


if __name__=='__main__':main()
