# 5668 F02 Listenerの直接JDBC・file境界の単体仕様

WBS-F02-b、SS311 §3／§10、SYS-005。BUG-3488／YKT-2781。監査対象は入口からの直接SQL型、ファイル操作、Storage物理依存。Listenerの名前を持つAPI inbound型、JMS Message引数を持つ入口、内部classを区分する。実Listener・業務処理・実JMS・実DB・実ファイル操作は起動しない。

| Test ID | 合成入力 | 独立期待 |
|---|---|---|
| PT-F02-LISTENER001 | API inbound ListenerからConnection | FRAMEWORK_FENCES |
| PT-F02-LISTENER002 | API inbound ListenerからFiles | FRAMEWORK_FENCES |
| PT-F02-LISTENER003 | API inbound Listenerの内側classからConnection | FRAMEWORK_FENCES |
| PT-F02-LISTENER004 | Web JMSContext／Message入口からConnection | FRAMEWORK_FENCES |
| PT-F02-LISTENER005 | Message入口からPath.resolve | FRAMEWORK_FENCES |
| PT-F02-LISTENER006 | Web JMS入口からStorage所有型 | FRAMEWORK_FENCES |
| PT-F02-LISTENER007 | Listenerから既定JMSContext型 | 許容 |
| PT-F02-LISTENER008 | JDBC adapterからConnection | 許容 |
| PT-F02-LISTENER009 | file adapterからFiles | 許容 |
| PT-F02-LISTENER010 | 非JMS onMessage(String)とConnection | 許容 |

JDK25の自作合成classだけを静的importする。既Controller／Protocolの53判定を修正後に同入力で確認する。実製品六包装の受入、実ファイル後条件、業務transactionの実証は別途。
