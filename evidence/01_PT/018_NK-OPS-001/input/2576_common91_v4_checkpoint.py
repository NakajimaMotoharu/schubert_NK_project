"""Preserve actual original failure, owned new-run cursor and next command without acceptance inflation."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
r=Path.cwd();s=r.parent/'PMO/pgpt-completion-stage-20261102';state=sys.argv[1];source=sys.argv[2] if len(sys.argv)>2 else None
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379/pg30748-haruka-common91-v4'
original=json.loads((b/'evidence/PG30734-common91-original-terminal-independent-xml-preservation-v1/manifest.json').read_text())
record=dict(atJST=now,state=state,source=source,productionCoreMain='2ebbdf391873a5be6247ea59cb9addffb886c591',remoteRun='/home/mini/schubert-nk-pgpt/runs/pg30748-common91-v4',privateLocal=str(w),wholeCases=91,newDefinitions=0,main5Physical10=True,originalV3=dict(source=original['source'],actualExit=1,tests=91,failures=0,errors=29,skipped=0,rawSuccessesNotQualified=62,toolOnlyNotAppRoster=True,retained=True),originalGroupEstimate=dict(low=.85,base=2.55,high=5.1),revisedGroupEstimate=dict(low=1,base=3,high=6),originalCapPp=6,formalTests=1964,formalScopes=53,effortRate=None,globalUnknownCwd3StillUnknown=True,aruAllAccessProhibited=True,currentToolSession=None,unitRepeated=False,nextCommand='Observe existing phase begin/terminal before any action; never repeat v1/v2/v3. v4 new-only stage/prepare with fresh quota; require standard7resource exact hashes, exactsource static admission then ordinary91/true exit/independentpost singleexec/all10CRC-init/XML/fourcounters. No oldexecmerge, DB/Root/native/VM/keys/held scope access. Continue after group with quota reserve10%.')
if w.exists():
 for name,key in [('stage-receipt.json','stage'),('payload-config.json','config')]:
  p=w/name
  if p.is_file():
   a=json.loads(p.read_text());record[key]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
   if key=='stage':record['archiveSha256']=a['archiveSha256'];record['stageOwner']=a['owner'];record['stageOwnerMeaning']='EXITED_BOOTSTRAP_NOT_CURRENT_MAVEN_OWNER'
 record['localPhaseFiles']=sorted(p.name for p in w.glob('*-local-*.json'))
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 p=s/name;a=json.loads(p.read_text());prior=a.get('currentHarukaCommon60')
 if prior and prior.get('state')!=state:a.setdefault('harukaCommon60History',[]).append(prior)
 a['currentHarukaCommon60']=record;a['updatedAtJST']=now;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
note='共通v3真正Maven1・全91/F0E29S0/他62も未資格。元XML/exec/Main10をPG30734へ保存、原run再起動0。BUG2881 epoch0で標準Maven copy省略をPG30738vendor独立再現、v4はGit正timestamp+標準7resource hash gate、BUG2880 collector欠落明示/未知class非読取。PG30740工具3条件0・全18Java/POM不変、新製品定義0。現在'+state+'。元群.85/2.55/5.1/見直し1/3/6cap6とv454残839.186未較正維持、App107/4337/4308/歴史29/正本184・正式1964-53/工数null。aru全非接続・globalcwd3UNKNOWN・全HOLD維持。source='+str(source)+'。次は上記専用v4元phase照合→通常91/独立post、元成功再確認や旧run再発行0。'
for pattern in ['456_*','460_*']:
 p=next((r/'documents/400_PGPT/450_品質').glob(pattern));text=p.read_text();pos=text.find('\n')+1;p.write_text(text[:pos]+'\n## 最新checkpoint（'+now+'、common91工具是正・元失敗保持）\n\n'+note+'\n\n'+text[pos:])
print(json.dumps(dict(actualExit=0,state=state,source=source,originalFailed91Preserved=True,formalAcceptanceAdded=0)))
