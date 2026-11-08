"""Prepend source-bound current facts to five PGPT reports; preserve every historical byte."""
from pathlib import Path
import hashlib,json,subprocess,datetime
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG24622-latest-handoff-update-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
proofPins={
'evidence/01_PT/002_NK-PRO-002/evidence/PG24546-protocol-independent-limits-original15-new1-independent-v1/manifest.json':'b8f150d8368f7d43413142c06a424684c34549e5c43929f5e14f0b8a1a97cb79',
'evidence/01_PT/002_NK-PRO-002/evidence/PG24584-protocol-whole119-independent-v1/manifest.json':'e154d86f98f935f9624d63e50e62c83d5cba1821c544bf563d841fac2800b077',
'evidence/01_PT/002_NK-PRO-002/evidence/PG24594-protocol-whole-denominator-v1/manifest.json':'9448c8cf89988f4d9a579ea10c433e8bad3e417c1df7709472648d1b29638dfe',
'evidence/01_PT/018_NK-OPS-001/evidence/PG24604-g07-pmd-vendor16-independent-v1/manifest.json':'c6dcdaeff82fabf27afea0152be0fd5cef819757c96a462353c653cba59a301b',
'evidence/01_PT/018_NK-OPS-001/evidence/PG24614-g07-existing-sdk-alias17-independent-v1/manifest.json':'2519676a16fa935072c8e971d7ed5e5da0f51232cf8037571bfa91939aee5825'}
for n,h in proofPins.items():assert sha(R/n)==h
new,whole,denom,vendor,aliases=[load(R/n) for n in proofPins];assert new['actualExit']==whole['actualExit']==denom['actualExit']==vendor['actualExit']==aliases['actualExit']==0
assert new['newUniqueTests']==1 and new['requalifiedExistingTests']==15 and new['tests']==16 and whole['tests']==119 and denom['counts']['measuredClasses']==159 and denom['coverage']['CLASS']==dict(covered=159,missed=0)
assert aliases['cumulativeClassified']==1213 and aliases['remainingUnclassified']==3280 and 1213+3280==4493 and aliases['actualSecretCount'] is None and vendor['newFalsePositives']==16 and aliases['newFalsePositives']==17
assert not subprocess.check_output(['git','diff','--name-only',whole['source'],'--',':(glob)src/**/src/main/java/**/*.java']).strip()
subprocess.run(['git','merge-base','--is-ancestor','42450b5','origin/main'],check=True)
now=datetime.datetime.now().astimezone().isoformat();lines=[
'<!-- PGPT-CURRENT-20261108-HANDOFF-BEGIN -->',
'## '+now+' 最新技術成果（PG/PT継続中・工程未完了）',
'',
'この追記を下段の過去報告に優先する。正式認定は **PT-WEB-20260925-24／1964PT／53scope** のまま。歴史WBS17/190と今回新規受入0件を分離し、**工数完成率は未較正null**。下段の旧割合・未回答QA・実行中job・VM/PID/boot記録は現在値に読み替えない。',
'',
'| 区分 | 当時点の確認済み事実 | 証跡 |',
'|---|---|---|',
'| Production Main | `7aed8eace7c844c2f79f2e39db766faf914890d5`。配置・実起動の認定ではない | normal PG22084/PG22086、各当run source照合 |',
'| 匿名Log追加 | source `'+new['source']+'`、既存15＋新規1＝16件成功。新規はPT-PRO-QA054-013一件だけ | PG24544／24546 `b8f150d8`、Program002仕様090/結果091 |',
'| protocol全体 | Test source `'+whole['source']+'`、24fixture119件一回OS0/FESaborted0。実line3478/method742/class159/branch1014、全miss0・module四counter100 | PG24582／24584 `e154d86f`＋必須母数補足PG24594 `9448c8cf`、Program002仕様092/結果093 |',
'| 母数と限界 | 入力176＝XML/classinfo169＋注釈7、169＝実測159＋interface6＋標準compiler filter4。raw24584の誤命名field169はXMLentryであり実測class159は24594へ訂正。自然branch0の118SourceはN-A/null、全Source非空四100や全451へ換算しない | 24594現byte/CRC/公式filter、手動除外0、旧exec合成0 |',
'| distinct追加試験 | 累計519＝Java415＋HTML97＋CSS7。119の再資格や上記16を再加算しない。候補114/pending12/旧whole93は暫定 | 4464/4466/4468/4470、456/460の保存点 |',
'| G07原検出 | 原4493中、分類1213／未分類3280、別container限界22、actualSecretCount=null。新16＋新17は元座標非重複、後者は既SDK証拠を再利用しartifact IO0 | PG24604 `c6dcdaef`／24614 `2519676a`、018仕様3884/3886・結果3885/3887 |',
'| QA-055 | 回答「現行の固定文を維持する」。Login画面は固定15分文、実待ち秒はHTTP Retry-After。設計main42450b5/PR207へ反映済みで再確認不要 | 911/UIC012/SSC338、局所DOM/header証跡21044/21064と後続元28再資格24414は別run |',
'',
'**残るPG/PT受入条件**：同source全scopeの451/独立oracle・trace・秘密scan、未解決障害/横展開、実NK CHR、当source native・普通起動/owned停止と独立post、必要PR/merge・全成果保存。上記局所成功を全体受入やIT/ST合格へ加算しない。QA051 final、実VM/Root/cohort/DB/Backup/鍵/native・拒否対象未特定・held四等の既HOLDを維持する。外部job/VMの現在状態は未認証であり、host Unit119の終了0と混同しない。',
'',
'**Linux server引継ぎ前提**：PG/PT残件をIT/STへ転嫁せず、許可と所有が成立してから当boot/source/BOM/DB/原本Backup/Unit/actor/clientを再認証する。旧PID/permit/旧runを再使用・そのまま復元せず、不明な操作やRoot/配備/停止を再発行しない。IT/ST性能・運用の合格は後続の別工程で実証する。通常の報告・commit・本追記の作成では自走を停止せず、fresh残10%以下/取得不能等の既定停止条件に従う。',
'<!-- PGPT-CURRENT-20261108-HANDOFF-END -->',
'']
block='\n'.join(lines).encode();paths=['documents/400_PGPT/401_PGPT成果物一覧.md','documents/400_PGPT/460_完了報告/461_PG完了報告.md','documents/400_PGPT/460_完了報告/462_PT完了報告.md','documents/400_PGPT/460_完了報告/463_PGPTフェーズ完了報告.md','documents/400_PGPT/460_完了報告/464_IT・ST引継ぎ事項.md'];rows=[]
for n in paths:
 p=R/n;old=p.read_bytes();assert old==subprocess.check_output(['git','show',head+':'+n]) and lines[0].encode() not in old;first,rest=old.split(b'\n',1);after=first+b'\n\n'+block+b'\n'+rest;p.write_bytes(after);rows.append(dict(path=n,beforeSha256=hashlib.sha256(old).hexdigest(),historicalTailSha256=hashlib.sha256(rest).hexdigest(),afterSha256=sha(p)))
O.mkdir();(O/'latest-block.md').write_bytes(block);v=dict(actualExit=0,atJST=now,observerSource=head,productionCoreMain=whole['productionCoreMain'],proofPins=proofPins,documents=rows,blockSha256=hashlib.sha256(block).hexdigest(),documentsUpdated=5,historicalBytesPreserved=True,newProductTests=0,newAcceptance=0,formalUpdated=False,effortRate=None,pgptAllComplete=False,itStAccepted=False,allHoldsPreserved=True,toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,documents=5,oldTailsPreserved=True,manifestSha256=sha(O/'manifest.json'))))
