# 1528 C03 当source設定個別受入matrix

2026-10-23、初回九項目達成後の独立一群。WBS-C03、source e7d64fda2453e906ee6ccc5fe718e5c29841e4aa。着手前見積.25/.60/1.50pp、共有群上限10ppをeventsで凍結。前群受入を再実行せず、必要終了依存なしの設定群だけを扱う。実配備操作/Production追加は元costScope対象外で、F03/実VM等のHOLDを解除しない。

## PG・独立oracle・scope

正本origin/main SS342§6.1～6.3/§9と当branch同byte、関連RD SYS/DAT/PER・UI212/253、既SSC069/QA043/UIC003の承認値を適用。PGとして全二owned templateと共有001_roles.sql、PostgresDeploymentTest全method/helper/fixture所有を点検した。実装は正しく、修正不要。1518の全要件/八TestID matrixと原6946 witness9695e383をそのまま使用し、名称やcounterだけで受入にしない。

| criteria | 独立期待値／実原証拠 | 受入範囲 |
|---|---|---|
| contract | SS342の32 directive、loopback限定/5432/40connections・memory/WAL/checkpoint/SCRAM・SQL/parameter本文抑止。PGCFG001/002/006は明示literal、PostgreSQL18自身のparse/単位変換/不正quote/未知GUCの元actual exit。HBA16順序を003/004/007でliteral＋catalog全列＋parse errorへ対応。005は7role20timeoutの実SQL後条件（Inspector idle未設定） | 設定templateとrole timeoutの承認契約。運用serverのeffective値や任意primary error MESSAGE秘密非出力を宣言しない |
| scope | 二owned fileを485/master/Git/source archive/currentで全hash一致。SQL/Testはshared参照費0。支援class/追加機能/新scopeなし | 481定義の二artifact全体、logical190不変更 |
| quality | 同source4222/660真正0の八元method/独立全Test byte/元XMLへ一意join、正常・境界・欠落/空/null・不正設定・権限policy負値を確認。008で自己生成target fixture/loopback/元HBA復元・raw logコピー無し。fixture stopはe7で既是正済み所有DBを解放する契約 | 宣言templateにJava四counterなし=N/A、100補完/適用除外追加0。新Production PT/VM操作0 |

同期/再送/並行は設定file評価には非該当（状態を持つdeliveryやmigration処理は別WBS）。HBA actual native parseは旧PGCFG fixture内の自己生成DBに限る。remote接続/原本DB/実credential/配備先権限/active config drift・OS logの実検証はN等の別runtime受入として残り、本群の完了で満たしたとしない。明示元費境界の分離であって品質条件を後から削らない。

## 原証拠・受入方法

`PG6946-c03-current-criteria-v1/manifest.json` SHA256 **9695e383d3af6f227e9d01fecc37063faa7f304ad463c8090a7368d808a2546c**、元PG6930/e7/Q728682a9の八case、1518のcommand/環境/元source/原hashを継承。成功確認目的の再実行はしない。既9記録を完全保持したsource別追加registerを作成し、元strict criteria/hash/source/終了依存と独立registry改変拒否を確認後だけ新C03を計上する。

静的template一致だけをnative parse成功の代用にせず、元actual native caseを参照する。元witnessのacceptedLeafDelta0は当時のローカル根拠のみという履歴値として不変更。今回の個別PG受入は別register/結果文書へ保存し、古い履歴17や正式1964/53へ混ぜない。工数率null、QA051final/PTALT0・全HOLD維持。
