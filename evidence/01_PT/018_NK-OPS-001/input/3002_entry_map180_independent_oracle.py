"""Independent literal ID joins and COPY bytes; no production import, DB or product PT count."""
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';stamp='2026-01-02T03:04:05Z'
source=[['-20','1','-5','0','1','dialogue','-30',' Alice / label ','Hello\nworld','text\t\\raw'],['10','2','5','2','3','narration',None,None,'other','raw2']]
files={(1,-5):900,(2,5):700};entries={-20:(800,1),10:(600,2)};speakers={(1,-30):500,(2,30):400};joined=[]
for row in source:
 eid,order=entries[int(row[0])];game=int(row[1]);speaker=None if row[6] is None else str(speakers[(game,int(row[6]))]);joined.append([str(eid),row[1],str(files[(game,int(row[2]))]),str(order),row[3],row[4],row[5],speaker,row[7],row[8],row[9],stamp])
expected=[['800','1','900','1','0','1','dialogue','500',' Alice / label ','Hello\nworld','text\t\\raw',stamp],['600','2','700','2','2','3','narration',None,None,'other','raw2',stamp]];assert joined==expected
copy='800\t1\t900\t1\t0\t1\tdialogue\t500\t Alice / label \tHello\\nworld\ttext\\t\\\\raw\t2026-01-02T03:04:05Z\n600\t2\t700\t2\t2\t3\tnarration\t\\N\t\\N\tother\traw2\t2026-01-02T03:04:05Z\n'
def escape(value):
 if value is None:return '\\N'
 return value.replace('\\','\\\\').replace('\t','\\t').replace('\n','\\n')
assert ''.join('\t'.join(map(escape,row))+'\n' for row in expected)==copy
p=i/'3002_entry_map180_independent_oracle.json';assert not p.exists();p.write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),metadataOnly=True,sourceRows=source,fileMapping=[[1,-5,900],[2,5,700]],entryMapping=[[-20,800,1],[10,600,2]],speakerMapping=[[1,-30,500],[2,30,400]],targetLiteralRows=expected,copyLiteral=copy,copyUtf8Sha256=hashlib.sha256(copy.encode()).hexdigest(),sourceRequiredTextPositions=[5,6,9,10],requiredNullRejectedBeforeRowToAvoidAccidentalNpe=True,actualProductTests=0,productionExpectedMethodUsed=False,actualDatabaseOrGeneratorExecution=False),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,metadataOnly=True,literalRows=2,literalCopyBytes=len(copy.encode()),productTestsExecuted=0))
