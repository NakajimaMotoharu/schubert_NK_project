package dev.codex.schubert.nk.protocol.layout;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/** Immutable 389-field UI 234-236 catalog. Trace: NK-PRO-001, SS 322 §2/§12. */
public final class LayoutFieldCatalog {
  private static final int CATALOG_COLUMN_COUNT = 8;
  private static final int MINIMUM_POSITIVE_VALUE = 1;

  private static final String CATALOG_TSV =
      """
        LGNREQ01\tDATA\tUsername\t1\t64\tX\tM\tNFC・trim後1～64 byte
        LGNREQ01\tDATA\tPassword\t65\t256\tX\tM\tNFC後1～256 byte。右spaceは値の一部と区別できないため末尾space passwordは禁止
        LGNREQ01\tDATA\tClient address\t321\t45\tX\tM\tIPv4/IPv6 text。Caddy検証済み
        LGNREQ01\tDATA\tReserved\t366\t19\tX\tF\t全space
        LGNRSP01\tDATA\tUsername\t1\t64\tX\tC\t成功時必須
        LGNRSP01\tDATA\tRole\t65\t5\tX\tC\t`USER`/`ADMIN`、成功時必須
        LGNRSP01\tDATA\t認証context ID\t70\t64\tX\tC\t成功時lowercase hex 64文字。header側は全space
        LGNRSP01\tDATA\t発行日時\t134\t17\tX\tC\t成功時17桁JST日時、失敗時全space
        LGNRSP01\tDATA\t期限日時\t151\t17\tX\tC\t成功時17桁JST日時、失敗時全space
        LGNRSP01\tDATA\tRetry after秒\t168\t6\tN\tM\tLock以外は0
        LGNRSP01\tDATA\t残り試行回数\t174\t3\tN\tM\t成功・非表示時0
        LGNRSP01\tDATA\t利用者message\t177\t256\tX\tO\tError/lock時。成功時全space
        LOGRSP01\tDATA\tSession失効日時\t1\t17\tN\tM\tJST日時
        LOGRSP01\tDATA\tReserved\t18\t7\tX\tF\t全space
        GAMRSP01\tDATA\tTotal count\t1\t9\tN\tM\tRecord件数と一致
        GAMRSP01\tRECORD\tGame code\t1\t12\tX\tM\t`NUKITASHI1`/`NUKITASHI2`
        GAMRSP01\tRECORD\tTitle\t13\t256\tX\tM\t表示title
        GAMRSP01\tRECORD\tDisplay order\t269\t3\tN\tM\t昇順
        GAMRSP01\tRECORD\tReserved\t272\t1\tX\tF\tSpace
        SPKREQ01\tDATA\tGame code\t1\t12\tX\tO\t全space/`NUKITASHI1`/`NUKITASHI2`
        SPKRSP01\tDATA\tTotal count\t1\t9\tN\tM\tRecord件数と一致
        SPKRSP01\tRECORD\tSpeaker ID\t1\t12\tN\tM\t内部ID
        SPKRSP01\tRECORD\tSpeaker名\t13\t128\tX\tM\t表示・検索値
        SPKRSP01\tRECORD\t出現件数\t141\t9\tN\tM\t対象game内entry件数
        SPKRSP01\tRECORD\tReserved\t150\t3\tX\tF\t全space
        SRCREQ01\tDATA\t本文keyword\t1\t256\tX\tO\t部分一致
        SRCREQ01\tDATA\tGame code\t257\t12\tX\tO\t全space/定義game
        SRCREQ01\tDATA\tSpeaker名\t269\t128\tX\tO\t完全一致
        SRCREQ01\tDATA\t章title\t397\t256\tX\tO\t部分一致
        SRCREQ01\tDATA\tEntry type\t653\t10\tX\tO\t全space/`dialogue`/`narration`
        SRCREQ01\tDATA\tVoice条件\t663\t1\tX\tO\tSpace/`1`あり/`0`なし
        SRCREQ01\tDATA\tPage\t664\t6\tN\tM\t1～999999
        SRCREQ01\tDATA\tPage size\t670\t3\tN\tM\t固定100
        SRCRSP01\tDATA\tEffective page\t1\t6\tN\tM\t1～999999
        SRCRSP01\tDATA\tPage size\t7\t3\tN\tM\tInterface固定値
        SRCRSP01\tDATA\tTotal count\t10\t9\tN\tM\tPage size 50は0～49,999,950、100は0～99,999,900
        SRCRSP01\tDATA\tTotal pages\t19\t6\tN\tM\t0件でも1
        SRCRSP01\tDATA\tFirst result\t25\t9\tN\tM\t0件は0
        SRCRSP01\tDATA\tLast result\t34\t9\tN\tM\t0件は0
        SRCRSP01\tDATA\tReserved\t43\t6\tX\tF\t全space
        SRCRSP01\tRECORD\tEntry ID\t1\t12\tN\tM\tScenario anchor ID
        SRCRSP01\tRECORD\tScript file ID\t13\t12\tN\tM\t明細遷移ID
        SRCRSP01\tRECORD\tGame code\t25\t12\tX\tM\t定義game
        SRCRSP01\tRECORD\t章title\t37\t256\tX\tO\t未設定はspace
        SRCRSP01\tRECORD\tLine番号\t293\t8\tN\tM\t1以上
        SRCRSP01\tRECORD\tEntry type\t301\t10\tX\tM\t`dialogue`/`narration`
        SRCRSP01\tRECORD\tSpeaker名\t311\t128\tX\tO\tNarrationはspace可
        SRCRSP01\tRECORD\t本文\t439\t4096\tX\tM\tCR/LF/TAB/NULなし
        SRCRSP01\tRECORD\tAudio有無\t4535\t1\tB\tM\t`0`/`1`
        SRCRSP01\tRECORD\tAudio ID\t4536\t12\tX\tC\tAudio有無1時ASCII数字、0時space
        SRCRSP01\tRECORD\tScript display path\t4548\t512\tX\tM\tSanitized表示専用。File解決には使用しない
        SRCRSP01\tRECORD\tAudio display path\t5060\t512\tX\tC\tAudio有無1時。Sanitized表示専用
        SRCRSP01\tRECORD\tReserved\t5572\t13\tX\tF\t全space
        RTEREQ01\tDATA\tGame code\t1\t12\tX\tM\t定義game
        RTERSP01\tDATA\tTotal count\t1\t9\tN\tM\tRecord件数と一致
        RTERSP01\tRECORD\tPrefix\t1\t2\tN\tM\t2桁section prefix
        RTERSP01\tRECORD\tRoute名\t3\t64\tX\tM\t固定mapまたは`未分類`
        RTERSP01\tRECORD\tFile件数\t67\t6\tN\tM\t1以上
        SCFREQ01\tDATA\tGame code\t1\t12\tX\tM\t定義game
        SCFREQ01\tDATA\tPrefix\t13\t2\tN\tM\t2桁
        SCFRSP01\tDATA\tGame code\t1\t12\tX\tM\t要求値
        SCFRSP01\tDATA\tPrefix\t13\t2\tN\tM\t要求値
        SCFRSP01\tDATA\tRoute名\t15\t64\tX\tM\t表示名
        SCFRSP01\tDATA\tTotal count\t79\t9\tN\tM\tRecord件数と一致
        SCFRSP01\tDATA\tReserved\t88\t1\tX\tF\tSpace
        SCFRSP01\tRECORD\tScript file ID\t1\t12\tN\tM\t明細遷移ID
        SCFRSP01\tRECORD\tDisplay title\t13\t256\tX\tM\t章title、section code、file名の最初の非空値
        SCFRSP01\tRECORD\tDisplay path\t269\t512\tX\tM\tSanitized表示専用
        SCFRSP01\tRECORD\tEntry件数\t781\t6\tN\tM\t0以上
        SCFRSP01\tRECORD\tReserved\t787\t14\tX\tF\t全space
        SCNREQ01\tDATA\tScript file ID\t1\t12\tN\tM\t対象ID
        SCNRSP01\tDATA\tScript file ID\t1\t12\tN\tM\t現在ID
        SCNRSP01\tDATA\tGame code\t13\t12\tX\tM\t定義game
        SCNRSP01\tDATA\tDisplay title\t25\t256\tX\tM\t現在title
        SCNRSP01\tDATA\tDisplay path\t281\t512\tX\tM\tSanitized表示専用
        SCNRSP01\tDATA\tPrevious file ID\t793\t12\tX\tO\tASCII数字/space
        SCNRSP01\tDATA\tPrevious title\t805\t256\tX\tC\tPrevious ID設定時
        SCNRSP01\tDATA\tNext file ID\t1061\t12\tX\tO\tASCII数字/space
        SCNRSP01\tDATA\tNext title\t1073\t256\tX\tC\tNext ID設定時
        SCNRSP01\tDATA\tDelivery mode\t1329\t1\tX\tM\t`I` inline/`F` large-result file
        SCNRSP01\tDATA\tFile ID\t1330\t36\tX\tC\tF時UUID
        SCNRSP01\tDATA\tFile relative path\t1366\t256\tX\tC\tF時transfer root基準
        SCNRSP01\tDATA\tFile byte長\t1622\t12\tN\tM\tI時0、F時実長
        SCNRSP01\tDATA\tFile SHA-256\t1634\t64\tX\tC\tF時lowercase hex
        SCNRSP01\tDATA\tFile record長\t1698\t6\tN\tM\tI時0、F時`004800`
        SCNRSP01\tDATA\tFile record件数\t1704\t9\tN\tM\tI時0、F時1～10000
        SCNRSP01\tDATA\tReserved\t1713\t16\tX\tF\t全space
        SCNRSP01\tRECORD\tEntry ID\t1\t12\tN\tM\t同じentryの複数audio recordで同値
        SCNRSP01\tRECORD\tEntry sequence\t13\t6\tN\tM\t1開始表示順
        SCNRSP01\tRECORD\tLine番号\t19\t8\tN\tM\t1以上
        SCNRSP01\tRECORD\tEntry type\t27\t10\tX\tM\t`dialogue`/`narration`
        SCNRSP01\tRECORD\tSpeaker名\t37\t128\tX\tO\tNarrationはspace可
        SCNRSP01\tRECORD\t本文\t165\t4096\tX\tM\t同じentryでは同値
        SCNRSP01\tRECORD\tAudio sequence\t4261\t3\tN\tM\tAudioなし0、あり1～999
        SCNRSP01\tRECORD\tAudio ID\t4264\t12\tX\tC\tAudioあり時ASCII数字
        SCNRSP01\tRECORD\tAudio display path\t4276\t512\tX\tC\tAudioあり時、sanitized表示専用
        SCNRSP01\tRECORD\tReserved\t4788\t13\tX\tF\t全space
        AUDREQ01\tDATA\tAudio ID\t1\t12\tN\tM\tDB logical ID
        AUDREQ01\tDATA\tDisposition\t13\t1\tX\tM\t`I`再生/`A`download
        AUDREQ01\tDATA\tReserved\t14\t3\tX\tF\t全space
        AUDRSP01\tDATA\tMedia logical ID\t1\t64\tX\tM\t要求IDのcanonical値
        AUDRSP01\tDATA\tStorage relative path\t65\t512\tX\tM\tBusiness asset root基準。絶対path禁止、Browser非表示
        AUDRSP01\tDATA\tFile name\t577\t256\tX\tM\t表示/download名
        AUDRSP01\tDATA\tFile byte長\t833\t12\tN\tM\t1以上
        AUDRSP01\tDATA\tSHA-256\t845\t64\tX\tM\tLowercase hex
        AUDRSP01\tDATA\tMIME type\t909\t64\tX\tM\t許可list内
        AUDRSP01\tDATA\tContent disposition\t973\t1\tX\tM\t`I` inline、`A` attachment
        AUDRSP01\tDATA\tReserved\t974\t51\tX\tF\t全space
        ANMRSP01\tDATA\tMain/SUBTRACK件数\t1\t3\tN\tM\t現行15
        ANMRSP01\tDATA\tOVA件数\t4\t3\tN\tM\t現行4
        ANMRSP01\tDATA\tOpening有無\t7\t1\tB\tM\t現行1
        ANMRSP01\tDATA\t総file件数\t8\t3\tN\tM\t現行20
        ANMRSP01\tDATA\tReserved\t11\t6\tX\tF\t全space
        ANLREQ01\tDATA\tCategory\t1\t16\tX\tM\t`MAIN`/`OVA`
        ANLRSP01\tDATA\tTotal count\t1\t6\tN\tM\tRecord件数
        ANLRSP01\tDATA\tReserved\t7\t2\tX\tF\t全space
        ANLRSP01\tRECORD\tVideo ID\t1\t64\tX\tM\tStable logical ID
        ANLRSP01\tRECORD\tTitle\t65\t256\tX\tM\t表示title
        ANLRSP01\tRECORD\tCategory\t321\t16\tX\tM\t`MAIN`/`SUBTRACK`/`OVA`
        ANLRSP01\tRECORD\tDisplay path\t337\t512\tX\tM\tSanitized表示専用。File解決には使用しない
        ANLRSP01\tRECORD\tFile byte長\t849\t12\tN\tM\t1以上
        ANLRSP01\tRECORD\tParent main ID\t861\t64\tX\tC\tSUBTRACK時対応main ID。他はspace
        ANLRSP01\tRECORD\tDisplay order\t925\t4\tN\tM\tCategory内順
        VIDREQ01\tDATA\tVideo ID\t1\t64\tX\tM\tStable logical ID
        VIDRSP01\tDATA\tMedia logical ID\t1\t64\tX\tM\t要求IDのcanonical値
        VIDRSP01\tDATA\tStorage relative path\t65\t512\tX\tM\tBusiness asset root基準。絶対path禁止、Browser非表示
        VIDRSP01\tDATA\tFile name\t577\t256\tX\tM\t表示/download名
        VIDRSP01\tDATA\tFile byte長\t833\t12\tN\tM\t1以上
        VIDRSP01\tDATA\tSHA-256\t845\t64\tX\tM\tLowercase hex
        VIDRSP01\tDATA\tMIME type\t909\t64\tX\tM\t許可list内
        VIDRSP01\tDATA\tContent disposition\t973\t1\tX\tM\t`I` inline、`A` attachment
        VIDRSP01\tDATA\tReserved\t974\t51\tX\tF\t全space
        VIDRSP01\tDATA\tTitle\t1025\t256\tX\tM\t表示title
        VIDRSP01\tDATA\tCategory\t1281\t16\tX\tM\t`MAIN`/`SUBTRACK`/`OVA`/`OPENING`
        VIDRSP01\tDATA\tDisplay path\t1297\t512\tX\tM\tSanitized表示専用。File解決には使用しない
        MCTRSP01\tDATA\tTotal count\t1\t6\tN\tM\tRecord件数
        MCTRSP01\tDATA\tReserved\t7\t2\tX\tF\t全space
        MCTRSP01\tRECORD\tCategory\t1\t64\tX\tM\t表示/要求値
        MCTRSP01\tRECORD\tTrack件数\t65\t6\tN\tM\tCategory配下総数
        MCTRSP01\tRECORD\tReserved\t71\t2\tX\tF\t全space
        MCSREQ01\tDATA\tCategory\t1\t64\tX\tM\tIF-013返却値
        MCSRSP01\tDATA\tTotal count\t1\t6\tN\tM\tRecord件数
        MCSRSP01\tDATA\tReserved\t7\t2\tX\tF\t全space
        MCSRSP01\tRECORD\tSection\t1\t128\tX\tM\t表示/要求値
        MCSRSP01\tRECORD\tTrack件数\t129\t6\tN\tM\tSection配下総数
        MCSRSP01\tRECORD\tReserved\t135\t2\tX\tF\t全space
        MTRREQ01\tDATA\tCategory\t1\t64\tX\tM\tIF-013返却値
        MTRREQ01\tDATA\tSection\t65\t128\tX\tM\tIF-014返却値
        MTRRSP01\tDATA\tTotal count\t1\t9\tN\tM\tRecord件数
        MTRRSP01\tDATA\tReserved\t10\t7\tX\tF\t全space
        MTRRSP01\tRECORD\tTrack ID\t1\t64\tX\tM\tStable logical ID
        MTRRSP01\tRECORD\tTitle\t65\t256\tX\tM\t表示title
        MTRRSP01\tRECORD\tCategory\t321\t64\tX\tM\tCategory
        MTRRSP01\tRECORD\tSection\t385\t128\tX\tM\tSection
        MTRRSP01\tRECORD\tDisplay path\t513\t512\tX\tM\tSanitized表示専用
        MTRRSP01\tRECORD\tFile byte長\t1025\t12\tN\tM\t1以上
        MTRRSP01\tRECORD\tPair key\t1037\t256\tX\tO\t`曲`のmain/instrumental grouping key
        MTRRSP01\tRECORD\tPair role\t1293\t1\tX\tM\t`M` main、`I` instrumental、`N` pair対象外
        MTRRSP01\tRECORD\tDisplay order\t1294\t4\tN\tM\t一覧順
        MTRRSP01\tRECORD\tReserved\t1298\t15\tX\tF\t全space
        MEDREQ01\tDATA\tTrack ID\t1\t64\tX\tM\tStable logical ID
        MEDREQ01\tDATA\tDisposition\t65\t1\tX\tM\t`I`再生/`A`download
        MEDREQ01\tDATA\tReserved\t66\t7\tX\tF\t全space
        MEDRSP01\tDATA\tMedia logical ID\t1\t64\tX\tM\t要求IDのcanonical値
        MEDRSP01\tDATA\tStorage relative path\t65\t512\tX\tM\tBusiness asset root基準。絶対path禁止、Browser非表示
        MEDRSP01\tDATA\tFile name\t577\t256\tX\tM\t表示/download名
        MEDRSP01\tDATA\tFile byte長\t833\t12\tN\tM\t1以上
        MEDRSP01\tDATA\tSHA-256\t845\t64\tX\tM\tLowercase hex
        MEDRSP01\tDATA\tMIME type\t909\t64\tX\tM\t許可list内
        MEDRSP01\tDATA\tContent disposition\t973\t1\tX\tM\t`I` inline、`A` attachment
        MEDRSP01\tDATA\tReserved\t974\t51\tX\tF\t全space
        LGSREQ01\tDATA\tKeyword\t1\t256\tX\tO\tMessage/details部分一致
        LGSREQ01\tDATA\tLog type\t257\t16\tX\tO\tACTION/REQUEST/SECURITY/MQ/SYSTEM/BATCH
        LGSREQ01\tDATA\tAction\t273\t64\tX\tO\t完全一致
        LGSREQ01\tDATA\tPath\t337\t256\tX\tO\t部分一致
        LGSREQ01\tDATA\tLevel\t593\t8\tX\tO\tINFO/WARN/ERROR
        LGSREQ01\tDATA\tFrom日時\t601\t17\tX\tO\tJST日時、全space可
        LGSREQ01\tDATA\tTo日時\t618\t17\tX\tO\tJST日時、From≦To、最大31日
        LGSREQ01\tDATA\tPage\t635\t6\tN\tM\t1以上
        LGSREQ01\tDATA\tPage size\t641\t3\tN\tM\t固定100
        LGSREQ01\tDATA\tReserved\t644\t13\tX\tF\t全space
        LGSRSP01\tDATA\tEffective page\t1\t6\tN\tM\t1～999999
        LGSRSP01\tDATA\tPage size\t7\t3\tN\tM\tInterface固定値
        LGSRSP01\tDATA\tTotal count\t10\t9\tN\tM\tPage size 50は0～49,999,950、100は0～99,999,900
        LGSRSP01\tDATA\tTotal pages\t19\t6\tN\tM\t0件でも1
        LGSRSP01\tDATA\tFirst result\t25\t9\tN\tM\t0件は0
        LGSRSP01\tDATA\tLast result\t34\t9\tN\tM\t0件は0
        LGSRSP01\tDATA\tReserved\t43\t6\tX\tF\t全space
        LGSRSP01\tRECORD\tLog ID\t1\t12\tN\tM\tID
        LGSRSP01\tRECORD\t発生日時\t13\t17\tN\tM\tJST
        LGSRSP01\tRECORD\tLog type\t30\t16\tX\tM\t定義値
        LGSRSP01\tRECORD\tLevel\t46\t8\tX\tM\tINFO/WARN/ERROR
        LGSRSP01\tRECORD\tAction\t54\t64\tX\tO\tAction code
        LGSRSP01\tRECORD\tMessage\t118\t512\tX\tM\t機微情報除外済み
        LGSRSP01\tRECORD\tHTTP request ID\t630\t36\tX\tO\tUUID
        LGSRSP01\tRECORD\t業務Message ID\t666\t36\tX\tO\tUUID
        LGSRSP01\tRECORD\tCorrelation ID\t702\t36\tX\tO\tUUID
        LGSRSP01\tRECORD\tHTTP method\t738\t8\tX\tO\tGET/POST等
        LGSRSP01\tRECORD\tPath\t746\t256\tX\tO\tURI path
        LGSRSP01\tRECORD\tHTTP status\t1002\t3\tX\tO\tASCII数字/space
        LGSRSP01\tRECORD\tElapsed ms\t1005\t9\tX\tO\tASCII数字/space
        LGSRSP01\tRECORD\tRemote address\t1014\t45\tX\tO\tIPv4/IPv6
        LGSRSP01\tRECORD\tDetails\t1059\t1024\tX\tO\t表示用JSON text、本文・秘密値なし
        LGSRSP01\tRECORD\tReserved\t2083\t6\tX\tF\t全space
        USRREQ01\tDATA\tUsername prefix\t1\t64\tX\tO\t前方一致
        USRREQ01\tDATA\tRole\t65\t5\tX\tO\tSpace/USER/ADMIN
        USRREQ01\tDATA\tState\t70\t8\tX\tO\tSpace/ACTIVE/DISABLED/LOCKED
        USRREQ01\tDATA\tPage\t78\t6\tN\tM\t1以上
        USRREQ01\tDATA\tPage size\t84\t3\tN\tM\t固定50
        USRREQ01\tDATA\tReserved\t87\t10\tX\tF\t全space
        USRRSP01\tDATA\tEffective page\t1\t6\tN\tM\t1～999999
        USRRSP01\tDATA\tPage size\t7\t3\tN\tM\tInterface固定値
        USRRSP01\tDATA\tTotal count\t10\t9\tN\tM\tPage size 50は0～49,999,950、100は0～99,999,900
        USRRSP01\tDATA\tTotal pages\t19\t6\tN\tM\t0件でも1
        USRRSP01\tDATA\tFirst result\t25\t9\tN\tM\t0件は0
        USRRSP01\tDATA\tLast result\t34\t9\tN\tM\t0件は0
        USRRSP01\tDATA\tReserved\t43\t6\tX\tF\t全space
        USRRSP01\tRECORD\tUser ID\t1\t12\tN\tM\tID
        USRRSP01\tRECORD\tUsername\t13\t64\tX\tM\t表示名
        USRRSP01\tRECORD\tRole\t77\t5\tX\tM\tUSER/ADMIN
        USRRSP01\tRECORD\tState\t82\t8\tX\tM\tACTIVE/DISABLED/LOCKED
        USRRSP01\tRECORD\tLocked until\t90\t17\tX\tO\tJST日時/space
        USRRSP01\tRECORD\tLast Login\t107\t17\tX\tO\tJST日時/space
        USRRSP01\tRECORD\tCreated at\t124\t17\tN\tM\tJST日時
        USRRSP01\tRECORD\tUpdated at\t141\t17\tN\tM\tJST日時
        USRRSP01\tRECORD\tVersion\t158\t9\tN\tM\tOptimistic lock
        USRRSP01\tRECORD\tReserved\t167\t2\tX\tF\t全space
        UCRREQ01\tDATA\tUsername\t1\t64\tX\tM\t`A-Z a-z 0-9 . _ -`、比較はcase-insensitive
        UCRREQ01\tDATA\tInitial Password\t65\t256\tX\tM\tNFC、12～128文字、256 byte以下、末尾space禁止
        UCRREQ01\tDATA\tRole\t321\t5\tX\tM\tUSER/ADMIN
        UCRREQ01\tDATA\tEnabled\t326\t1\tB\tM\t0/1
        UCRREQ01\tDATA\tOperation token\t327\t36\tX\tM\tWeb採番UUID。二重更新防止
        UCRREQ01\tDATA\tReserved\t363\t10\tX\tF\t全space
        UCRRSP01\tDATA\tUser ID\t1\t12\tN\tM\t成功時のTarget ID
        UCRRSP01\tDATA\t更新後version\t13\t9\tN\tM\t成功時のOptimistic lock version
        UCRRSP01\tDATA\tReserved\t22\t3\tX\tF\t全space
        UDTREQ01\tDATA\tUser ID\t1\t12\tN\tM\tTarget ID
        UDTRSP01\tDATA\tUser ID\t1\t12\tN\tM\tID
        UDTRSP01\tDATA\tUsername\t13\t64\tX\tM\t表示名
        UDTRSP01\tDATA\tRole\t77\t5\tX\tM\tUSER/ADMIN
        UDTRSP01\tDATA\tState\t82\t8\tX\tM\tACTIVE/DISABLED/LOCKED
        UDTRSP01\tDATA\tLocked until\t90\t17\tX\tO\tJST/space
        UDTRSP01\tDATA\tLast Login\t107\t17\tX\tO\tJST/space
        UDTRSP01\tDATA\tPassword changed at\t124\t17\tN\tM\tJST
        UDTRSP01\tDATA\tCreated at\t141\t17\tN\tM\tJST
        UDTRSP01\tDATA\tUpdated at\t158\t17\tN\tM\tJST
        UDTRSP01\tDATA\tActive session数\t175\t3\tN\tM\t0～2
        UDTRSP01\tDATA\tVersion\t178\t9\tN\tM\tOptimistic lock
        UDTRSP01\tDATA\tCreated by\t187\t64\tX\tM\tActor username。BootstrapのDB NULLは`SYSTEM`
        UDTRSP01\tDATA\tUpdated by\t251\t64\tX\tM\tActor username。BootstrapのDB NULLは`SYSTEM`
        UDTRSP01\tDATA\tReserved\t315\t6\tX\tF\t全space
        USTREQ01\tDATA\tUser ID\t1\t12\tN\tM\tTarget
        USTREQ01\tDATA\tEnabled\t13\t1\tB\tM\t0無効/1有効
        USTREQ01\tDATA\tExpected version\t14\t9\tN\tM\t画面表示version
        USTREQ01\tDATA\tOperation token\t23\t36\tX\tM\tWeb採番UUID
        USTREQ01\tDATA\tReserved\t59\t2\tX\tF\t全space
        USTRSP01\tDATA\tUser ID\t1\t12\tN\tM\t成功時のTarget ID
        USTRSP01\tDATA\t更新後version\t13\t9\tN\tM\t成功時のOptimistic lock version
        USTRSP01\tDATA\tReserved\t22\t3\tX\tF\t全space
        URLREQ01\tDATA\tUser ID\t1\t12\tN\tM\tTarget
        URLREQ01\tDATA\tNew role\t13\t5\tX\tM\tUSER/ADMIN
        URLREQ01\tDATA\tExpected version\t18\t9\tN\tM\t画面表示version
        URLREQ01\tDATA\tOperation token\t27\t36\tX\tM\tWeb採番UUID
        URLREQ01\tDATA\tReserved\t63\t6\tX\tF\t全space
        URLRSP01\tDATA\tUser ID\t1\t12\tN\tM\t成功時のTarget ID
        URLRSP01\tDATA\t更新後version\t13\t9\tN\tM\t成功時のOptimistic lock version
        URLRSP01\tDATA\tReserved\t22\t3\tX\tF\t全space
        UPWREQ01\tDATA\tUser ID\t1\t12\tN\tM\tTarget
        UPWREQ01\tDATA\tNew Password\t13\t256\tX\tM\tUser作成と同じpolicy
        UPWREQ01\tDATA\tExpected version\t269\t9\tN\tM\t画面表示version
        UPWREQ01\tDATA\tOperation token\t278\t36\tX\tM\tWeb採番UUID
        UPWREQ01\tDATA\tReserved\t314\t11\tX\tF\t全space
        UPWRSP01\tDATA\tUser ID\t1\t12\tN\tM\t成功時のTarget ID
        UPWRSP01\tDATA\t更新後version\t13\t9\tN\tM\t成功時のOptimistic lock version
        UPWRSP01\tDATA\tReserved\t22\t3\tX\tF\t全space
        ULKREQ01\tDATA\tUser ID\t1\t12\tN\tM\tTarget
        ULKREQ01\tDATA\tExpected version\t13\t9\tN\tM\t画面表示version
        ULKREQ01\tDATA\tOperation token\t22\t36\tX\tM\tWeb採番UUID
        ULKREQ01\tDATA\tReserved\t58\t3\tX\tF\t全space
        ULKRSP01\tDATA\tUser ID\t1\t12\tN\tM\t成功時のTarget ID
        ULKRSP01\tDATA\t更新後version\t13\t9\tN\tM\t成功時のOptimistic lock version
        ULKRSP01\tDATA\tReserved\t22\t3\tX\tF\t全space
        QSBREQ01\tDATA\t質問本文\t1\t4096\tX\tM\tNFC後1～4096 byte、CR/LF/TAB/NULと末尾ASCII spaceなし
        QSBREQ01\tDATA\tOperation token\t4097\t36\tX\tM\tWeb採番UUID、利用者session内で一意
        QSBREQ01\tDATA\tReserved\t4133\t12\tX\tF\t全space
        QSBRSP01\tDATA\t受付ID\t1\t26\tX\tM\tRandom public ID
        QSBRSP01\tDATA\tQuestion ID\t27\t12\tN\tM\t内部ID
        QSBRSP01\tDATA\t受付日時\t39\t17\tN\tM\tJST
        QSBRSP01\tDATA\tReserved\t56\t9\tX\tF\t全space
        NTSREQ01\tDATA\t通知区分\t1\t12\tX\tO\tACCEPTED/COMPLETED/ERROR/space
        NTSREQ01\tDATA\t受付日時From\t13\t17\tX\tO\tJST/space
        NTSREQ01\tDATA\t受付日時To\t30\t17\tX\tO\tJST/space、最大366日
        NTSREQ01\tDATA\tPage\t47\t6\tN\tM\t1以上
        NTSREQ01\tDATA\tPage size\t53\t3\tN\tM\t固定50
        NTSREQ01\tDATA\tReserved\t56\t9\tX\tF\t全space
        NTSRSP01\tDATA\tEffective page\t1\t6\tN\tM\t1～999999
        NTSRSP01\tDATA\tPage size\t7\t3\tN\tM\tInterface固定値
        NTSRSP01\tDATA\tTotal count\t10\t9\tN\tM\tPage size 50は0～49,999,950、100は0～99,999,900
        NTSRSP01\tDATA\tTotal pages\t19\t6\tN\tM\t0件でも1
        NTSRSP01\tDATA\tFirst result\t25\t9\tN\tM\t0件は0
        NTSRSP01\tDATA\tLast result\t34\t9\tN\tM\t0件は0
        NTSRSP01\tDATA\tReserved\t43\t6\tX\tF\t全space
        NTSRSP01\tRECORD\tNotification ID\t1\t12\tN\tM\t明細ID
        NTSRSP01\tRECORD\t受付ID\t13\t26\tX\tM\tPublic ID
        NTSRSP01\tRECORD\t通知区分\t39\t12\tX\tM\tACCEPTED/COMPLETED/ERROR
        NTSRSP01\tRECORD\t内部状態\t51\t12\tX\tM\tRECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLED
        NTSRSP01\tRECORD\t受付日時\t63\t17\tN\tM\tJST
        NTSRSP01\tRECORD\t最終更新日時\t80\t17\tN\tM\tJST
        NTSRSP01\tRECORD\t質問概要\t97\t512\tX\tM\t先頭100文字相当または`削除済み`
        NTSRSP01\tRECORD\t質問削除済み\t609\t1\tB\tM\t0/1
        NTSRSP01\tRECORD\tReserved\t610\t15\tX\tF\t全space
        NTDREQ01\tDATA\tNotification ID\t1\t12\tN\tM\tTarget
        NTDRSP01\tDATA\tNotification ID\t1\t12\tN\tM\tID
        NTDRSP01\tDATA\t受付ID\t13\t26\tX\tM\tPublic ID
        NTDRSP01\tDATA\t通知区分\t39\t12\tX\tM\t定義値
        NTDRSP01\tDATA\t内部状態\t51\t12\tX\tM\t定義状態
        NTDRSP01\tDATA\t受付日時\t63\t17\tN\tM\tJST
        NTDRSP01\tDATA\t処理開始日時\t80\t17\tX\tC\tPROCESSING/COMPLETED/ERROR時JST、他はspace
        NTDRSP01\tDATA\t処理完了日時\t97\t17\tX\tC\tCOMPLETED時JST、他はspace
        NTDRSP01\tDATA\tError日時\t114\t17\tX\tC\tERROR時JST、他はspace
        NTDRSP01\tDATA\t取消日時\t131\t17\tX\tC\tCANCELLED時JST、他はspace
        NTDRSP01\tDATA\t質問削除済み\t148\t1\tB\tM\t0/1
        NTDRSP01\tDATA\t質問本文\t149\t4096\tX\tC\t未削除時。削除済みはspace
        NTDRSP01\tDATA\t回答本文\t4245\t4096\tX\tO\tCOMPLETED時。空回答は全spaceと区別するため状態で判定
        NTDRSP01\tDATA\tError code\t8341\t16\tX\tC\tERROR時必須、他はspace
        NTDRSP01\tDATA\t利用者向けerror\t8357\t512\tX\tC\tERROR時必須、他はspace
        NTDRSP01\tDATA\tQuestion ID\t8869\t12\tX\tC\t未削除時ASCII数字、削除済みはspace
        NTDRSP01\tDATA\tReserved\t8881\t16\tX\tF\t全space
        NTCREQ01\tDATA\tNotification ID\t1\t12\tN\tM\tTarget
        NTCREQ01\tDATA\tOperation token\t13\t36\tX\tM\tUUID
        NTCRSP01\tDATA\t更新後状態\t1\t12\tX\tC\t`0000`/`0200`はCANCELLED、`0107`は競合時最新状態
        NTCRSP01\tDATA\t取消日時\t13\t17\tX\tC\t`0000`/`0200`時JST、`0107`時space
        NTCRSP01\tDATA\tReserved\t30\t3\tX\tF\t全space
        QSSREQ01\tDATA\tKeyword\t1\t256\tX\tO\t質問/回答部分一致
        QSSREQ01\tDATA\tUsername\t257\t64\tX\tO\tADMINのみ完全一致。USERはspace必須
        QSSREQ01\tDATA\t回答状態\t321\t12\tX\tO\tANSWERED/UNANSWERED/ERROR/space
        QSSREQ01\tDATA\t受付日時From\t333\t17\tX\tO\tJST/space
        QSSREQ01\tDATA\t受付日時To\t350\t17\tX\tO\tJST/space、最大366日
        QSSREQ01\tDATA\tPage\t367\t6\tN\tM\t1以上
        QSSREQ01\tDATA\tPage size\t373\t3\tN\tM\t固定50
        QSSREQ01\tDATA\tReserved\t376\t9\tX\tF\t全space
        QSSRSP01\tDATA\tEffective page\t1\t6\tN\tM\t1～999999
        QSSRSP01\tDATA\tPage size\t7\t3\tN\tM\tInterface固定値
        QSSRSP01\tDATA\tTotal count\t10\t9\tN\tM\tPage size 50は0～49,999,950、100は0～99,999,900
        QSSRSP01\tDATA\tTotal pages\t19\t6\tN\tM\t0件でも1
        QSSRSP01\tDATA\tFirst result\t25\t9\tN\tM\t0件は0
        QSSRSP01\tDATA\tLast result\t34\t9\tN\tM\t0件は0
        QSSRSP01\tDATA\tReserved\t43\t6\tX\tF\t全space
        QSSRSP01\tRECORD\tQuestion ID\t1\t12\tN\tM\t明細ID
        QSSRSP01\tRECORD\t受付ID\t13\t26\tX\tM\tPublic ID
        QSSRSP01\tRECORD\tUsername\t39\t64\tX\tM\tADMIN表示用。USER responseにも設定
        QSSRSP01\tRECORD\t質問概要\t103\t512\tX\tM\t先頭100文字相当
        QSSRSP01\tRECORD\t回答状態\t615\t12\tX\tM\tANSWERED/UNANSWERED/ERROR
        QSSRSP01\tRECORD\t受付日時\t627\t17\tN\tM\tJST
        QSSRSP01\tRECORD\t回答日時\t644\t17\tX\tC\tANSWERED時JST、他はspace
        QSSRSP01\tRECORD\tReserved\t661\t12\tX\tF\t全space
        QSDREQ01\tDATA\tQuestion ID\t1\t12\tN\tM\tTarget
        QSDRSP01\tDATA\tQuestion ID\t1\t12\tN\tM\tID
        QSDRSP01\tDATA\t受付ID\t13\t26\tX\tM\tPublic ID
        QSDRSP01\tDATA\tUsername\t39\t64\tX\tM\tOwner
        QSDRSP01\tDATA\t回答状態\t103\t12\tX\tM\tANSWERED/UNANSWERED/ERROR
        QSDRSP01\tDATA\t質問本文\t115\t4096\tX\tM\t本文
        QSDRSP01\tDATA\t回答本文\t4211\t4096\tX\tO\t空回答可
        QSDRSP01\tDATA\t受付日時\t8307\t17\tN\tM\tJST
        QSDRSP01\tDATA\t回答日時\t8324\t17\tX\tC\tANSWERED時JST、他はspace
        QSDRSP01\tDATA\tReserved\t8341\t12\tX\tF\t全space
        QDLREQ01\tDATA\tQuestion ID\t1\t12\tN\tM\tTarget
        QDLREQ01\tDATA\tOperation token\t13\t36\tX\tM\tUUID
        QDLRSP01\tDATA\t削除日時\t1\t17\tN\tM\t論理削除JST日時
        QDLRSP01\tDATA\tReserved\t18\t7\tX\tF\t全space
        QWKREQ01\tDATA\t受付ID\t1\t26\tX\tM\tPublic ID
        QWKREQ01\tDATA\tQuestion ID\t27\t12\tN\tM\tDB ID
        QWKREQ01\tDATA\tAsync job ID\t39\t12\tN\tM\tJob ID
        QWKREQ01\tDATA\tReserved\t51\t14\tX\tF\t全space
        WLGEVT01\tDATA\t発生日時\t1\t17\tN\tM\tHTTP response確定時のJST
        WLGEVT01\tDATA\tLog type\t18\t16\tX\tM\tREQUEST/ACTION。QA054限定組合せ
        WLGEVT01\tDATA\tLevel\t34\t8\tX\tM\tINFO/WARN/ERROR
        WLGEVT01\tDATA\tAction\t42\t64\tX\tO\tBounded action code
        WLGEVT01\tDATA\tMessage\t106\t512\tX\tM\t本文・secretを含まない定型要約
        WLGEVT01\tDATA\tHTTP request ID\t618\t36\tX\tM\tUUID
        WLGEVT01\tDATA\tHTTP method\t654\t8\tX\tM\tGET/POST等
        WLGEVT01\tDATA\tPath\t662\t256\tX\tM\tQueryを除くURI path。制御文字なし
        WLGEVT01\tDATA\tHTTP status\t918\t3\tX\tM\tASCII 3桁
        WLGEVT01\tDATA\tElapsed ms\t921\t9\tX\tM\tASCII数字、0～999999999
        WLGEVT01\tDATA\tRemote address\t930\t45\tX\tM\t検証済みIPv4/IPv6 text
        WLGEVT01\tDATA\tUsername\t975\t64\tX\tO\t未認証はspace
        WLGEVT01\tDATA\tRole\t1039\t5\tX\tO\tUSER/ADMIN/space
        WLGEVT01\tDATA\tDetails\t1044\t1024\tX\tO\t表示用bounded JSON。本文、query値、cookie、tokenなし
        WLGEVT01\tDATA\tReserved\t2068\t13\tX\tF\t全space
      """;

