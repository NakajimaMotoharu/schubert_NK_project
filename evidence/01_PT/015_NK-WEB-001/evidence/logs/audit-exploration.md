# Web SECURITY local JSON audit探索

2026-09-09 JST/dev-web。PG-D-107/PT095～100は8646931で実装前仕様化。BUG068/YKT060は4bdc477でroute不足を修正前起票し、e70bbddで同じ必須contextのtargetType不足を修正前追加。UI226/252、SS314/351 §2～4/352 §12。421既存Java25.0.4/Maven3.9.12/Gson2.14.0、追加dependency/toolなし。

| /tmp log | 終了JST | 結果 | SHA256 |
|---|---|---|---|
| PT-WEB-audit-20260909-explore-01.log | 00:17:42 | Web6件PASS、audit/Event/Route全coverage100%・静的解析0。ただしtargetType追加前なので最終適合の代用にしない | 864e9bc47844ee0ebc05519ff32a85eed0ae0aeee2a5cbedbf90625390f54a3d |
| PT-WEB-audit-20260909-explore-02.log | 00:19:07 | targetTypeも含むWeb6件PASS、新3class line/method/class/branch100%、NullAway/format/SpotBugs0。API横展開の追加assertionは次の全体回帰で実行 | 544e3d60c0ec4230f08fddb9b41c41f3f1db8a25ed7702f47dcf4b7e1650a015 |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=WebSecurityAuditTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

## 独立期待とredaction

固定ClockのJST zoneを無視してUTC millis `2026-09-09T00:00:00.123Z`、SS351の共通key・catalog6eventのaction/reason/outcome/levelをtest側の固定tableで照合。全eventにRoute enumの既知handler/filter patternと固定targetType=HTTP_REQUESTを付与する。Loginは/loginのみ、raw URL/queryを受け取る入口なし。任意details、Throwable、HTTP request、passwordを入力にしない。JDK25 System.Logger公開SPIの収集doubleは文字列overloadのbundle/params nullを検査し、Throwable overload呼出を失敗にする。Productionは標準logger.log(level,json)を呼び、配備backend設定は後続。

成功actorはSessionPrincipalからusername/roleのみ瞬間的に投影し保持しない。失敗/lockの利用者入力usernameは受け取らない。NFC/64byte/line separator/JSON escapeを固定文字列で検証し、合成contextとloginAt等が出力へ入らない。canonical numeric IP/IPv6/IPv4mapped、scope/hostname/空/長さ異常、version1/64/65/ASCII禁止文字、全null/metadata相互不整合を非出力で確認。lockだけ0～900、他eventは0のみ。

Clock null/faultとlogger faultを正常監査に見せない。各callの新JSON、actor/IPなしへの切替、100並行request/actor/IP/level/待機秒と公開monitor非依存を検証。収集double以外のJVM raw log、credential、raw session/cookie/tokenは格納しない。

## BUG068/YKT060全対象

| 対象 | 修正または非該当根拠 | 再発防止test |
|---|---|---|
| WebSecurityAudit全6event | routeを全event必須の閉enumへ、Login path整合とtargetType固定を追加。未実装部分ではなく新実装の必須監査context漏れとして起票 | PT095の全JSON key/value、096のnull/不一致、099/100の経路・event混入防止 |
| API LogQueryAuditWriter | 元から検証済LGSREQ01/layoutとLOG targetTypeあり。自由検索値なし、非該当 | PT-ADM-068/069等のDB JSON key/value/secret canary、全回帰 |
| API UserQueryAuditWriter | 元から検証済layoutとUSER targetTypeあり、非該当 | PT-ADM-049の既存key集合にUSRREQ01/USER固定値assertion追加 |
| API UserRequestAuditWriter | 元から検証済layout/operation/USER typeあり、非該当 | PT-ADM-034の全認証/role拒否へUSTREQ01/USER固定DB後条件追加、039等の既存監査検査 |
| 未実装owner拒否処理 | 実装済生成点なし。検索だけを実装済合格へ算入しない | 後続QST/NTF/QRYのProgram PTで必須contextを検査 |

検索条件: Web/APIのAUTHORIZATION_DENIED/OWNER_SCOPE_DENIED生成点、detailsのlayout/route/targetType。API側source・期待値を変更せず追加assertionで正規値を確認する。

## 正式gate

root clean verifyと全7collectorで確定予定。Web SECURITY local encoder/公開logger呼出の部品PTであり、HTTP handler/request ID/Caddy/実backend/logger WARN固定やAPI DB監査への到達、実NK CHR、IT/STの完了ではない。
