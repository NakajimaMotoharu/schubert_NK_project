# BUG-3278 API MQ・Inbox・DB Query監視の設定と並行

WBS-F03/2-2、WBS-P018-09、SS351/354、UI252。Core bcc9e0673287c51950ecab9b36350abfcd4b2c69。元MqMessage八、MqProcessingDuration九、InboxReplay八、DbQueryDuration九、計34。各既mode負例へ正modeとhashが一致する別値DEBTf/STANDAQcを追加（PG39230の独立固定計算）。固定CONFIG_INVALID、registry登録0、正mode・null・空・unknown・数値境界の元判定を保持する。

MQEVENT007は64件、8worker、5秒invokeAll & Future.get、期待count map、別registry値を維持し、明示shutdownNowと10秒awaitで真正終了後にregistryを解放する。ほか三fixtureの既有限停止は変更しない。JDK25.0.4、Maven3.9.12、Micrometer1.17.1、Linux amd64 dev-foundation。Protocol固定値・ローカルregistryのみで実JMS、DB、HTTP、保護型なし。既Main/物理閉包、同一一回のXML/CRCと生counter・類縁support未到達をPG39418へ保全。0.55/2.1/4.4pp、cap6、元行価格追加0。
