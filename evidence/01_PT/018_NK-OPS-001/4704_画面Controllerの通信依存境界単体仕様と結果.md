# Webの画面Controllerと内部通信clientの依存監査

WBS-F02-a、RD SYS-011、UI211、SS311 §5.2。BUG-3394／YKT-2725。fixtureは製品classをロードしない。対象は現工具 `0a3b1c8627` と固定のArchUnit 1.4.2／JDK 25。

| Test ID | 入力 | 独立期待 |
|---|---|---|
| PT-F02-WEB-REPLY-001〜004 | 合成Controllerからclient本人／内側型への呼び出し、field、内側class、配列署名 | 各1辺をCONTROLLER_BOUNDARYとして報告 |
| PT-F02-WEB-REPLY-005〜007 | Controller→facade、facade→client、別型の同名prefix | すべて当規則の報告0 |

元は期待一致3/7。修正後は7/7、既存65/65。修正後112物理を静的取込みし、意図した46指摘だけを確認した。負例を含むため基底auditは終了1、全期待に一致した検証は終了0。実行環境とargvは、PG40624／PG40626のmanifest。独立照合は[PG40628](evidence/PG40628-f02-controller-reply-edge-independent-v1/manifest.json)。現製品Core・全六JAR・実通信・F02正式受入に加算しない。
