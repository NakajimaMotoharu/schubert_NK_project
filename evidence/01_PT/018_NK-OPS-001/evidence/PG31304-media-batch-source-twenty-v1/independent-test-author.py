from pathlib import Path
import hashlib,json,datetime
r=Path.cwd();sha=hashlib.sha256(b'abc').hexdigest();mid=hashlib.sha256(b'SCHUBERT-NK:MUSIC:music/c.ogg').hexdigest();stamp='2026-01-02T03:04:05Z'
fields=[['1','video-a','VIDEO','A','MAIN',None,'video/a.mp4','current/a.mp4','a.mp4','3',sha,'video/mp4','video-b',None,None,'1',stamp],['2','video-b','VIDEO','B','MAIN',None,'video/b.mp4','current/b.mp4','b.mp4','3',sha,'video/mp4',None,None,None,'2',stamp],['3',mid,'MUSIC','C','BGM',None,'music/c.ogg','music/c.ogg','c.ogg','3',sha,'audio/ogg',None,None,'N','1',stamp]]
golden=''.join('\t'.join('\\N' if x is None else x for x in row)+'\n' for row in fields)
e=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG31304-media-batch-source-twenty-v1';(e/'independent-golden.json').open('x').write(json.dumps({'method':'Python hashlib.sha256 literal ASCII prefix+UTF8 displayPath; literal V002 seventeen-column order and explicit values; tab, LF and SQL null \\N; no Java/production calls','musicDisplayPath':'music/c.ogg','musicId':mid,'sha256Abc':sha,'expectedCopyUtf8':golden,'expectedCopySha256':hashlib.sha256(golden.encode()).hexdigest(),'fields':fields},ensure_ascii=False,indent=2)+'\n')
t='''package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-MEDIABATCH001..020; literal SQL/golden and independent Python SHA vector. */
final class MediaAssetCopyBatchTest {
  private static final String SHA = __SHA__;
  private static final String MUSIC_ID = __MID__;
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String GOLDEN = __GOLDEN__;
  private static final String DIAGNOSTIC = "migration media asset COPY batch is invalid";
  private static final String PARENT_A = "video-a";
  private static final String PARENT_B = "video-b";
  private static final String VIDEO_TYPE = "VIDEO";
  private static final String SOURCE_A = "current/a.mp4";
  private static final String SOURCE_B = "current/b.mp4";
  private static final String TARGET_A = "video/a.mp4";
  private static final String TARGET_B = "video/b.mp4";
  private static final String MUSIC_PATH = "music/c.ogg";
  private static final String VIDEO_MIME = "video/mp4";
  private static final String ONE = "1";
  private static final String TWO = "2";
  private static final String THREE = "3";
  private static final int ID_INDEX = 0;
  private static final int LOGICAL_INDEX = 1;
  private static final int STORAGE_INDEX = 6;
  private static final int DISPLAY_INDEX = 7;
  private static final int PARENT_INDEX = 12;
  private static final int STAMP_INDEX = 16;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test void independentMixedSeventeenColumnGoldenAndColumnOrder() throws Exception {
    var batch = normal();
    assertArrayEquals(expected(), batch.copyBytes(new PostgresCopyTextEncoder()));
    assertEquals(List.of("id", "logical_id", "media_type", "title", "category", "section",
        "storage_relative_path", "display_path", "file_name", "byte_size", "sha256", "mime_type",
        "parent_logical_id", "pair_key", "pair_role", "display_order", "created_at"), batch.columnNames());
  }

  @Test void emptyDeclarationRemainsEmpty() throws Exception {
    var batch = new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of());
    assertEquals(List.of(), batch.rows());
    assertArrayEquals(new byte[0], batch.copyBytes(new PostgresCopyTextEncoder()));
    var sink = new TrackingSink(); batch.writeTo(writer(), sink);
    assertEquals(0, sink.size()); assertEquals(0, sink.closes); assertEquals(0, sink.flushes);
  }

  @Test void duplicatePrimaryIdIsRejected() throws Exception {
    var rows = raw(); rows.get(1).set(ID_INDEX, ONE); reject(rows, claims());
  }

  @Test void duplicateLogicalIdIsRejected() throws Exception {
    var rows = raw(); rows.get(1).set(LOGICAL_INDEX, PARENT_A); reject(rows, claims());
  }

  @Test void duplicateTypedStorageIsRejected() throws Exception {
    var rows = raw(); rows.get(1).set(STORAGE_INDEX, TARGET_A); reject(rows, claims());
  }

  @Test void transactionTimestampsMustAgree() throws Exception {
    var rows = raw(); rows.get(1).set(STAMP_INDEX, "2026-01-02T03:04:06Z"); reject(rows, claims());
  }

  @Test void backwardAndForwardParentReferencesUseTheWholeSet() throws Exception {
    var rows = raw(); rows.get(0).set(PARENT_INDEX, null); rows.get(1).set(PARENT_INDEX, PARENT_A);
    assertEquals(List.of(PARENT_A,PARENT_B,MUSIC_ID), make(rows, claims()).rows().stream().map(MediaAssetCopyRow::logicalId).toList());
    assertTrue(normal().rows().get(0).parentLogicalId().isPresent());
  }

  @Test void unknownParentIsRejectedAfterBuildingTheWholeSet() throws Exception {
    var rows = raw(); rows.get(0).set(PARENT_INDEX, "absent"); reject(rows, claims());
  }

  @Test void selfAndCyclesRemainAllowedByTheDeclaredForeignKey() throws Exception {
    var rows = raw(); rows.get(0).set(PARENT_INDEX, PARENT_A);
    assertEquals(PARENT_A, make(rows,claims()).rows().get(0).parentLogicalId().orElseThrow());
    rows.get(0).set(PARENT_INDEX, PARENT_B); rows.get(1).set(PARENT_INDEX,PARENT_A);
    assertEquals(PARENT_A, make(rows,claims()).rows().get(1).parentLogicalId().orElseThrow());
  }

  @Test void manifestCardinalityCannotBeSmallerOrLarger() throws Exception {
    var less = claims(); less.remove(0); reject(raw(),less);
    var more = claims(); more.add(new AssetMigrationManifest.Entry(AssetMigrationManifest.Kind.VIDEO,"other.mp4","video/other.mp4",3,SHA)); reject(raw(),more);
  }

  @Test void unknownOrRepeatedSourceCannotConsumeOneClaimTwice() throws Exception {
    var rows = raw(); rows.get(0).set(DISPLAY_INDEX,"unknown.mp4"); reject(rows,claims());
    rows = raw(); rows.get(1).set(DISPLAY_INDEX,SOURCE_A); reject(rows,claims());
  }

  @Test void kindsMustBeMediaAndMatchTheRow() throws Exception {
    for (var kind : List.of(AssetMigrationManifest.Kind.SCENARIO,AssetMigrationManifest.Kind.AUDIO,AssetMigrationManifest.Kind.MUSIC)) {
      var claims = claims(); claims.set(0,new AssetMigrationManifest.Entry(kind,SOURCE_A,TARGET_A,3,SHA)); reject(raw(),claims);
    }
  }

  @Test void targetSizeAndHashEachMatchTheExactDeclaration() throws Exception {
    var claims = claims(); claims.set(0,new AssetMigrationManifest.Entry(AssetMigrationManifest.Kind.VIDEO,SOURCE_A,"video/other.mp4",3,SHA)); reject(raw(),claims);
    claims = claims(); claims.set(0,new AssetMigrationManifest.Entry(AssetMigrationManifest.Kind.VIDEO,SOURCE_A,TARGET_A,4,SHA)); reject(raw(),claims);
    claims = claims(); claims.set(0,new AssetMigrationManifest.Entry(AssetMigrationManifest.Kind.VIDEO,SOURCE_A,TARGET_A,3,"0".repeat(64))); reject(raw(),claims);
  }

  @Test void nullableBoundariesHaveFixedDiagnostics() throws Exception {
    var manifest = new AssetMigrationManifest(claims());
    assertEquals(DIAGNOSTIC,assertThrows(IllegalArgumentException.class,()->new MediaAssetCopyBatch(null,List.of())).getMessage());
    assertEquals(DIAGNOSTIC,assertThrows(IllegalArgumentException.class,()->new MediaAssetCopyBatch(manifest,null)).getMessage());
    var rows = values(raw()); rows.set(1,null);
    assertEquals(DIAGNOSTIC,assertThrows(IllegalArgumentException.class,()->new MediaAssetCopyBatch(manifest,rows)).getMessage());
  }

  @Test void snapshotAndReturnedViewsAreImmutableAndKeepDeclaredOrder() throws Exception {
    var input = values(raw()); Collections.swap(input,0,2);
    var batch = new MediaAssetCopyBatch(new AssetMigrationManifest(claims()),input); input.clear();
    assertEquals(List.of(MUSIC_ID,PARENT_B,PARENT_A),batch.rows().stream().map(MediaAssetCopyRow::logicalId).toList());
    assertThrows(UnsupportedOperationException.class,()->batch.rows().clear());
    assertThrows(UnsupportedOperationException.class,()->batch.columnNames().clear());
    assertThrows(UnsupportedOperationException.class,()->batch.rows().get(0).fields().clear());
  }

  @Test void typedAccessorsExposeValidatedValuesAndOptionalParents() throws Exception {
    var row = normal().rows().get(0);
    assertEquals(ONE,row.id()); assertEquals(PARENT_A,row.logicalId()); assertEquals(VIDEO_TYPE,row.mediaType());
    assertEquals(TARGET_A,row.storageRelativePath()); assertEquals(SOURCE_A,row.displayPath());
    assertEquals(THREE,row.byteSize()); assertEquals(SHA,row.sha256()); assertEquals(STAMP,row.createdAt());
    assertEquals(PARENT_B,row.parentLogicalId().orElseThrow());
    assertTrue(normal().rows().get(1).parentLogicalId().isEmpty());
  }

  @Test void returnedBytesAreOwnedAndNullEncoderIsRejected() throws Exception {
    var batch = normal(); byte[] first = batch.copyBytes(new PostgresCopyTextEncoder()); byte[] second = batch.copyBytes(new PostgresCopyTextEncoder());
    assertNotSame(first,second); first[0]=0; assertArrayEquals(expected(),second);
    assertEquals(DIAGNOSTIC,assertThrows(IllegalArgumentException.class,()->batch.copyBytes(null)).getMessage());
  }

  @Test void borrowedWriterAndSinkKeepOwnershipAndNullContract() throws Exception {
    var batch = normal(); var sink = new TrackingSink(); batch.writeTo(writer(),sink);
    assertArrayEquals(expected(),sink.toByteArray()); assertEquals(0,sink.closes); assertEquals(0,sink.flushes);
    assertEquals(DIAGNOSTIC,assertThrows(IllegalArgumentException.class,()->batch.writeTo(null,sink)).getMessage());
    assertEquals(DIAGNOSTIC,assertThrows(IllegalArgumentException.class,()->batch.writeTo(writer(),null)).getMessage());
  }

  @Test void ioFailureIdentityPartialOutputAndIndependentRetryArePreserved() throws Exception {
    var batch = normal(); var sink = new FailingSink();
    assertSame(sink.failure,assertThrows(IOException.class,()->batch.writeTo(writer(),sink)));
    assertArrayEquals("1\\t".getBytes(StandardCharsets.UTF_8),sink.prefix.toByteArray());
    assertEquals(0,sink.closes); assertEquals(0,sink.flushes);
    var normal = new TrackingSink(); batch.writeTo(writer(),normal); assertArrayEquals(expected(),normal.toByteArray());
    assertEquals("MediaAssetCopyBatch[REDACTED]",batch.toString());
  }

  @Test void finiteWorkersUseOneImmutableBatchWithIndependentSinks() throws Exception {
    var batch = normal(); var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<byte[]>>();
      for (int i=0;i<TASKS;i++) results.add(executor.submit(()->{var sink=new TrackingSink();batch.writeTo(writer(),sink);return sink.toByteArray();}));
      for(var result:results) assertArrayEquals(expected(),result.get(WAIT_SECONDS,TimeUnit.SECONDS));
    } finally {executor.shutdownNow();assertTrue(executor.awaitTermination(TERMINATION_SECONDS,TimeUnit.SECONDS));}
  }

  private static MediaAssetCopyBatch normal() throws Exception {return make(raw(),claims());}
  private static MediaAssetCopyBatch make(List<List<@Nullable String>> raw,List<AssetMigrationManifest.Entry> claims) throws Exception {return new MediaAssetCopyBatch(new AssetMigrationManifest(claims),values(raw));}
  private static ArrayList<@Nullable MediaAssetCopyRow> values(List<List<@Nullable String>> rows) throws Exception {
    var result = new ArrayList<@Nullable MediaAssetCopyRow>(); for(var row:rows)result.add(new MediaAssetCopyRow(row));return result;
  }
  private static void reject(List<List<@Nullable String>> rows,List<AssetMigrationManifest.Entry> claims) throws Exception {
    var validRows=values(rows);var manifest=new AssetMigrationManifest(claims);
    assertEquals(DIAGNOSTIC,assertThrows(IllegalArgumentException.class,()->new MediaAssetCopyBatch(manifest,validRows)).getMessage());
  }
  private static List<List<@Nullable String>> raw() {
    return new ArrayList<>(List.of(
        new ArrayList<@Nullable String>(Arrays.<@Nullable String>asList(ONE,PARENT_A,VIDEO_TYPE,"A","MAIN",null,TARGET_A,SOURCE_A,"a.mp4",THREE,SHA,VIDEO_MIME,PARENT_B,null,null,ONE,STAMP)),
        new ArrayList<@Nullable String>(Arrays.<@Nullable String>asList(TWO,PARENT_B,VIDEO_TYPE,"B","MAIN",null,TARGET_B,SOURCE_B,"b.mp4",THREE,SHA,VIDEO_MIME,null,null,null,TWO,STAMP)),
        new ArrayList<@Nullable String>(Arrays.<@Nullable String>asList(THREE,MUSIC_ID,"MUSIC","C","BGM",null,MUSIC_PATH,MUSIC_PATH,"c.ogg",THREE,SHA,"audio/ogg",null,null,"N",ONE,STAMP))));
  }
  private static ArrayList<AssetMigrationManifest.Entry> claims() {return new ArrayList<>(List.of(
      new AssetMigrationManifest.Entry(AssetMigrationManifest.Kind.VIDEO,SOURCE_A,TARGET_A,3,SHA),
      new AssetMigrationManifest.Entry(AssetMigrationManifest.Kind.VIDEO,SOURCE_B,TARGET_B,3,SHA),
      new AssetMigrationManifest.Entry(AssetMigrationManifest.Kind.MUSIC,MUSIC_PATH,MUSIC_PATH,3,SHA)));}
  private static byte[] expected() {return GOLDEN.getBytes(StandardCharsets.UTF_8);}
  private static PostgresCopyTextWriter writer() {return new PostgresCopyTextWriter(new PostgresCopyTextEncoder());}
  private static final class TrackingSink extends ByteArrayOutputStream {
    private int closes; private int flushes;
    @Override public void close() {closes++;}
    @Override public void flush() {flushes++;}
  }
  private static final class FailingSink extends OutputStream {
    private static final int PREFIX_BYTES=2;
    private final IOException failure=new IOException("synthetic media batch failure");
    private final ByteArrayOutputStream prefix=new ByteArrayOutputStream();
    private int closes;private int flushes;
    @Override public void write(int value) throws IOException {if(prefix.size()==PREFIX_BYTES)throw failure;prefix.write(value);}
    @Override public void close(){closes++;}
    @Override public void flush(){flushes++;}
  }
}
'''
t=t.replace('__SHA__',json.dumps(sha)).replace('__MID__',json.dumps(mid)).replace('__GOLDEN__',json.dumps(golden,ensure_ascii=False))
p=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/MediaAssetCopyBatchTest.java';p.open('x').write(t)
print('20 whole tests authored, independent golden sha',hashlib.sha256(golden.encode()).hexdigest())
