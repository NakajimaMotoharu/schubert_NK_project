# API request残静的文脈レビュー仕様

群2506/API_REQUEST_CURRENT_CONTEXT16_V1、原.5/2/5pp cap10、共有使用25残75/reset1793599188。Main/Test変更・新製品PTは行わずsource9b/11040の実17診断と承認SS323324/当原16PT・Main所有契約を個別対応する。2141/2142を継承、全451/正式受入の代用ではない。

PT-REQ-CTX001：CanonicalField六aliasはnewでなくcanonical.fields()からborrow、CanonicalRequest.closeが全fieldを閉じる。check内四つとQuery/Submit各一のTWR owner、close後ゼロ観測二を含む。個別aliasの早期closeで独立fingerprint期待値を壊さない。

PT-REQ-CTX002：Connection二はProxy interface loaderと全call AssertionError handlerのみ、実JDBC接続なし。Main queryの三null guardと原Test三null呼出しを対応する。closeもhandler拒否であり実資源解放としてcloseを加えない。UseProperClassLoader二はJ2EE前提ではなく専用host JUnit/JDK Connection型のProxy生成である。

PT-REQ-CTX003：THREAD五は既8worker64task/TWR executor/Future5/10s/外側240s。公開monitor一はMain private ReentrantLockと独立してcopyQuestionが完了する契約の反証試験であり、synchronizedをReentrantLockへ置換するとそのoracleを削る。Main自体の同期方針免除へ一般化しない。

PT-REQ-CTX004：shared MESSAGE一は未分類のまま、二DB Test static importの無試験renameを行わない。元raw/gate1・全17・元source/行/ID/既JVM成功を保持、局所レビュー16件のみ。新PT/coverage実測/全F03受入0。11054/11056が原診断・source/hash・具体根拠と別経路反例を保存し、各根拠不一致・旧source/PASS/除外/coverage捏造を拒否する。実VM/DB/Root/鍵/保留二工具/Graph9へアクセスしない。
