# Media SQL前入力境界・単体仕様

2026-10-26、NK-MED-001/MediaRepositoryとMediaPreSqlBoundaryTest、原P00901担当費/主P00801と共有22/2run・開始1/3/8 cap10/assessment2044。FUN005/006/007・AUT001/UI223/235§6.1/8.1/9.1/10.1・SS312332333354/451。Main/上位仕様変更0。

PT-MED-PRE001～008はmethod順にaudioMetadata/musicMetadata/videoMetadata/animationMenu/animationList/musicCategories/musicSections/musicTracksの単独connection/actor nullで各NPE/message connection/actor。request付き六methodは単独request null/message requestも同methodで確認。固定正常入力はAudioId7/INLINE、track-7/INLINE、video-7、AnimationListCategory.MAIN、category、category/sectionで独立に構築。

PRE009/medPre009Track65BytesBeforeSql=Track ASCII65/X64、PRE010/medPre010Video65BytesBeforeSql=Video65/X64、PRE011/medPre011SectionCategory65BytesBeforeSql=Sections Category65/X64、PRE012/medPre012TrackCategory65BytesBeforeSql=Tracks Category65/X64、PRE013/medPre013TrackSection129BytesBeforeSql=Tracks Section129/X128。全てDTO構築をassert外に置き、input/payload encodeのFieldEncodingException/JDBC0を期待する。幅の正本はorigin/main UI235で、Production catalogから算出しない。

共通null/oversize helperはTest所有NoSql fixtureを持ち、任意Connection methodでcount++/AssertionError。実Connection/resourceを開かないのでcloseも禁止し、DB/driver/実media/manifest/Root/VM/ネットワーク/鍵/認証を使わない。公開合成actor7/USERは内部non-null fixtureで実認可証明ではない。各case/独立postでJDBC callback0/保留Main二probe0、queryのnonnull境界とtry内SQLを区別、unexpected SQL errorの注入はしない。

新13ID/13methodはScenario九と同source/一runで検証する。先行static/GJF/正常六compile/NullAway・閉catalog・全XML/CRC/一session・完整MediaRepository source四counter・全Main/旧Test保持・traceを004へ保存。SQLメニュー結果/表示順/owner/descriptor正常値/file配信/Range/並行/再送/実DB等は別未完。四counterの未達や0/0をPASSにせず、全G01/451/正式1964-53/既17-190/工数null/HOLD不変。
