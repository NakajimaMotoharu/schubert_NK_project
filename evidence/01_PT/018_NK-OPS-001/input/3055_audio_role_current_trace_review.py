"""Current SQL comment/Program trace join only; retain exact Java-run source, never re-label it."""
from pathlib import Path
import json,hashlib,re,subprocess,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));post=b/'evidence/PG32642-audio-role818-post-v1/manifest.json';m=load(post);before=load(b/'evidence/PG32630-program-trace-correction-defect-v1/manifest.json');old=load(i/'3046_audio_role818_independent_oracle.json');pub=b/'evidence/PG32652-ssc396-programtrace-main-publication-v1/manifest.json';assert load(pub)['actualExit']==0
for path,h in m['inputHashes'].items():assert sha(r/path)==h
body=lambda s:re.sub(r'(?m)^--[^\n]*\n','',s)
current={}
for path in before['originalArtifacts']:
 original=subprocess.check_output(['git','show','0bed68f16b8e373ee5d06d89934695832b4d8731:'+path],text=True);text=(r/path).read_text();assert body(original)==body(text) and 'NK-DAT-001' in text and 'NK-DDL-001' not in text;current[path]=dict(sha256=sha(r/path),sqlBodySha256=hashlib.sha256(body(text).encode()).hexdigest(),onlyProgramCommentChanged=True)
owner=next(x for x in load(r/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if x['id']=='WBS-P004-01');assert owner['program']=='NK-DAT-001' and set(current)<=set(owner['ownedArtifacts'])
e=b/'evidence/PG32654-current-ddl-programtrace-review-v1';assert not e.exists();e.mkdir();j=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),bugs=['BUG2943','BUG2945'],javaQualificationSource=m['productionCoreMain'],javaUnitSource=m['source'],currentSqlArtifactSource='67d1c94abbc5be46c49e7247a47361d474d5a1ea',javaRunNotRelabelledToNewCommit=True,allQualifiedJavaRunInputHashesUnchanged=True,sqlStatementsUnchangedFromIndependentGolden=ref(i/'3046_audio_role818_independent_oracle.json'),currentDdlArtifacts=current,old29AppliedSqlUnchanged=True,program='NK-DAT-001',owner='WBS-P004-01',costOwner='WBS-P019-03',mainTracePublication=ref(pub),authoringRecovery='Publisher path and branch namespace corrected before PR; existing branch/worktree never discarded.',actualDbPt='HOLD_NOT_RUN',ddlRuntimeCoverage=None,productTestsExecuted=0,newAcceptance=0,formalUpdated=False)
(e/'manifest.json').open('x').write(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
p=r/'evidence/01_PT/004_NK-DAT-001';assert not (p/'4238_V030音声role互換・DDL単体仕様とHOLD.md').exists();(p/'4238_V030音声role互換・DDL単体仕様とHOLD.md').open('x').write('''# NK-DAT-001 V030音声role互換・DDL単体仕様

Program NK-DAT-001 / WBS-P004-01、費用は共通原因BUG2943のWBS-P01903へ一回帰属。RD MIG003005006/DAT004/TST、UI223242254、SS311331343/SSC396397、BUG2943/YKT2472、識別訂正BUG2945/YKT2474。V030と030 rollback templateが対象。PG32606の旧V001..029 hashと3046独立SQL golden、PG32654現在Program/SQL body hashが独立期待値。

静的確認ID PT-DB-AUDIOROLE030-STATIC001..005: 001旧29SQL byte同一、002前進三DDLだけでrole varchar11/byte1..11、003切戻し七statementと明示TX/ACCESS EXCLUSIVE/既値>8なら固定RAISE、004無切捨て/改名/role-grant/他表列変更0、005正規Program/owner/source/artifact hash/Java39入力同一。これはsource静的確認で製品PT PASS・実測coverage・実DB安全を意味しない。

実DB Test ID PT-DB-AUDIOROLE030-001..008はすべてNOT_RUN_HOLD。前提は拒否HOLD解除と既正規auth/所有/隔離scratchDB・元Backup/全schema snapshot・承認済みsource/BOM一致であり、本資料が実行許可を発行しない。001 V029→V030/Flyway history030正常一回・旧29checksum不変、002実型varchar11/byte CHECK1..11、003movie_audio11保持/他列不変、00412byte拒否/NFC/NULL契約、005PK/UK/FK/index/role/grant/24table/75制約/原本不変、006>8byte存在時rollback全体拒否・値とschema不変、007<=8だけの隔離DBで元型/constraintへ原子的切戻し、008中途失敗rollback/再実行/競合lock・全connection/transaction返却を確認する。期待は明示catalog/postconditionと独立literal/前後snapshotで算出、Production methodから生成しない。

将来の実行は既正規DB試験経路のsource固定commandを当時のfresh認証後に記録する。client ON_ERROR_STOP=1必須。原本DB/現稼働server/未認証DBへ試し実行しない。DatabaseMigrationTest/MigrationInventoryはV030/30へsource更新済みだが本scopeではcompile/runしない。実行日時/環境/branch/対象commit/command/終了code/input/期待actual/DB後条件/coverageを取得してからmanifestとBUG/YKT再試験を更新する。現時点はcommand未発行・exit/実際DB結果/coverage=null、未実行を合格へ算入0。
''')
(p/'4239_V030音声role互換・静的確認結果_実DB未実施.md').open('x').write('# V030静的確認結果・実DB未実施\n\nPT-DB-AUDIOROLE030-STATIC001..005のsource reviewを3046/PG32654に保存。旧29byte同一、前進三DDL/切戻し七statement、guardとProgram NK-DAT-001/ownerを確認。独立golden・現artifact/SQL bodyのpath/hash・Source67d1c94aはPG32654 manifestへ記録。Java818はCore0bed68f1/Unit006de1ae/PG32640の別scopeの実行結果で、SQL runtime成功やSource67dの新PTとして加算しない。\n\n実DB001..008はNOT_RUN_HOLD、未発行command/exit/DB actual/SQL coverage=null。BUG2943/YKT2472はJava・静的対策済み/実DB再試験HOLDで未閉鎖。IT/ST合格は宣言しない。\n')
for name in ['001_NK-DAT-001_単体テスト仕様書.md','002_NK-DAT-001_実行結果.md']:
 with (p/name).open('a') as f:f.write('\n\nSSC396397/V030: [4238](4238_V030音声role互換・DDL単体仕様とHOLD.md)/[4239](4239_V030音声role互換・静的確認結果_実DB未実施.md)、PG32654 current artifact Source67d1c94a/Java Core0bed68f1 Unit006de1ae。SQL静的source確認のみ、実DB PT001..008 NOT_RUN_HOLD/coverage null、Java818をDB成功へ混ぜない。BUG2943/YKT2472未閉鎖。\n')
print(dict(actualExit=0,program='NK-DAT-001',sqlCommentOnly=True,javaInputsSame=True,dbRuntime='HOLD_NOT_RUN',productTestsExecuted=0))
