# Login全154件の実行結果

Test source `1bc908a375875a4f10aca2d5218289377d30cb68`、Production Main `236ffddc83a08f1ba8f2ac5c3932e381371acd59`不変更、dev-foundation/push済。[仕様4047](4047_Login純交換・有限所有と未知例外消去_単体テスト仕様書.md)。実commandは1256 qualifierの`run 1bc908a375875a4f10aca2d5218289377d30cb68`。

PG26530-LOGIN-CONNECTED154は真正終了0、154成功、failed/error/skipped/aborted0。PG26532独立manifest SHA256 `934e043a179a8fb724556a21f9385e87fe71a1f2a35c49c572d851b3cdbbed20`。原Login6＋新1と必要共通147を同sessionで実行し、旧execを合算していない。新1内で未知NPE/Errorの同一instance・caller password/sender clone消去・fresh UUID正常再利用を各2回確認。

| counter | covered | missed |
|---|---:|---:|
| line | 3707 | 0 |
| method | 786 | 0 |
| class | 168 | 0 |
| branch | 1084 | 0 |
| instruction | 18390 | 0 |

188physicalを全入力保持、172positive Mainの当CRC一致、自然Code不在16・標準synthetic switchmap4を別々に検証。手動coverage除外なし。元六は製造時逆変換一致、二worker ownerはfinally shutdownNow/await5assert、actual JVMも期限内に終了した。

fresh Java25/ErrorProne/NullAway0、全12physicalはnormalとbyte一致、fresh全12ClassStatsのSpotBugs0/missing0/error0、PMD raw15は全個別文脈非該当、適用/未分類/CS/error0。根拠・元XMLhash・環境・実command/exit・source/run・入力と期待/実際・coverageは[PG26532 manifest](evidence/PG26532-login-independent-v1/manifest.json)およびpreflight26528。

BUG2664/YKT2344の当二ownerを限定CLOSED、global2177は未完。全入力はsynthetic、IPはliteral parseのみ。実認証・HTTP/session・DB・鍵・broker・VM/native・Root・held四classへの操作なし。P00502全owner/C04/F02F03/全451は未受入、正式1964PT/53scope・元190新規受入0・工数率nullを維持し、IT/ST完了を宣言しない。