  private static final LayoutFieldCatalog RETAINED_STANDARD =
      parse(CATALOG_TSV, LayoutRegistry.standard());

  private final List<LayoutFields> layouts;
  private final Map<String, LayoutFields> byId;

  private LayoutFieldCatalog(List<LayoutFields> source) {
    layouts = List.copyOf(source);
    LinkedHashMap<String, LayoutFields> index = new LinkedHashMap<>();
    for (LayoutFields fields : layouts) {
      index.put(fields.id().value(), fields);
    }
    byId = Collections.unmodifiableMap(index);
  }

  public static LayoutFieldCatalog standard() {
    return RETAINED_STANDARD;
  }

  public List<LayoutFields> all() {
    return layouts;
  }

  public LayoutFields require(LayoutId id) {
    Objects.requireNonNull(id, "id");
    LayoutFields fields = byId.get(id.value());
    if (fields == null) {
      throw new UnsupportedLayoutException("unsupported layout field catalog");
    }
    return fields;
  }

  public LayoutFields require(String id) {
    Objects.requireNonNull(id, "id");
    return require(new LayoutId(id));
  }

  public int fieldCount() {
    return layouts.stream()
        .mapToInt(fields -> fields.dataFields().size() + fields.recordFields().size())
        .sum();
  }

  public List<String> tsvRows() {
    ArrayList<String> rows = new ArrayList<>(fieldCount());
    for (LayoutFields fields : layouts) {
      appendRows(rows, fields.id(), fields.dataFields());
      appendRows(rows, fields.id(), fields.recordFields());
    }
    return Collections.unmodifiableList(rows);
  }

