# BUG-3267 API MQ圧力・再配送の固定mode

WBS-F03/2-2、WBS-P018-09、RD171 MON005–013、UI252、SS351/354。Core bcc9e0673287c51950ecab9b36350abfcd4b2c69。元1693/1695のMqPressureMetricRecorderTest、MqRedeliveryMetricRecorderTest各8件。一切の元Normal・数値境界・null・別owner・有限並行fixtureを維持。元mode不正それぞれにDEBTf／STANDAQcの二件を追加する。独立の31進演算はPG39230を参照。二入力は固定許可modeと同hashでも別値で、IllegalArgumentExceptionの固定CONFIG_INVALIDと監視登録0が期待値。

自有SimpleMeterRegistryとBrokerTopologyのenumだけ。実Artemis・JMS・network・DB・保護型はなし。元2×8を一固定commitの一回で実行し、同一execの独立XML・CRC・Main全物理と生constructor、静的を照合。共有Protocol部分の未到達と自然B0は保持。JDK25.0.4、Maven3.9.12、Micrometer1.17.1、Linux amd64、dev-foundation、群上限4.5pp、元行追加0。PG39328は製品全451と独立。
