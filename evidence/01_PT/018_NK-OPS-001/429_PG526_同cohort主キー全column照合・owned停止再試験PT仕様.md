# PG526 同cohort主キー全column照合・owned停止（BUG823/YKT592）

Productiona2/PG495/schema028、SS341343353/SSC190198213、QA047、PG524/427の同live4世代と原本/Backup/startupISSUED7を使用。旧工具はPG525回収actual0、旧PG524 actual143/UNKNOWNを保持。別TOOLS/SAVE/予約をnew-onlyで固定し、旧sourceの成功流用なし。

| Test ID | 期待値と独立根拠 | command |
|---|---|---|
| PG526-H01 | batch462行をpositive integer唯一idでjoin。順序違いは同値、欠落/重複/列/値/null/bool/int/float/string/nestedの差は拒否、raw列を変更0。103assert | pg526_batch_join_test.py |
| PG526-H02 | literal旧452行全column保持+新10件承認SKIP、attempt=max+1・元run/date・全counter0・エラーliteral、真正PID1四record/同Job26968/DONE時刻と元1800s。80assert | pg526_completed_oracle_test.py |
| PG526-H03 | 同cohort全generation/宣言とprimary終了履歴を分離、全raw保持・Cleanup後だけ暗黙Broker終端許容・一回順序/全receipt。49assert、固定live actor/TERM/vendor285assert | pg526_reference_protocol_test.py / pg526_native_owned_stop_test.py |
| PG526-H04 | Java引数null/欠落/未知値negative、ownership0/NPE0、JDK25.0.4 javac全警告error | Pg526NativeArgumentTest / pg526_native_compile_v1.sh |
| PG526-V01 | 新M-A/RODB/advisory/十Ref/FD→当親真正DONE・原本SUCCESS/startintent0/保存462PK全列→Caddy/Web/API/Cleanup/Inspector/Expiry/Backup/Brokerの所定逆順一回owned停止→全正常scope・全kernel終端/同Unit資源後条件、全24DB/原本/Backup/startup不変 | pg526_native_stop_v1.py |

期待値はProduction methodから生成せず、SSとliteralfixture/PG523同source実原値に束縛。PG524原raw/hash/SQL並び順は保持、画面/電文等の外部順序は変更0。関連横展開=PG523batch-onlyとPG524all24の跨artifact境界、full24同SQLのPG519～522/PG525、将来停止/coverage採取。検索だけ完了にせず、全対象の是正又は非該当と追加testをYKT592に記録する。

実行: `bash tools/quality/vm/050_s1/pg526_native_compile_v1.sh`（new-only）後 `python3 -B tools/quality/vm/050_s1/pg526_native_stop_v1.py` 一回。host専用oracleはguest再実行0、immutable6payloadでcompiled sourceを結合。全ログ/DB/電文/rawはprivate、Gitは終了/集計/hashのみ。実結果未実行を合格へ算入0、native coverage/正式runは別照合が必要。
