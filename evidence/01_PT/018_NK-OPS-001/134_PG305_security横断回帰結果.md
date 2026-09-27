# PG305 shared security 六module回帰

2026-09-27 23:00:34 JST、source `ac7dac5463725ab63c295faad9bd01d6c8bc66bd`固定、code/test/config/tools変更なし。Protocol80/Storage149/Bootstrap119/API734/Web555/Batch444、計2081PT、failure/error/skip0、全6module静的0。25限定時未実行のreadServiceを含めInspectorCredentialLoader全counter missed0。全suite/XML/coverage/static/log/source inventory hashはprovisional/PG305-regression/manifest.json。

Java25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0。Triggerは共用資格情報reader security変更、D01/04/05・SSC090。全6module `clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check` exit0。collector正式認定・whole coverage checkの代替ではない。

Protocol/Storage/Batch全counter missed0。Bootstrapは既知native入口7line/3method/28instruction未網羅、API/Web各未組立main19line/3method/1branch/60instruction未網羅をそのまま保持。全4指標100%未達で正式gate不合格、除外/到達不能扱いなし。正式run24/1964PT/53scope/48.3%不変更。

回帰中read-only reviewでBUG271/YKT205/SSC091を修正前登録したが、このrunに修正を混入していない。子終端不明のborrowed FD寿命、startPipeline不成立時のfixed Unit隔離、Production privateコピー・親backup/業務起動は未達。Batch Retirementの6768故障位置matrixは実行中CPU進行を確認し、試験を短縮・skipせず完了した。
