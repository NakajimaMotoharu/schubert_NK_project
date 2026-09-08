# 永続CSRF・POST filter接続探索

2026-09-08 JST/dev-web、NK-WEB-001/FUN-001/AUT-001～004、UI226、SS313/314 §8.1/351/352、PG-D-100/PT-WEB-050～053。先行仕様fa71ab2後に実装。実PG18.6/Flyway13.4.0/JDBC42.7.13とSpring Session4.1.1/CsrfFilter Security7.1.1/Mock Servlet6.1、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15。追加依存収束/取得元/hashは421 §5.8。

## 探索記録

| run末尾（prefix PT-WEB-csrf-filter-） | 終了JST | exit/結果 | raw log SHA256（/tmpのみ） |
|---|---|---|---|
| compile-01 | 21:31:25 | 1、初期依存1.17.1/1.16.7混在をEnforcer拒否 | 31ce3a3e222895763b373d807718dbf7be3f680cbad61f00c81e6a1cbb8fcbc8 |
| compile-02 | 21:33:25 | 0、候補1.17.0でcompile成功、最終採用せず | dbac96156acd631128488b40adc77c50b92aba98b5d4f0e31dffc758c48deeae |
| compile-03 | 21:33:51 | 0、Security POMと同じ1.17.1へ収束、compile/NullAway | 99207ffc4bf6461ad42091f8db371ab2903453b997f587e9ad217653bce57462 |
| explore-01 | 21:36:26 | 0、新4件/既存Spring6件PASS、新3class全coverage100% | ea1895359529d9f1d3c9b47bece5c4def5997247e925a78244b73b0984aa72c5 |

初期依存導入の収束過程であり、未成立候補をPG/PT合格にしない。新規実装済み挙動の違反は今回検出なし、新BUG起票なし。既存BUG/YKT再試験は正式全moduleで維持する。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=WebCsrfIntegrationTest,SpringWebSessionTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

本探索初回は追加jar取得のため上記-oを省いて実行、以後offline再現可能。独立literal CSRF tokenは制御CSPRNGの02/04/06/08 hex、HTTP期待は固定403/空200、後段call count0/1。DefaultCsrfTokenはrequest上だけで、Java serialization/DB object保存を行わない。input/expectedの秘密は合成fixtureに限り、raw request/cookie/CSRF値・JVM properties/stdoutをGit証跡へ出さない。

050は生成/load/既存rotate/principal保持/同値save/全null/type/不正保存/Logout後の冪等不在。051はdeferred提示、1値body・64/128・欠落/空/複数/null要素/未知字、header代替なし、decode後query key_csrf拒否。query値の文字列は変えず、不正escape検査はquery keyに限定する。052はSS313の10 POST操作（User同path4operationを含む）×7正常/拒否matrix、GET/HEAD/OPTIONS/TRACEのCSRF非適用とPUT/DELETE/PATCHの保護を確認。これらmethodの実routing/業務更新許可を認定する試験ではない。053は別session/旧fixation/expiry拒否、100並行同値成功、operationTokensを生成しないこと、DB open/commit/close/key故障の非成功。

## 正式gateと残件

正式PT-WEB-20260908-08、source22c40bdb9871629d5d0aa2757f275a886e2b65f8、21:39:46～21:44:10 JST、exit0。全678件（Protocol80/Storage34/API394/Web129/CHR41）、新4件を含むWeb53件PASS。全5対象module line/method/class/branch各100%、NullAway/Enforcer/format PASS、SpotBugs0、新BUGなし。002/manifest/checksumsで実行環境・Test ID・hashを追跡。最終Security chain/MQ認証/custom Login strategy/Logout revoke・queue/本番redacting監査403 handler/全画面/起動とlogger固定/実NK CHRは未完了。特にCsrfFilter loggerをWARN以上へ固定、secret-bearing拒否例外のmessage/causeを表示しないこと、null-saveをLogout coordination後だけ使うことを継続gateとする。PT callbackは固定403とcall countだけの代替であり、実監査完了を偽らない。IT/ST完了ではない。
