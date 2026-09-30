# 正規issuer接続 実行結果

## PG395変更群の選択検証（未認定）

JDK25.0.4/Maven wrapper、Linux development host、dev-foundation/HEAD7b0d7f6a3＋明記した未commit差分。実Source/fullrun固定前の限定結果で、PG394 actual execや正式run24とは合算しない。

| 時刻JST | command対象 | PT/F/E/S・静的 | log/hash |
|---|---|---|---|
| 02:28:08 | Storage/Bootstrap/Batch、LinuxMonotonicClock/FixedServiceIdentity/ApiNonSecretConfig/WebNonSecretConfig/MorningExpirySession、spotless apply/test/spotbugs check | 28/0/0/0、3module各Bug/Error0 | work/pgpt-runs/PG379/pg395-issuer-owned-selected.log、SHA256 5d54b207c0dd381551856cb6201b652ad320ed3b35c1fe494eab1695603f626b |
| 02:36:02 | 上記＋CleanupTerminalRepository/MorningProcessMain | 44/0/0/0、3module各Bug/Error0 | work/pgpt-runs/PG379/pg395-issuer-steps-selected.log、SHA256 5ef61a17e8fca3f22085456a9e1acbad822c35108cfb8589a516e2936bede4c0 |
| 02:42:54 | 上記＋MorningUnitTerminals/MaintenanceUnitTermination/MorningControlScope/MorningBackupStage | 87/0/0/0だがBatch static1、build失敗・gate非合格、BUG372/YKT292 | work/pgpt-runs/PG379/pg395-issuer-stop-selected.log、初回失敗を保存 |
| 02:48:51 | 同87PT、BUG372はimmutable保存をList.copyOfで明示（除外/抑制なし） | 87/0/0/0、3module各Bug/Error0、直接是正・YKT全6未完 | work/pgpt-runs/PG379/pg395-issuer-stop-corrected.log、SHA256 6aad84cca4dfbd53fa737fb1e19f022a62fbc40211e708a6e1891c355d528c35 |
| 03:05:19 | 上記＋RootReleaseAdmission、Main actual config caller | 97/0/0/0、3module各Bug/Error0、ISSCFG002 | work/pgpt-runs/PG379/pg395-issuer-config-fixture-corrected.log、SHA256 c5aaeefd6c1a4cee37947706eceb6d8ae37f6d492a315bfd9ba9c51fabde06dd |

Root config初回compileはshared parseのchecked NoSuchAlgorithmException未宣言で`pg395-issuer-config-selected.log`に保存。次試験は新fixtureのcomment-only YAMLを正常mappingと仮定したため新ISSCFG002がerror、`pg395-issuer-config-corrected.log`へ非合格として保存。既存shared parserは「blankかmapping」だけを受理する契約でありProduction parser/oracleは変更せず、有効なmappingにcommentを付けたfixtureへ是正（protocol string '001'を明示）。独立hashは既存手書きGOLDENをNode cryptoで計算した固定vector。デフォルトだけでなくraw comment変更時に再読拒否することを確認した。新規接続/fixtureの最初の未完成試験として扱い、実装済み承認仕様違反に読み替えない。

ISSCFG001/ISSROOT001の固定NSS、ISSSTEP002/003を独立literal/実隔離PGで検証。現在SUCCESS auditと再開SKIP結果/handle/receiptを分け、実元SUCCESS全列を別読み取りする。STOP_SET値保存の選択runは02:43現在実行中、未実行issuer/発行途中root変化/APIWeb/CHR/全6/full coverageは合格にしない。選択はoffline固定repo、`-Dsurefire.failIfNoSpecifiedTests=false`、全対象classを明示、未対象scopeは未実行。過去単独bootstrapの旧installed Storage compile失敗は`pg395-shared-config-initial.log`へ残し、2module reactor修正で16PT成功（pg395-shared-config-reactor.log、02:01:47）、Production障害として加算していない。

2026-10-01、SSC126/295を実装前登録。現Source7b0d7f6a3/pushはPG394実Broker/Expiry証跡保存まで。issuer/publication/Root/APIWeb/CHRは未実行・未認定、正式run24/48.3%は不変更。次はshared strict configを再利用し同Morning内のactual roots/steps/gates collector→正規issue callerを接続、同変更群全回帰/同signedSource nativeへ継続する。実観測が不足するgateに任意digest/成功flagを入れない。
