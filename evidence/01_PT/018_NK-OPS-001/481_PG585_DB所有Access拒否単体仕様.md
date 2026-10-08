# PG585 非native Accessの公開拒否・null契約

Program NK-BAT-001/MorningDatabaseSession.Access、主担当P017-01.02、関連RD OPS009/DAT009/UI251/SS341343/SSC129133200。対象同null/引数/閉鎖capability仕様は不変更、Productionソース969のmain classbyteを保持し試験だけ追加。実VM正常起動・旧hostselected試験は別scope、当host試験を実native認証代替にしない。

PT-OPS-MACCESS585001: 独立固定run/cutoff/Backup claimのvalid objectからnon-native Accessへ照会・resume・complete・failureを呼ぶ。期待=literal IOException「root batch database unavailable」、cause/suppressed無し、能力のないdataでDB実行/許可発行無し。002: valid owner guard/currentclaims/child/original lookupを渡しinspect/observe/begin/handoffを試みる。期待=同拒否、owner/child/lookup/abstract DB callback全0。003: original request/recheck再入を拒否、同じdataの再送は権限を発生させない。004: APIの明示nonnull契約はconstructor/boundaryでNullPointerExceptionによりfail-fast（正常扱い/catchなし）、owner callback無し・ネイティブ資源取得前。意図的プログラミング契約違反のnegativeと正常入力でのNPE排除は区別する。

対象追加4PT、独立assertionはexception literal/identity/callback0、不明値からexpected生成無し。正常ownerの実DB/lock/原本不変は既MorningDatabaseSessionTestを同batch回帰内で合わせて実行し、unsupported判定を実ownerの不正拒否へ拡大しない。コマンド bash tools/quality/vm/050_s1/pg585_access_pt_v1.sh <固定40桁HEAD>、JDK25.0.4/Maven3.9.12/PG18 fixture/NullAway-Werror/Spotbugs4.10.4/JaCoCo0.8.15、全batch scopeを一回実行。source-files hash/exit/開始終了/全XML/FES/四counter/classbyte/静的をPG379/pg585-access-selected-v1へ封印する。

着手前P017-01.02仮枠0.67/1.67/3.67pp、群PG585-ACCESS-OWNER-DENIAL/event0080、共通K01全体回帰/実VM N費を含めない。未実行を加点0/正式認定不変更、当分岐網羅前後と依存残件は実結果へ追記する。