  static LayoutFieldCatalog parse(String tsv, LayoutRegistry registry) {
    Objects.requireNonNull(tsv, "tsv");
    Objects.requireNonNull(registry, "registry");
    LinkedHashMap<String, MutableFields> parsed = new LinkedHashMap<>();
    for (String rawLine : tsv.lines().toList()) {
      String line = rawLine.strip();
      if (line.isEmpty() || line.startsWith("#")) {
        continue;
      }
      String[] cells = line.split("\\t", -1);
      if (cells.length != CATALOG_COLUMN_COUNT) {
        throw new LayoutValidationException("field catalog row must contain eight columns");
      }
      LayoutDefinition layout = registry.require(cells[0], 1);
      FieldArea area = parseArea(cells[1]);
      String name = cells[2];
      int start = parsePositiveInt(cells[3], "field start");
      int length = parsePositiveInt(cells[4], "field length");
      WireType wireType = parseWireType(cells[5]);
      Presence presence = parsePresence(cells[6]);
      validateFixedField(layout.id(), name, presence);
      Padding padding = paddingFor(wireType);
      FieldDefinition<?> field =
          new FieldDefinition<>(
              area,
              name,
              start,
              length,
              wireType,
              presence,
              padding,
              javaTypeFor(wireType),
              cells[7]);
      MutableFields target =
          parsed.computeIfAbsent(layout.id().value(), ignored -> new MutableFields());
      List<FieldDefinition<?>> areaFields =
          area == FieldArea.DATA ? target.dataFields : target.recordFields;
      if (areaFields.stream().anyMatch(existing -> existing.name().equals(name))) {
        throw new LayoutValidationException("duplicate field name within one payload area");
      }
      areaFields.add(field);
    }

    ArrayList<LayoutFields> result = new ArrayList<>(registry.all().size());
    for (LayoutDefinition layout : registry.all()) {
      MutableFields fields = parsed.getOrDefault(layout.id().value(), new MutableFields());
      result.add(new LayoutFields(layout, fields.dataFields, fields.recordFields));
    }
    return new LayoutFieldCatalog(result);
  }

