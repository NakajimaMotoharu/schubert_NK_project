# Revocation版選択冗長条件 PG・PT仕様

2026-10-20、BUG1481/YKT1242、WBS-F03、NK-WEB-002/QA050/SS314/352/451。群1336開始.25/.75/2pp固定（実event番号は機械event正本）。PGはRevocationPayloadCodec.selectKeyの一冗長null比較だけ変更、SS外部仕様/鍵選択/包絡/保存/再送間隔不変更、新QA/SSC不要。

独立論理根拠：receiver versionはnon-null String、String.equals(null)はfalse。current一致は先行returnし、current不一致時のpreviousVersion null/同値/異値はそれぞれfalse/true/false。constructorがpreviousVersionとpreviousKeyの両null又は両非nullを強制し、version一致時のrequireNonNull(previousKey)を保持する。NPEをcatchしない。可到達branchを免除せず、等価な冗長条件だけ除去する。

当sourceで既RevocationPayloadCodecTest七method/RERUN003a～gを通常実行。aは独立JCA/長さprefixで組み立てたNKENC1/AAD全byte/current・previous読戻しと鍵/nonceコピー、bは未知版/旧鍵なし/別鍵/全AAD改変の固定error、cは長さ/境界/ヘッダ/nonce/tag/plaintext異常、dはnull/版名/片側null/鍵長/同version constructor拒否、eはprovider/random故障の固定安全error/消去、fは100並行nonce/close後拒否、gはborrower待ち/close同期/再起動時前世代読戻しを確認する。期待値生成はproduction encrypt/decryptを使わず既独立envelope/fields/明示Reasonを保持。元七TestID不変更、新試験件数加算0。

462/PTPRE008=PT_DEFAULT。固定public合成鍵/context/UUID/Instantとメモリbyte、有限owned threadのみ。eは自己所有の一時test JVM内SunJCE登録を一時removeしfinallyで同positionへrestore、OS設定/実鍵/VM/サービス/権限/アクセス経路を変更しない。外部data/通信/認証/DB/配備/回収0、拒否を探る実行ではない。

新clean source→pg5742の六moduleformat/compile/型null/SpotBugsと全15case/7suite（対象七＋必要reactor八）。全inventory一致/FES-flaky-rerun0/source固定/1664Main/六静的0、RevocationPayloadCodecのline/method/class/branch実miss0を別検査する。旧source七成功や旧nativeを加算しない。次pg5744で全849Mainの差が当一箇所だけ/全1664物理classの差が当一classだけ/元enum48モデル不変を確認し、当sourceのPMD/Checkstyle・当警告消失を独立点検する。

結果は元new-only safe manifest/公開projection・1189後続結果へsource/command/環境/実exit/XML/coverage/hash/BUG/YKTを保存。未測定/global coverage・正式1964/53・QA051final・実所有/未知拒否依存の実操作は別保留。通常小群で停止せず許可済み後続へ継続する。
