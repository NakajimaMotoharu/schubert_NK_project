# NK-DAT-001 検査resource寿命 単体テスト仕様書

RD DAT-009/OPS-009/FIL-006、UI212/241/251、SS343 §6.7/324/341/352、QA-046/UIC-006/SSC-049/PG-D-143。InspectorSettings、InspectorApplication.execute、共有URL/version検証を対象。実main/unit/親OS/backup実体の合格を含まない。

## 1. 独立fixture・期待値

公開path/URL/version境界、JDK標準Path/UUID/Instant、実TempDir/保持inode/独立byte credential、隔離PG18.6のDDL後条件を使う。合成privileged metadataはportへ明示注入し実root配布成功と誤記しない。正系DB authenticationそのものは047/PT207を回帰し、本試験のtrust fixtureをSCRAM認証の証明へ用いない。鍵はruntime CSPRNG、passwordは公開fixture（実環境に使用不可）、証跡へ本文やrawログを出さない。root/entry/DB資源の取得・解放回数と公開FD操作結果で寿命を照合、private reflectionは禁止。

## 2. Test ID

| ID | class/method | 事前条件・入力・操作／独立期待値 |
|---|---|---|
| PT-DB-INBOX-209 | InspectorSettingsTest.validSnapshot | absolute正規path/canonical URL/合法version集合。入力集合変更は非伝播、返却集合不変、toString固定 |
| PT-DB-INBOX-210 | 同.invalidSettings | null/相対/root/dot・dotdot、空/不正URL・port/host、空/不正/null versionをIO前拒否 |
| PT-DB-INBOX-211 | 同.sharedValidation | provider/Processと同じURL/version受理境界、version長1/16/17・URL port1/65535/65536、異常値を露出しない |
| PT-DB-INBOX-212 | InspectorApplicationTest.successAndResume | 実DB同run backup2成功・候補0でEND/SUCCESS。再実行は同永続累積、毎回別root/provider寿命、全FD解放 |
| PT-DB-INBOX-213 | 同.protectedResult | 不正暗号1候補は保持しEND/WARNING/protected1、最後のclose後だけ結果返却 |
| PT-DB-INBOX-214 | 同.databaseFailure | SQL gate/接続障害でSTORAGE_FAILURE、row削除なし、全資源close |
| PT-DB-INBOX-215 | 同.credentialFailures | password不存在/不正、AES途中欠落/同用途・世代不正で例外。既取得FD/copy回収、DB変更なし |
| PT-DB-INBOX-216 | 同.rootFailures | open/最後のclose故障で結果返却なし。close故障後の再開はDB永続結果を読み直す |
| PT-DB-INBOX-217 | 同.nativeAdmission | default実Linux factoryでRW/非専用rootを拒否。別metadata portの正系を実root認可と混同しない |
| PT-DB-INBOX-218 | 同.nullContracts | settings/native/io/runのnullはconstructor/execute境界で拒否、run null時IO0 |
| PT-DB-INBOX-219 | 同.interruptedExecution | 割込flag維持、内部結果INTERRUPTEDを成功にしない、外側で取得済resourceも全close |
| PT-DB-INBOX-220 | 同.concurrentLifetimes | 独立操作を並行実行し借用native portをcloseしない。各root/entryを回収、設定snapshot非変化、実DB競合試験は既存run PTを回帰 |

## 3. 正式gate・再現

421のJDK25.0.4+7/Maven3.9.12/PG18.6/JDBC42.7.13で探索後に新source commitを固定しroot clean verify。全Javaのline/method/class/branch100%、NullAway/Spotless/SpotBugs、failed/error/skipped/not-run/flaky0。新scopeを固定inventoryへ追加し全collectorの同run/source/hash/traceを照合、017/019負canaryを別集計する。050・evidence/inspector-application/manifest.jsonへ12 Test ID・日時/環境/branch/source/command/exit/期待・実際/coverage/関連BUG/SSC/hashを保存する。未実装・探索は合格へ算入しない。
