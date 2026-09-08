# CSRF value探索記録

2026-09-08 JST、dev-web、PG-D-097/PT-WEB-032～035。先行判断/PT仕様83faded。JDK25.0.4/Maven3.9.12、JDK標準CSPRNG/MessageDigest/HexFormatのみ。新dependencyなし。

PT-WEB-csrf-explore-01は20:13:52終了、exit0、新4件PASS（failed/error/skipped0）、新WebCsrfTokenのline/method/class/branch missed0。raw log `/tmp/PT-WEB-csrf-explore-01.log` SHA256 `57f8945a5978a039b9864e92fcbff1fbe5fe85ada2351b3f4d17f98f6b31ba83`、Gitへ格納しない。秘密値/nonce/token/入力payloadは本証跡へ転記しない。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=WebCsrfTokenTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

独立oracleは0..31の合成byteから手書き64hex、全許可長64～128の同一/先頭・中間・末尾・長さ差異の明示bool。正規token同士は129byte固定長＋length byteでMessageDigest.isEqualを呼び、入力診断/比較値を出さない。生成一時bufferは公開CSPRNG出力を通じzeroを観測、比較一時bufferのfinally消去はsource review。Nullable submittedの欠落/不正はfalse、factory nullはfail-fast。Provider途中故障でも固定message/causeなし/suppressed0。100生成uniqueと共有immutable照合を確認。Timing実測をconstant-timeの数学的証明とはしない。

新BUGなし。正式clean verify予定PT-WEB-20260908-05で累積探索coverageを再確定する。これはvalue部品だけで、HTTP全POST/parameter重複/403/JMS未送信・session保存/rotationとの接続は未完了。
