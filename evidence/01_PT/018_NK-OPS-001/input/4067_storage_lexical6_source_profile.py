"""Independent lexical record fixtures, no actual root, filesystem or identity lookup."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));prefix='src/schubert-nk-storage/src/';mains=[prefix+'main/java/dev/codex/schubert/nk/storage/'+n+'.java' for n in ['StorageIdentity','StorageRootLayout']];old=prefix+'test/java/dev/codex/schubert/nk/storage/StorageRootLayoutTest.java';assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in mains+[old]);new=prefix+'test/java/dev/codex/schubert/nk/storage/StorageLexicalValueContractTest.java';p=r/new;assert not p.exists();p.open('x').write('''package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-STORAGE-IDENT001..003/LEX004; SS333/343/354: strings and lexical paths, never OS authority. */
final class StorageLexicalValueContractTest {
  private static final String FIXED_IDENTITY = "StorageIdentity[REDACTED]";
  private static final String FIXED_LAYOUT = "StorageRootLayout[REDACTED]";
  private static final String OWNER = "nk_asset";
  private static final String GROUP = "nk_shared";

  @Test
  void ident001LiteralNamesAndLengthBoundariesArePreservedAsBothRecordComponents() {
    for (String name : List.of("a", "_", "nk_asset", "a0_-", "a".repeat(32), "_".repeat(32))) {
      StorageIdentity owner = new StorageIdentity(name, GROUP);
      StorageIdentity group = new StorageIdentity(OWNER, name);
      assertEquals(name, owner.owner());
      assertEquals(GROUP, owner.group());
      assertEquals(OWNER, group.owner());
      assertEquals(name, group.group());
      assertEquals(FIXED_IDENTITY, owner.toString());
      assertEquals(FIXED_IDENTITY, group.toString());
    }
  }

  @Test
  void ident002EveryInvalidComponentRejectsWithoutLeakingItsLiteralInput() {
    for (String name :
        List.of("", "a".repeat(33), "0name", "-name", "Upper", "space name", "x/y", "あ", "a\\n")) {
      IllegalArgumentException owner =
          assertThrows(IllegalArgumentException.class, () -> new StorageIdentity(name, GROUP));
      IllegalArgumentException group =
          assertThrows(IllegalArgumentException.class, () -> new StorageIdentity(OWNER, name));
      for (IllegalArgumentException failure : List.of(owner, group)) {
        assertEquals("invalid storage OS identity", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
      }
    }
    assertEquals(
        "OS identity",
        assertThrows(NullPointerException.class, () -> new StorageIdentity(null, GROUP)).getMessage());
    assertEquals(
        "OS identity",
        assertThrows(NullPointerException.class, () -> new StorageIdentity(OWNER, null)).getMessage());
  }

  @Test
  void ident003BothComponentsDefineEqualityEvenWhenDistinctOwnersHaveEqualStringHashes() {
    StorageIdentity value = new StorageIdentity(OWNER, GROUP);
    StorageIdentity equal = new StorageIdentity(OWNER, GROUP);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, OWNER);
    for (StorageIdentity other :
        List.of(new StorageIdentity("other_owner", GROUP), new StorageIdentity(OWNER, "other_group"))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
    StorageIdentity first = new StorageIdentity("an", GROUP);
    StorageIdentity second = new StorageIdentity("c0", GROUP);
    assertEquals(3117, "an".hashCode());
    assertEquals(3117, "c0".hashCode());
    assertEquals(first.hashCode(), second.hashCode());
    assertNotEquals(first, second);
    Map<StorageIdentity, String> values = Map.of(first, "first", second, "second");
    assertEquals("first", values.get(new StorageIdentity("an", GROUP)));
    assertEquals("second", values.get(new StorageIdentity("c0", GROUP)));
  }

  @Test
  void lex004EachOfSixComponentsDefinesRecordIdentityWithoutResolvingTheSyntheticPath() {
    Path[] roots = {
      Path.of("/synthetic/asset"), Path.of("/synthetic/transfer"), Path.of("/synthetic/backup"),
      Path.of("/synthetic/log"), Path.of("/synthetic/artemis"), Path.of("/synthetic/staging")
    };
    StorageRootLayout value = layout(roots);
    StorageRootLayout equal = layout(roots.clone());
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, FIXED_LAYOUT);
    assertEquals(FIXED_LAYOUT, value.toString());
    for (int index = 0; index < roots.length; index++) {
      Path[] changed = roots.clone();
      changed[index] = Path.of("/synthetic/other" + index);
      StorageRootLayout other = layout(changed);
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }

  private static StorageRootLayout layout(Path[] paths) {
    return new StorageRootLayout(paths[0], paths[1], paths[2], paths[3], paths[4], paths[5]);
  }
}
''');subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);tests=[dict(path=old,tests=2),dict(path=new,tests=4)];e=b/'evidence/PG35300-storage-lexical6-source-v1';e.mkdir();inv=ld(r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');owners={n:next(x for x in inv['artifacts'] if x['path']==n)['owner'] for n in mains};assert set(owners.values())=={'WBS-P003-05'};v=dict(actualExit=0,mainSources=mains,testSources=tests,expectedTests=6,newTestDefinitions=4,necessaryPriorDefinitions=2,inputHashes={n:sha(r/n) for n in mains+[x['path'] for x in tests]},unchangedMainAndOriginalLayoutTwo=True,pureJdkLexicalOnly=True,filesystemOrOsAuthorityOperations=0,productOwnerByMainPath=owners,targets=['dev/codex/schubert/nk/storage/'+n for n in ['StorageIdentity','StorageRootLayout']]);(e/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');c=ld(b/'input/4057_ssc439_exception21_profile.json');c.update(id='PG35310-STORAGE-LEXICAL-WHOLE6',productOwnerByMainPath=owners,oracleSpecs=[ref(b/'4377_Storage純識別子・字句root全六仕様.md')],closureProofs=[ref(e/'manifest.json')],mainSources=mains,testSources=tests,expectedTests=6,newTestDefinitions=4,physicalClasses=[n+'.class' for n in v['targets']],targetClasses=v['targets'],pomInputs=['pom.xml','src/schubert-nk-storage/pom.xml'],slots={k:str((b/('evidence/PG'+str(n)+'-storage-lexical6-'+k+'-v1')).relative_to(r)) for k,n in [('prestyle',35302),('prepare',35304),('static',35306),('preflight',35308),('unit',35310),('post',35312)]},privateDirs=dict(prepare='pg35304-storage-lexical6-v1',unit='pg35310-storage-lexical6-v1'));(b/'input/4068_storage_lexical6_profile.json').open('x').write(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=2,tests=6,newDefinitions=4,originalLayout2Unchanged=True)))
