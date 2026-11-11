# 保護業務全163件の実行結果

Test source `a3766cdf52f91022d72aaa509a2301bb39161bbb`、Production Main236ffddc83不変更、dev-foundation/push済。[4049仕様](4049_保護業務十八種NPE消去・容量回復_単体テスト仕様書.md)。実commandは1264 qualifierの`run a3766cdf52f91022d72aaa509a2301bb39161bbb`。

PG26558-PROTECTED-CONNECTED163は真正終了0、163成功、failed/error/skipped/aborted0。独立PG26560 manifest SHA256 `c5ad1d60e32b09e3873d7c036b9618a10431b8b1f685eb02c76f34910a393af9`。Business原12＋新1、Exception原3、Client10/Registry7/Protocol130を同sessionで実行。新1内で18種すべてのNPE同一instance・送信clone消去・相関解放と、明示fresh UUIDでの容量再利用18回を確認。元12と既finite workerを変更していない。

| counter | covered | missed |
|---|---:|---:|
| line | 3738 | 0 |
| method | 800 | 0 |
| class | 175 | 0 |
| branch | 1086 | 0 |
| instruction | 18579 | 0 |

全194physicalを保持、179positive Main CRCは当byte一致。自然Code不在15と標準switchmap4を区別し、手動除外・旧exec合算なし。fresh Java25/ErrorProne/NullAway0、Main全18ClassStats SpotBugs0/missing0/error0、Main全18normal byte一致、Test PMD raw5は全件既有限worker文脈非該当・CS/適用/未分類/error0。Exception原3の全file styleも別途26555=0。

実日時・OS/JDK・command/exit・source/run・入力/期待/実際・XMLhash・CRC・coverageは[PG26560 manifest](evidence/PG26560-protected-independent-v1/manifest.json)。BUG2666/YKT2346の独立post件数誤記は実行前に26564で保存、五post ASTを照合後に狭く是正し、元163試験を再実行せず独立回収した。BUG2665/YKT2345は実Web一次015二fileへの四群trace漏れを追記訂正、原event/試験結果/費用は保持。

実認証・HTTP/session・DB・原本/Backup/鍵・broker・VM/native・Root・held四classへの操作なし。値例外Scenarioだけを使いScenario実FSへ進まない。P00502全owner/C04/F02F03/全451は未受入、正式1964PT/53scope・元190新規受入0・工数nullを維持。新定義・局所実行数をPGPT全完了やIT/ST合格へ転用しない。
