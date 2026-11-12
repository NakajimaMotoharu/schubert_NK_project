# P00805 immutable snapshot原6件＋現Protocol130 通常PT仕様

対象ScenarioDetailSnapshot constructor/records/metadata/toString、FUN004/005/UI234/SS3324.2・333、原TestID SNAPSHOTMAX001～003/PT-SCN-SHAPE001～003。独立期待値: 0/1/10000/10001件、全entry連番、201/5000/9999位置のgap、末尾4097byte拒否、null metadata/list/element拒否、FILE shape拒否、caller変更後も保持した先頭row-1/末尾row-10000と不変List、toString件数だけ。期待値は手書き整数・文字列・例外型・objectidentityで指定しproduction methodから生成しない。

Whole standalone二fixture6はsource全文確認済み、DB/file/JMS/key/actual4/native/Root/threads副作用なし。Protocol130は原whole27fixtureを現byteと結合し、二つのdirect dependency DisplayPath/RelativePathが旧snapshot6 source65dから変わったため必要な再資格として同runで実行する。原6の成功だけの確認再演ではない。旧exec/coverageを合成せず、全178physical（Protocol176＋Snapshot/package-info2）保持で全実行class CRCとclass initialization/Code/synthetic/noCodeを分ける。

prepare: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1376_snapshot_current_qualifier.py prepare`、Testcompile0。1377 PMD/Checkstyle/format全0、1378 preflight0: ownMain2はnormal compiler/NullAway/SpotBugs/style原証跡と現在source/physical同一を限定reuse、未変更Mainのbuildを反復しない。Test2は現Protocolでfreshcompile。source固定push後: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1376_snapshot_current_qualifier.py run <fixed-source>`。独立postはXML/FES/abort/exit/全scope source/static/session/CRC/四counterを照合し、不足があれば未合格として保存する。実行結果・実source・環境・hashは後続独立manifestへ一意join、開始前現時点NOT_RUN。

別範囲: BUG2680のRegenerator fatal一行PGは1379 format/Checkstyle0・source差一行だけ。actualTemporary/Codec runtime・compile HOLD、当136にこのPGのPT/coverageは含めない。BUG2679/2680/YKT2359七target未閉鎖、原P00805/2・全451・終了依存・元190/正式1964PT53scopeは未更新。原費に加え SOURCE_REQUALIFICATION .1/.25/.5、PG限定 .05/.15/.3を事前内訳化、群cap2、共有実費配賦null。


実行追記: source a27bf16e22698294a5900b13f06a09d1d213d830、26878真正0/136FESabort0、[26882独立結果](../018_NK-OPS-001/evidence/PG26882-snapshot-current-independent-v1/manifest.json) hash8780b454913911e0736b30ae9f8b004c4be59376be7dafe954b684db058aa704。全178physical/CI170/code160/positive164CRC、L3499/M744/C160/B1026未網羅0、手動除外/旧execunion0。環境・command・exit・二scope分離・BUG/現在sourceは[26884](../018_NK-OPS-001/evidence/PG26884-snapshot136-regenerator1-scope-join-v1/manifest.json)。未実行の開始時記録は履歴として維持、元190/全451未受入。
