# BUG-009 reproduction（sanitized）

- 発見日時: 2026-09-05 06:33～06:34 JST
- Branch / 基点commit: `dev-messaging` / `6ce14d8`
- 対象: 未commit Outbox production/test追加後の`OutboxJmsSender.send`
- Command: Java 25、offline Maven local repositoryを用いたProtocol/API reactor `clean verify`
- PT: Protocol 69/69、API 88/88 PASS。failure/error/skipped 0
- Coverage: Protocol/APIともclass/branch/line/method 100%
- Static analysis: API SpotBugs bug 1、error 0
- Bug pattern: `THROWS_METHOD_THROWS_RUNTIMEEXCEPTION`、`OutboxJmsSender.java`の非duplicate commit failure再throw
- Expected: provider固有runtime failureを型付き・redactedな送信失敗へ正規化し、dispatcherがERROR/retryへ遷移できること
- Actual: `JMSRuntimeException`をそのまま再throwし、SpotBugs gateがbuildをFAILした
- Secret handling: exception本文、wire body、credential、operation token、session/token/key実体は本証跡へ保存していない

本runはBUG再現用の非合格runであり、PT-IDEM-010/011またはProgram PASSへ算入しない。
