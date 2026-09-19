# NK-DAT-001 Inbox検査実行結果

2026-09-20 最新確定: dev-foundation/source 1d5b44ad26736366950936653914f67e7e096fe2、正式PT-WEB-20260920-03（02:01:07～02:16:34 JST、Maven15:26/exit0）、全1463件（Protocol80/Storage74/API660/Web241/Batch367/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3method限定静的レビュー・coverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと48負canary成功。DB29部品266＋Batch25部品281＋OPS15部品126＝69部分成果673 PT（全1463の内数）。今回9月19日再開比+48 PT/+4部分成果、PG184のroot検証・全4file照合からDB両step原子確定caller8PTを追加認定しSSC067限定完了。PG178～183のSQL資源905複合は既存Test ID内で新件数増算0。BUG195/206・YKT154/162・SSC063の別境界分類は継続。PG185試験並列化/PG186・SSC068 private子生成は仕様のみ。実archive/7世代/親実子制御/全cleanup/通常Question/Web/Logout/QA045/実NK互換gateは未完了、固定加重約4割（35～50%、456）を維持。利用枠残76%で継続、元dev-web3file保全、IT/ST完了ではない。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/inbox-inspection/manifest.jsonの現行SHA-256は `d25e489432d334772f918c6d7424e33494c135f8c97abf4ff983ce29daaa1e34`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

## 1. 現状

最新回帰PT-WEB-20260909-18、source56935aa0、2026-09-09 09:44:09 JST終了、全838件/全coverage100%/静的解析0、構造8件も再PASS。最新manifestのhashは `7c3b5cccddb0137fa60c19865f19a71019099cc22752bbfdba826494ec2701a1`。以下のrun13/hash表は証跡commit d0f27656時点の履歴であり、最新manifestのhashとは区別する。認証参照8件の結果は006、SQL境界8件は008。

PG-D-119の構造検査8caseは正式PT-WEB-20260909-13で成功。source e00e1855f8e818f04b3ba8a18605710969bfe7c7、2026-09-09 07:36:25～07:41:29 JST、dev-foundation、exit0。全798件（Protocol80/Storage34/API402/Web241/CHR41）成功、failure/error/skipped0。対象5moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。8collector成功と全checksum照合を確認。Program全体の完了ではない。
対象は003のPT-DB-INBOX-001～008。DB参照・backup/期限・削除transaction・権限・oneshotは未実施であり合格へ算入しない。

## 2. 探索履歴

| 実行 | 結果 | 独立根拠・是正 |
|---|---|---|
| 2026-09-09 07:20:15 JST終了、dev-foundation/c7744d84＋新規source/test、exec session75782 | 8件、failure1/error0/skipped0、Maven exit1、非合格 | PT-DB-INBOX-003のoffset533 `000`にfalseを期待したtest oracle不備。UI234 §5.3はN3/昇順で0を禁止しない。BUG-075/YKT-067を修正前e566b01dで起票 |
| 2026-09-09 07:23:03 JST終了、dev-foundation/e566b01d＋修正test、exec session29088 | 8件成功、failure/error/skipped0、Maven exit0。Protocol5/Storage16も成功 | 000/999/同順位正常、非数字・降順異常を独立追加。Production変更なし。追加classのline37/method3/class1/branch28のmissed0、SpotBugs0/NullAway/Enforcer/format PASS。部分探索coverageなので全体完了は宣言しない |

実行commandは003 §3。生ログ・鍵・暗号入力・DB dumpはGitへ保存しない。正式証跡は `evidence/inbox-inspection/manifest.json` と `results.xml` に出力し、過去のDB15件の証跡は上書きしない。

## 3. YKT-067の照合

| 対象 | 判断・再発防止 |
|---|---|
| Display order | wire N3の0..999・同順位を正常、降順/非数字を異常とする。DBのpositive制約を転用しない。PT003 |
| Total/record count | 空0と1/最大10を正常、DATA/header不一致を異常。PT001/002/003 |
| header/data/record/total length | wire定義の厳密値と実byte数を独立照合、±1/短縮/1MB超を拒否。PT002/005 |
| owner/message | N3と混同しない。identityのN12/UUIDとAAD照合。未知ownerに認証を与えない。PT002/007/008 |
| 時刻 | wire millisecondと保存microsecondの精度変換を区別。同millisのμs違いを正常、隣接millisを異常。PT005 |

BUG-075/YKT-067は上記正式全回帰で再試験完了。BUG-014/YKT-012はSQL/参照/起動まで継続。

## 4. 正式01の制限と再試験

PT-ADM-20260909-01（source 5e418c70）は全798件成功、全module build/coverage/静的解析PASS。構造8件も成功したが、BUG-076のcross-manifest参照不備により新004のtrace gateは非合格。生成manifestのscopeResultは構造試験だけを表し、全品質gateの合格として使用しない。
Web collector015はPT-WEB prefix専用のため当該run IDを受理せず、旧Web証跡を更新していない。次回は全collector共通のPT-WEB prefixでclean実行する。未収集を合格へ加算しない。
BUG-076の修正前起票は391ea854。相対参照を実pathから計算し、出力前に参照先の同一性・存在・hashを検査する。017の独立fixtureで正しい3段pathを受理、誤った4段/別file/改ざんhash/不存在/範囲外参照を拒否する。再試験後に正式runとhashを固定する。

## 5. BUG-076/YKT-068再試験証跡

修正e00e1855、正式PT-WEB-20260909-13の全8collector成功。017の独立path/hash負canaryは2026-09-09 07:42 JST頃exit0、1 test/0 failure。006を最初に収集し、他7collectorは同run/sourceの008manifestを照合してから実結果を収集した。
004の新nested manifestは `../../../008_NK-SCN-001/evidence/manifest.json` に解決し、参照hashと実file SHA-256一致をcollector内で確認。全manifestのfilesは当該directory基準、003/006/007/008/009/010/015と新004の全checksumsを `sha256sum --check --quiet checksums.sha256` で照合しexit0。旧004のhistorical DB証跡は別実行であり新規Java8件の全体完了へ流用しない。

| 証跡path（本directory基準） | SHA-256 |
|---|---|
| evidence/inbox-inspection/manifest.json | 4d1d67d7ed9aef8e378bbad283d562fdbc75a4a26e31a7cd9ae17a1c08fa6fdf |
| ../008_NK-SCN-001/evidence/manifest.json | 60377a907dd261b745e51948731977a5c85de708394dd26cb542731363b9a063 |

BUG-076/YKT-068は本再試験で完了。Production構造期待値の変更なし。認証参照PT009～016は別005/006で管理し、この798件へ未実施分を加算しない。
