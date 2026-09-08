# 暗号session lifecycle探索・BUG-057/YKT-052

2026-09-08 JST、dev-web。NK-WEB-001、FUN-001/AUT-001～004、UI226 §6、SS314 §7.2.4/331/352、SSC-041/PG-D-098/PT-WEB-036～043。JDK25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13/Flyway13.4.0/JaCoCo0.8.15。Production DDL/roleを使う隔離合成DBのみ。秘密値、実session、DB dump、raw JVM logは格納しない。

## 先行起票と横展開

f6dde98でBUG-057/YKT-052を修正前登録。破損rowが既に存在するload経路で、deleteByHashのfalseを見落としてOptional.emptyをcommitしていた。探索01で16437byteの不正row＋公開JDBC DELETE0件を注入して期待固定障害に対する失敗を再現。require(true)を追加し、探索02以降で削除不能時のrollback/固定例外、成功時だけ削除commit後の不在を確認した。期待値/DDL/Current baselineは変更しない。

| 横展開対象 | 修正/非該当根拠 | 再発防止test |
|---|---|---|
| 構造/NULL不正rowのhash delete | BUG箇所、戻り値を必須検査へ修正 | 037/041、不正row＋0件・SQL/commit失敗、元row残存、成功削除 |
| expiry/暗号tag/key/AAD/schema不正のidentity delete | 既にrequire true、修正不要 | 037/041、境界前/一致/後、全不正分類＋0件/commit失敗と隣接row保持 |
| authenticate旧row delete | 既にrequire true | 039/041、0件/各SQL・commit故障、Cookie/UUID/CSRF・別row UUID衝突、全rollback |
| version上限rollover旧row delete | 既にrequire true | 040/041、0件/UUID衝突rollback、同Cookie新PK/0と旧PK CAS拒否 |
| 明示invalidate hash delete | 不在0件を許す冪等契約のため非修正 | 038/041/043、連続失効・未知ID・不正更新数・commit/close・並行非復活 |
| 低位JdbcWebSessionStore | delete/replaceはfalseを返す契約、insertは1件必須 | 024～031既存全実DB/公開JDBC fault回帰。lifecycle側で必須結果を検査 |

## 探索記録

| run末尾 | 終了JST | exit/結果 | raw log SHA256（/tmpのみ） |
|---|---|---|---|
| compile-01 | 20:32:05 | 0、compile/NullAway | 66b1e4c562d4df0cb1082cc333231f6060baf41db5fdef45ed4a694e8e03c5a1 |
| explore-01 | 20:36:56 | 1、新1件がBUG-057再現FAIL、既存store8 PASS | 6616aa774cea755a5ec0f43d9319cdc551de883d2be6953c181dd36e33c40aa3 |
| explore-02 | 20:39:19 | 0、修正後1件＋既存8 PASS | 29f00cfd5f2d4721859195c79cab61c1bbbd5188ea4311ffe83daa034b52bbcb |
| explore-03 | 20:44:10 | 0、新7件＋既存8 PASS、fault matrixは未実装で合格数へ算入せず | e299f2eb97459b51f48bc7bd93345ad1cea85a504dabb040183a72185e02339c |
| explore-04 | 20:47:15 | 0、新8件＋既存8 PASS、対象全branch/line100% | cc28f11716c5552d294679471166f212345daa60d06ed9a6e3c99e9a0fdc3fed |
| explore-05 | 20:54:16 | 0、未発行CSRF/別row UUID衝突/10token並行追加削除を補強、新8＋既存8 PASS | 2fd1fdf545a0abd493d105d6b90b65fd1a06712ec36e01b2bc016532ff9511ed |
| explore-06 | 20:55:06 | 0、全破損分類の削除0件/commit失敗・AAD結合を補強、新8＋既存8 PASS | 61f244fd0acb5918af4bac7b3041b64b1290f3c995d2e0836702b41ef941bbab |

run prefixは`PT-WEB-lifecycle-`。探索coverageは累積であり、正式clean verifyが最終gate。除外/suppression/private reflectionは追加なし。JDBC proxyは公開interfaceだけへの故障注入。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-web -am -Dtest=EncryptedWebSessionRepositoryTest,JdbcWebSessionStoreTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

期待値は手書JSON、DataOutputStream LP/JCE独立復号、明示SQL後条件。新ID/hash/UUID/µs時刻/8h/version/移管属性を独立固定値へ照合。commit前失敗はrollbackを試み、commit後close失敗はDB確定があり得ることを操作別件数と次lookupで確認する（既commitをrollbackしたと偽らない）。100現在値mutationと10token並行追加・削除で他属性保持、30失効raceで再生成なし。Clock/key/provider/null設定やrow不正を正常認証へ変換しない。

## 正式gate

正式PT-WEB-20260908-06、source01e378340b334fba5f51442384761afe818d56ae、20:56:12～21:00:30 JST、exit0。全668件（Protocol80/Storage34/API394/Web119/CHR41）、新8件を含むWeb43件PASS。全5対象moduleのline/method/class/branch各100%、NullAway/Enforcer/format PASS、SpotBugs0。SSC-041/BUG-057/YKT-052全対象再試験完了。002/manifest/checksumsで実行環境・Test ID・hashへ追跡。Spring adapter、HTTP Cookie、Security/CSRF filter、API revoke queue/監査、全画面、実NK Characterizationは別残件。IT/STを完了扱いしない。