  private static void appendRows(List<String> rows, LayoutId id, List<FieldDefinition<?>> fields) {
    for (FieldDefinition<?> field : fields) {
      rows.add(
          String.join(
              "\t",
              id.value(),
              field.area().name(),
              field.name(),
              Integer.toString(field.start()),
              Integer.toString(field.length()),
              wireCode(field.wireType()),
              presenceCode(field.presence()),
              field.semanticRule()));
    }
  }

  private static FieldArea parseArea(String value) {
    {
      final String dispatchValue0 = java.util.Objects.requireNonNull(value);
      if (dispatchValue0.equals("DATA")) {
        return FieldArea.DATA;
      } else if (dispatchValue0.equals("RECORD")) {
        return FieldArea.RECORD;
      } else {
        throw new LayoutValidationException("unknown field area");
      }
    }
  }

  private static WireType parseWireType(String value) {
    {
      final String dispatchValue1 = java.util.Objects.requireNonNull(value);
      if (dispatchValue1.equals("X")) {
        return WireType.TEXT;
      } else if (dispatchValue1.equals("N")) {
        return WireType.NUMERIC;
      } else if (dispatchValue1.equals("B")) {
        return WireType.BOOLEAN;
      } else {
        throw new LayoutValidationException("unknown wire type");
      }
    }
  }

