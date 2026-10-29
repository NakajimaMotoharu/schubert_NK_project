# 2625 現四PT実行環境 補完manifest仕様

2026-10-30 JST、BUG2096/YKT1843修正前起票、source6b53/原14242・52・56・70と各postを保持。開始0.25/1/2pp cap10、元費/元Test/元manifestの変更/再実行0。期待は利用者指定のmanifest環境再現契約、既Reporterの固定四prefix runtime.version/os.name/os.arch/os.versionを実測情報とする。

新14276は固定した四親の公開manifest hash/source/真正exit0・元own test log hashを照合し、各own slotのselected-junit.log先頭最大32行/4096byteだけから四prefixを一意抽出する。未知行は保存/公開せず、許可scalarのみ・四fieldの重複欠落/制御文字/長大値を拒否、実JDKは25.0.4の元報告を必要とする。公開envelopeへ親path/hash/run/source/branch（元qualification HEADのGit branchは当時資料参照）/実行期間/command hash・元command参照/exit/JDK・OS/SDK versionと実hashを保存。古い25/400等のprivate log、実application/VM/DB/鍵/credential/他processへはアクセスしない。

独立14278は同じ元四parentと許可prefix・reported version/OS・rawhash/source/run/期間/exit・既SDK path/hashを別に確認しmetadata反例を拒否する。工具自己検証だけで元PT/PASS/coverageを再加算しない。元manifestは不変のまま新manifestへの参照を2626/各結果/456へ追記し、今後の同runner原scopeも必要時に新envelopeで結ぶ。原実行環境を現在のunameやfresh java -versionで代替しない。

状態/実command/終了/hashは2626へ保存、全formal/個別受入/工数null/全品質/HOLD/原本保全・二held工具metadata前除外維持。旧履歴の全件環境保証をしない。新Source/JVM/Test/fixture/DB/VM/Root/cohort/permit/配備/回収操作は0、拒否再試行ではない。
