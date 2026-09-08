# Session属性探索・障害再現記録

2026-09-08 JST、dev-web、BUG-055/YKT-050/SSC-038/PG-D-094。JDK25.0.4/Maven3.9.12/Gson2.14.0、OS等は正式manifestの環境参照。合成JSONだけで実施し、入力値・例外raw診断・JVM propertiesをこの証跡へ転記しない。

## 実行と再現

- 修正前起票commit3c45325。探索02は19:25:56終了、exit1。新7件中PT-WEB-014だけFAIL。期待SessionAttributeExceptionに対しDateTimeParseExceptionが外へ出た。raw log `/tmp/PT-WEB-attributes-explore-02.log` SHA256 `8e2a96789cb1221d3ffd293792a7b270088330b1ba03f51846c3e1728aba53aa`。rawはローカルのみ保持し、Gitへ入れない。
- 明示DateTimeException捕捉へ修正。探索03は19:31:10終了、exit1、test未実行。root POMにない短縮goal `jacoco:report` をofflineで解決できなかったコマンド問題。製品障害ではなく、正式指定goalへ訂正。SHA256 `f0aca6a6db5607d3afc2dacf0661e6591ba4f8f61cd77e2b541a2bdac6a78ae7`。not-runを合格へ算入しない。
- 探索04は19:31:49終了、exit0、新7件すべてPASS（failed/error/skipped0）。`/tmp/PT-WEB-attributes-explore-04.log` SHA256 `b77107c888dea639b3cb0ce40e62138780ef45fd604be0e91110bba4ea756935`。
- tools01は19:32:03終了、exit0、完全修飾JaCoCo0.8.15 report＋dependency3.9.0 tree。新5classのline/method/class/branch missed0、Gson2.14.0 compile。SHA256 `3f20d83c66d4c2f4cb8bac86e7bc076b5d963d7a563fcbc7764bbaeeaf14fcb0`。探索coverageは累積なので最終合否はclean verifyだけで確定する。

再現command（repository root、各run別log、JAVA_HOMEは421参照）:

```sh
./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=SessionAttributeCodecTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test
./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am org.jacoco:jacoco-maven-plugin:0.8.15:report org.apache.maven.plugins:maven-dependency-plugin:3.9.0:tree -Dincludes=com.google.code.gson:gson
```

## YKT-050全対象確認

検索は`rg -n 'Instant.parse|DateTimeException|LocalDateTime.parse' src/*/src/main/java --glob '*.java'`。外部JSONのInstant.parseはSessionAttributeCodecのloginAt/issuedAt共通helperのみで両方を修正・PT-WEB-014で不正/非実在日/範囲外/非canonicalを再試験。PT012/014は固定message・causeなし・suppressed0をassertする。

JstWireTimestampは17桁wire専用で任意session JSONを受けず、既にDateTimeExceptionを捕捉。parseのcauseは検証済み17数字の日時診断で、秘密属性JSONの保持経路ではない。FieldCodecは同codecを利用しUTF8/数値を個別変換。LargeResultDescriptorはallowlist pathから8桁日付のみ抽出して明示DateTimeException捕捉、TransferUsageScannerも固定StorageIoExceptionに変換済み。この3対象に新たな変更は不要。既存JstWireTimestamp/FieldCodec/LargeResultDescriptor/transferの負例は正式全reactorで再試験する。定数時刻のInstant.parseを持つtestは外部入力境界でなく修正対象外。

## 正式gate

予定PT-WEB-20260908-02。確定sourcecommit・開始終了・全件数・各coverage・全対象再試験結果は同runのmanifest/checksumsと002へ追記する。暗号/永続化/CSRF/HTTP/実NK Characterization未完了、Program完了とはしない。