  private static Presence parsePresence(String value) {
    {
      final String dispatchValue2 = java.util.Objects.requireNonNull(value);
      if (dispatchValue2.equals("M")) {
        return Presence.MANDATORY;
      } else if (dispatchValue2.equals("C")) {
        return Presence.CONDITIONAL;
      } else if (dispatchValue2.equals("O")) {
        return Presence.OPTIONAL;
      } else if (dispatchValue2.equals("F")) {
        return Presence.FIXED;
      } else {
        throw new LayoutValidationException("unknown presence");
      }
    }
  }

  private static Padding paddingFor(WireType type) {
    {
      final WireType dispatchValue3 = java.util.Objects.requireNonNull(type);
      if (dispatchValue3 == WireType.TEXT) {
        return Padding.SPACE_RIGHT;
      } else if (dispatchValue3 == WireType.NUMERIC) {
        return Padding.ZERO_LEFT;
      } else {
        return Padding.NONE;
      }
    }
  }

  private static void validateFixedField(LayoutId layoutId, String name, Presence presence) {
    if (presence == Presence.FIXED && !name.equals("Reserved")) {
      throw new LayoutValidationException("unknown fixed payload field");
    }
  }

  private static Class<?> javaTypeFor(WireType type) {
    {
      final WireType dispatchValue4 = java.util.Objects.requireNonNull(type);
      if (dispatchValue4 == WireType.TEXT) {
        return String.class;
      } else if (dispatchValue4 == WireType.NUMERIC) {
        return Long.class;
      } else {
        return Boolean.class;
      }
    }
  }

