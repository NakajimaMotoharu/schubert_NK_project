# YKT2152 Web応答・外側owner静的横展開

4162、原.5/2/5pp cap6、主費用P00503。対象は現56720のArtemisReplyConsumers/WebNativeRuntime/ApiLogPathApplicationRuntime、直接のadmission/phase helperを静的に点検した。source/fixture/native/VM/broker/DB/key/四heldの生成・実行0。共通原因は「複数の独立したAPI business consumerを持つ親が、最初のblocking close前に他子の新business admissionを止めない」ことで、単語close/stopだけで全経路へ同じ変更を適用しない。

| 対象 | 静的事実・因果 | 判定と未実測 |
|---|---|---|
| ArtemisReplyConsumers | 所有JMSContextは1つ、closeの最初のblocking resource操作は自身context.close。複数の別context/groupを残したまま先行子のcloseを待つloopはない。stoppingでready/startを拒否し、haltedはfatal delivery停止用 | API親の兄弟fanout欠落とは非該当。providerの停止時callback配送/queued reply/close完了は未実測のままで、正常close時のhalted値からprovider保証や全PT成功を推定しない |
| WebNativeRuntime | closeはadmission.refuse→admission.drain→HTTP close→retry join→log replay join→replies close→management/metric/assets/transfer/codecs/broker。SS314§10はHTTP drain→retry worker join→replies→外側資源の順を明示 | Webのbusiness新規受入gateはHTTP admissionにあり先にrefuseする。既HTTP/Logout再試行が応答を待つ間はrepliesが必要なので、親停止開始時のAPI型一括callback停止へ置換しない。実drain・worker終端・外側資源は未実測 |
| ApiLogPathApplicationRuntime | closeは単一のmessaging.closeへ委譲し、独自の先行blocking resourceや兄弟group loopを持たない。startはApiMessagingRuntimeのlegacy4+1経路 | 修正済み親のfanoutをそのまま受ける関連caller、独自修正不要。新PT-GROUP002/006のlegacy/partial実測は未実行HOLD。initial Login/Game/Log pathであり全31layout readinessの受入へ広げない |

支持sourceも点検した。WebHttpAdmissionは同lock下でrefuse後のacquireを拒否し、activeが0になるまで所定残budgetでdrainする。WebHttpAdmissionValveはServlet finallyでleaseを解放せず、Tomcat terminal AccessLogの同一Lease.completeをCASで一度だけ完了する。ASYNC/media/REQUEST persistenceを含む実測の代替ではない。WebRuntimeStopは当phaseが正常帰還した後だけconfirmedを進め、IOException/Lifecycle/Runtimeで後続phaseへ進まない。これらのconstructor・native portは呼ばない。

既期待の限定参照: WebRuntimeStopTest.stop001..005の全bodyは30s→28sの残budget/phase順/反復close/UNKNOWN時後続保持・元deadline/0境界・fatal同一性を規定する。ArtemisReplyConsumersTest.closeIsIdempotentAndPreservesStartupAndCloseFailuresのbodyはready false/未確認close再試行2回・startup cleanupの原cause/suppressedを確認する設計。これらを今回再実行せず、同Test classの他bodyをレビュー済みにしない。新6fanout Testをこれら既期待でPASSにしない。

別原因の追加発見としてWebRuntimeStopのphase後absolute deadline比較がsigned原点の折返しで誤判定する静的vectorを得た。BUG2409/YKT2154へ修正前起票し、YKT2152の兄弟停止欠落と分けた。現在VM/旧失敗の原因や動的再現済みとは扱わない。次の独立PT可否は当Test/calleeの実際の副作用から判定する。

YKT2152は原API4修正＋新interfaceに対する005026の6動的Testが未実行のためOPEN。今回のWeb非該当/委譲根拠で全横展開完了・BUG2407再試験完了・実runtime/CHR/native/451合格としない。新製造/新Test/PASS/coverage/source四counter資格/leaf受入0、正式1964/53・工数率nullを保持する。
