# NK-DAT-001 検査AEScredential単体テスト仕様書

InspectorAesCredential.consume/version/copyKey/close/toString、RD DAT-009/OPS-009、UI212/241/251、SS343 §6.1/324 §12/352、QA-046/UIC-006/SSC-049、PG-D-131。Inputは実行時CSPRNG32byteと独立JDK Base64で手組み、production消去前のliteralコピーを期待値とする。実credential/固定秘密値をGit/証跡へ置かない。正常・境界・null・不正・例外・alias・並行/再closeを以下で確認する。

| Test ID | Method・入力/操作 | 独立期待値 |
|---|---|---|
| PT-DB-INBOX-105 | validKeyAndVersionBounds: 1/16長version・random32byte | 元array全0、copyKeyは独立元値、version一致、再copy不変 |
| PT-DB-INBOX-106 | envelopeLengthAndMagic: 空/不足/過長/magic/BOM/CRLF/末尾byte | 固定IllegalArgumentException、入力全0、cause/suppressed/値非保持 |
| PT-DB-INBOX-107 | versionAndLineBoundaries: empty/17byte/先頭記号/非ASCII/control/改行不正 | 同固定失敗・全入力消去、1～16合法文字境界のみ許可 |
| PT-DB-INBOX-108 | base64AndKeySize: 非base64/内側padding/未padding/31・33byte/noncanonical末尾bit | 不正拒否・全入力/temporary消去経路、32byte canonicalだけ成功 |
| PT-DB-INBOX-109 | consumedInputAndCopiedKeysDoNotAlias: 入力/返却copyを変更 | 内部key・後続copy不変、consumeは元bufferを必ず消去、callerがcopyも消去 |
| PT-DB-INBOX-110 | closeIsIdempotentAndRedacted: 2回close/close後copy/version/表示 | copyは固定IllegalStateException、versionは非秘密metadataとして可、鍵値非表示 |
| PT-DB-INBOX-111 | concurrentCopiesAndCloseStayConsistent: 100独立consume/copyとclose競合 | 各値は対応元32byteか閉鎖例外のみ、部分zero/混線不可、全future回収。public monitor保持でprivate lockを阻害しない |
| PT-DB-INBOX-112 | nullAndInvalidInputsNeverEscape: null/bad sample群・例外表示 | null契約拒否、bad入力値/encoded値を例外/cause/toStringへ出さず、NPEを正常catchしない |

実IO/ACL/credential provisioning/親mainは本仕様の合格範囲外。Systemdのroot+named ACLを未実装のmode0400判断で代替しない。

探索・正式command/source/branch/日時/OS/JDK/tool/exit/全4種coverage/BUG・SSC/Test ID/期待・実際/証跡hashは030/evidence/inbox-aes-credential/manifestで実行後確定する。Full clean verify・8collector/21scope、旧V001～013/Current baseline不変、秘密scan/trace負canaryを要求し、failed/flaky/skipped/not-runを成功へ算入しない。実NK CHR/IT/STは未完了。
