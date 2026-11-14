"""BUG2881 isolated local vendor-copy reproduction; no actual project test, remote job or oracle change."""
from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path.cwd();tc=r.parent/'toolchain';b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379/pg30738-maven-resource-epoch-repro';e=b/'evidence/PG30738-maven-resource-epoch-independent-reproduction-v1';assert not w.exists() and not e.exists();w.mkdir(mode=0o700);e.mkdir();jar=tc/'m2/repository/org/apache/maven/shared/maven-filtering/3.3.1/maven-filtering-3.3.1.jar';assert jar.is_file();code='''import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import org.apache.maven.shared.filtering.FilteringUtils;
public final class ResourceEpochProbe {
  public static void main(String[] args) throws Exception {
    Path root = Path.of(args[0]);
    Files.createDirectory(root);
    Path input = root.resolve("literal.json");
    Files.writeString(input, "{\\"independent\\":\\"VALUE\\"}", StandardCharsets.UTF_8);
    Files.setLastModifiedTime(input, FileTime.fromMillis(0));
    Path zero = root.resolve("missing-zero.json");
    FilteringUtils.copyFile(input.toFile(), zero.toFile(), "UTF-8", null, false);
    if (Files.exists(zero)) throw new AssertionError("epoch-zero behavior not reproduced");
    Files.setLastModifiedTime(input, FileTime.fromMillis(1700000000000L));
    Path positive = root.resolve("positive.json");
    FilteringUtils.copyFile(input.toFile(), positive.toFile(), "UTF-8", null, false);
    if (!Files.readString(positive, StandardCharsets.UTF_8).equals("{\\"independent\\":\\"VALUE\\"}"))
      throw new AssertionError("positive timestamp must copy literal bytes");
    System.out.println("EPOCH_ZERO_MISSING_REPRODUCED; POSITIVE_TIMESTAMP_LITERAL_COPY_OK");
  }
}
''';p=w/'ResourceEpochProbe.java';p.write_text(code);(e/'ResourceEpochProbe.java.txt').write_text(code);command=[str(tc/'jdk-25.0.4/bin/java'),'--class-path',str(jar),str(p),str(w/'synthetic-fixture')]
with (e/'probe.stdout').open('xb') as out,(e/'probe.stderr').open('xb') as err:result=subprocess.run(command,stdout=out,stderr=err,timeout=60,check=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=dict(actualExit=result.returncode,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),bug='BUG-2881',command=command,vendorJarSha256=sha(jar),fixtureSourceSha256=sha(p),positiveValueExpected='literal independent VALUE JSON',productTestsExecuted=0,remoteConnections=0,actualDbRootVmNativeKeyActions=0,sourceAndTestOraclesChanged=False,formalAccepted=False);(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=result.returncode,probeOutput=(e/'probe.stdout').read_text().strip(),productTestsExecuted=0)));assert result.returncode==0
