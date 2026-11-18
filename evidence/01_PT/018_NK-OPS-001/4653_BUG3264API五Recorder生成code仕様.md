# BUG-3264 API五Recorderの全生code測定

WBS-F03/2-2（第58版実行順82）、WBS-P018-09、RD171/UI252/SS351/354、現Core bcc9e0673287c51950ecab9b36350abfcd4b2c69。PG39264に生未到達の生成6methodがあるため、元Recorder4×8にDbPoolMetricRecorderTestの8とGeneratedMetricValueContractTestの8を加え、一つのXML/JaCoCo execで計測する。元Recorder32は同一sourceに必要な閉包再計測として記録し、固有加算0。元仕様1623/1635/1643/1647/1650/1660/3017/4651を対象とする。

POOLMET004はDEBTf／STANDAQcが対応正modeと同hashの別文字列である独立値（PG39230）に対し、固定CONFIG_INVALIDと登録0を確認する。標準・debug・空・null・未知値・並行の元期待は保持。GENMET003/004のCounts(3,5,2) hash3040と固定text、等価・非等価・異型・nullを独立照合。GENMET005〜008は四enumの固定順、valueOfの正常・未知・null、values配列防御を明示試験する。GENMET001/002ではPoolのCounts(3,5,2,8) hash94248、固定text、成分とnullも保つ。群開始予算0.45/1.75/3.7pp、上限5pp、元行加算0。

JDK25.0.4／Maven3.9.12／JaCoCo0.8.15／Micrometer1.17.1、Linux amd64、dev-foundation。元六Testは新規DB/Hikari/JMS/OS起動の依存なし。closed-host toolのdata-only Registryで、proofの元source/全物理/独立期待・実終了・failures/errors/skips/not-run・固定CRCを照合する。生の自然な分岐0と実未到達を区分して保存し、別execと合成しない。
