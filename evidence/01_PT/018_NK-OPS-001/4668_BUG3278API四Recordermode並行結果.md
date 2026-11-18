# BUG-3278 API四監視Recorderのmode・並行結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `56c16517777ee2af66d27e11a809a4165cdd6bfc`。PG39410はMQ Message 8、MQ Processing Duration 9、Inbox Replay 8、DB Query Duration 9の全34初回成功。失敗・error・skip・未実行0。各同hash異値2件でCONFIG_INVALID、登録0。MQEVENT007の元64、5秒Future、期待count map、別registryを維持し、終了後解放へ揃えた。Main差0。

PG39414独立は物理24/正CRC18。PG39418で四constructorの生分岐は順に14、16、16、18の全到達、本体4型は各生四counter全到達。生成enumまたは支援の105箇所は当execの実未到達。静的適用0、PMD生26は有限worker、serial期待map、元private monitorを個別照合。F03/451・実環境へ拡張しない。

固定mode横展開の現Main 20型中18型で局所反例を測定。API Outbox observationの二型は実型閉包にQA056のTemporaryInfrastructureExceptionを持つので、既の任意抽出や実行を行わない。YKT2691全体はOPEN。

Linux amd64、JDK25.0.4／Maven3.9.12／Micrometer1.17.1、dev-foundation。[独立証跡](evidence/PG39418-f03-four-api-recorder-mode-independent-v1/manifest.json) SHA-256 `d171dab4bc27902c99b6e57b264057fbfedf40bef708f3b4fbc653a137b82b21`。実command、XML、終端、CRC、静的、生counterを参照。
