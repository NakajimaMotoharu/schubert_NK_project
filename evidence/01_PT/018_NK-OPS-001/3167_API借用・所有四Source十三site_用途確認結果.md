# API借用・所有 四Source十三site 用途確認結果

2026-10-31/3166/PG-D1017/WBS-F03、開始0.5/2/5共有ppを維持。原Main全1011行読取後、`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg16356_api_borrowed_owned_thirteen_purpose.py` はchunk e47647/entry88fac75d・lint0/body0、公開manifest **e02c92bbc82d40711832235ad83f4d7377bbdfd1c27f31b549d863cf51ff9165**。独立16358（同checked entry方式）はchunk2b64de/entrya658ab3d・lint0/body0、manifest **7265189bdb7a8a1b473421affbd7f33b633f38e49bb4e51d2b82dac887e7b900**。両runは `evidence/provisional/PG16356-api-borrowed-owned-thirteen-purpose-v1/` と `PG16358-api-borrowed-owned-thirteen-post-v1/`、元command/実行時刻/tool SHAは各invocationへ保持。

Command取消/削除2、Sync5、Log4、Query2=13warning/9catchを原13253 manifest/findings/XML、全Source SHA・全attrs/診断・halfopen UTF8 byteへ結合。文字列Source control十二反例、独立metadata26＋byte四反例を確認。Commandは後方362行escape前の196/280行までだけ既UTF8 adapterを適用し、独立側は原XMLと実UTF8行prefixから座標を再構成、対象prefixのescape/CR/NUL無しを確認。全Java escape翻訳/AST・CFG証明とはしない。QuestionSubmission/Workerは今回非選択で、旧非適用の解除なし。

借用Command/Queryは接続のcommit/rollback/closeを新たに所有せず、Statement/ResultSet終了後に既fatal分類と固定catalogへ移る。Queryの確定業務拒否はsuppressedが無い場合のみ保持。Sync/Logは所有transactionで失敗時rollback一回とTWR closeを経るが、Graph helperの有限帰還/同一Error保持・実rollback/close成功は今回未実証。LogはSQLだけを固定DB例外へ変換しRuntime/Errorは別伝播、Syncはprotocol/uncertain commit/closeの固定扱いを区別する。両方でJMS送信/ACKを新たに行わない直接Source方針を保持。

参照1171＋限定用途208=1379/1491、残112（RootFailedStartRecovery十HOLD含む）。manualPurposeは既理由との初回性不明null、警告抑制0/actualViolationCount null/PT免除false。今回Product/Test実行/Source修正/新BUG/拒否/正式受入0。2174/296・四262/383・正式1964/53・歴史17/190・工数null・QA051final/G07/G13/451/全HOLD不変更。新sourceへ旧成功転用/保留whole抽出/外部VM・DB・Root・鍵・権限操作なし。

fresh20:39 JST共有used58/rem42/reset1793774153/短期null/券0。共有丸め差0は専有費0ではなくN/T/actual費null。usage20:36:50 cursor3c92ac8b3066b8b4263591dd4855cdbf48c1a39e23d7090152702e0056286116、NO_NEW_EXPLICIT_USAGE_RECORD、欠測補填なし。保存後も許可済み残generic/独立通常PTへ継続し、小群/commitで全体停止しない。
