# NK-DAT-001 Inbox検査実行結果

## 1. 現状

PG-D-119の構造検査8caseは探索成功。正式clean gate・証跡収集前でありProgram全体の完了ではない。sourcecommit/正式日時は確定後に記録する。
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

正式全回帰と証跡が揃うまでBUG-075/YKT-067は再試験待ち。BUG-014/YKT-012はSQL/参照/起動まで継続。

## 4. 正式01の制限と再試験

PT-ADM-20260909-01（source 5e418c70）は全798件成功、全module build/coverage/静的解析PASS。構造8件も成功したが、BUG-076のcross-manifest参照不備により新004のtrace gateは非合格。生成manifestのscopeResultは構造試験だけを表し、全品質gateの合格として使用しない。
Web collector015はPT-WEB prefix専用のため当該run IDを受理せず、旧Web証跡を更新していない。次回は全collector共通のPT-WEB prefixでclean実行する。未収集を合格へ加算しない。
BUG-076の修正前起票は391ea854。相対参照を実pathから計算し、出力前に参照先の同一性・存在・hashを検査する。017の独立fixtureで正しい3段pathを受理、誤った4段/別file/改ざんhash/不存在/範囲外参照を拒否する。再試験後に正式runとhashを固定する。