  private static String wireCode(WireType type) {
    {
      final WireType dispatchValue5 = java.util.Objects.requireNonNull(type);
      if (dispatchValue5 == WireType.TEXT) {
        return "X";
      } else if (dispatchValue5 == WireType.NUMERIC) {
        return "N";
      } else {
        return "B";
      }
    }
  }

  private static String presenceCode(Presence presence) {
    {
      final Presence dispatchValue6 = java.util.Objects.requireNonNull(presence);
      if (dispatchValue6 == Presence.MANDATORY) {
        return "M";
      } else if (dispatchValue6 == Presence.CONDITIONAL) {
        return "C";
      } else if (dispatchValue6 == Presence.OPTIONAL) {
        return "O";
      } else {
        return "F";
      }
    }
  }

  private static int parsePositiveInt(String value, String label) {
    final int parsed;
    try {
      parsed = Integer.parseInt(value);
    } catch (NumberFormatException exception) {
      throw new LayoutValidationException(label + " is not an integer", exception);
    }
    if (parsed < MINIMUM_POSITIVE_VALUE) {
      throw new LayoutValidationException(label + " must be positive");
    }
    return parsed;
  }

  private static final class MutableFields {
    private final List<FieldDefinition<?>> dataFields = new ArrayList<>();
    private final List<FieldDefinition<?>> recordFields = new ArrayList<>();
  }
}
