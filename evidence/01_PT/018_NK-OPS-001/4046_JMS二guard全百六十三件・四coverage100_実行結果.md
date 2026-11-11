# JMS二guard・同source接続163件の実行結果

対象commit／Production Main `236ffddc83a08f1ba8f2ac5c3932e381371acd59`、branch dev-foundation。仕様[4045](4045_JMS二guard_provider故障分類_単体テスト仕様書.md)。コード修正・原14保持・新2製造は同commitへ保存しpush済み。

PG26506-JMS-PROVIDER-CONNECTED163は真正終了0、163件成功、failed/error/skipped/abortedは0。独立PG26508 manifest SHA256 `fea8455692f6796f75f5db1617539b4d9f011e35405ae5b5d9adeacf03c206f0`。新定義2はprovider128入力・早期検査4入力を完走。JUnit数と入力観測数を混同しない。元161件は変更guardが使用する同閉包の必要再資格で、新規定義・元190正式受入へ加算しない。

| counter | covered | missed |
|---|---:|---:|
| line | 3777 | 0 |
| method | 801 | 0 |
| class | 168 | 0 |
| branch | 1142 | 0 |
| instruction | 18664 | 0 |

全188physical入力を保持、172positive MainのCRCは当byteと一致。自然Code不在16、JaCoCo標準switchmap4は異なる区分として全分母へ残す。手動除外・旧exec合算なし。独立postの初回classinfo零命令とCode不在の混同はBUG2663/YKT2343へ修正前起票・PG26512保全後、postだけを是正し元PTを再実行していない。

Java25.0.4・ErrorProne2.50.0・NullAway0.14.1のfresh限定Main compile0、全12ClassStatsのSpotBugs0/missing0/error0。新TestのPMD raw12は全件個別文脈非該当（standalone Proxyのinterface loader／fixture専有null対応map／Proxy equals identity）、未分類・適用違反・Checkstyle・解析error0。抑制設定を追加していない。旧命名違反・初期参照/計数不備とred2も原hashで保全する。

実command・日時・環境・入力/期待/実際・XML原hash・coverage・source/runの結合は[PG26508 manifest](evidence/PG26508-jms-provider-independent-v1/manifest.json)。実行commandは1250 qualifierの`run 236ffddc83a08f1ba8f2ac5c3932e381371acd59`、その内部JUnit終了0とJaCoCo出力の真正終端を独立照合した。仕様の独立期待値はSSのliteral offset・元例外instance・固定診断で、productionをexpected生成に用いていない。

BUG2659/YKT2339は二guardの限定scopeをCLOSED。BUG2660/2661/2662/2663は各保存済み工具/fixture是正scopeをCLOSED。原実broker・transaction結果・VM/native・DB・原本/Backup/鍵・Root・held四classへの操作なし。P00502/P00503全owner／C04／F02/F03／全451／実NK CHRは未受入、正式1964PT/53scopeを更新しない。IT/STは未実施、工数率null。
