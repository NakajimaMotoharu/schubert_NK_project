package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;

/** Data-only SDK graph probe under fixed retained administrator exclusion.
 * Host DirectoryCalls refuses every mutation; writer/UUID supplier also refuse.
 * This observer has no run/epoch/start authorization and never obtains a DB.
 */
public final class Pg1042ColdReadonlyGraphProbe {
  static String phase="ENTRY";
  static int reads,names;
  static final class ReadonlyLocal implements DirectoryCalls {
    final DirectoryCalls actual=LinuxDirectoryCalls.create();
    @Override public int openRoot()throws StorageIoException{return actual.openRoot();}
    @Override public int openDirectory(int parent,String name)throws StorageIoException{return actual.openDirectory(parent,name);}
    @Override public int openEntry(int parent,String name)throws StorageIoException{return actual.openEntry(parent,name);}
    @Override public void close(int descriptor)throws StorageIoException{actual.close(descriptor);}
    @Override public int createFile(int parent,String name)throws StorageIoException{throw denied();}
    @Override public void createDirectory(int parent,String name)throws StorageIoException{throw denied();}
    @Override public void publish(int directory,String part,String ready)throws StorageIoException{throw denied();}
    @Override public void unlink(int directory,String name)throws StorageIoException{throw denied();}
    @Override public void sync(int directory)throws StorageIoException{throw denied();}
    static StorageIoException denied(){return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);}
  }
  static final class TraceIo implements MaintenanceRunFiles.Io {
    final MaintenanceRunFiles.NioIo actual=new MaintenanceRunFiles.NioIo();
    @Override public Map<String,Object> attributes(Path path)throws IOException {
      phase="ATTRIBUTES";return actual.attributes(path);
    }
    @Override public String filesystem(Path path)throws IOException {
      phase="FILESYSTEM";return actual.filesystem(path);
    }
    @Override public SeekableByteChannel open(Path path)throws IOException {
      phase="FILE_READ";reads++;return actual.open(path);
    }
    @Override public DirectoryStream<Path> openNames(Path path)throws IOException {
      phase="DIRECTORY_NAMES";names++;return actual.openNames(path);
    }
    @Override public InspectorEnvironmentPublisher.Writer openWriter(Path path)throws IOException {
      throw new IOException("readonly diagnostic mutation refused");
    }
  }
  public static void main(String[] args)throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((thread,failure)->
        System.err.println("PG1042_UNCAUGHT type="+failure.getClass().getName()+" diagnosticsRedacted=true"));
    if(args==null||args.length!=1||!"local".equals(args[0]))throw new IllegalArgumentException("fixed readonly diagnostic");
    var security=LinuxInodeSecurity.create();var io=new TraceIo();
    var readonly=new MaintenanceRunFiles(Path.of("/var"),new ReadonlyLocal(),security,io,
        ()->{throw new AssertionError("readonly diagnostic UUID refused");},
        ()->MessageDigest.getInstance("SHA-256"),Optional.of(LinuxHostDirectoryCalls.create()));
    var expected=new MaintenanceActivation(new BatchRun(UUID.fromString("eeae04ea-713c-4f2d-888d-358fb4bed274"),
        Instant.parse("2026-10-09T23:31:22.087768Z")),UUID.fromString("091663ce-1cf4-47e7-8311-218ebb0c8653"));
    try {
      readonly.execute(session->{
        System.out.println("PG1042_CALLBACK_ENTERED namespace=true runAuthority=false");
        session.verifyRetained();
        System.out.println("PG1042_RETAINED namespace=true runAuthority=false");
        phase="STARTUP_GRAPH";var first=session.observeStartup(expected);
        if(!first.equals(session.observeStartup(expected))||first.completed().isEmpty())throw new IOException("fixed original graph refused");
        var done=first.completed().orElseThrow();
        if(done.outcome()!=MaintenanceCompletion.Outcome.SUCCESS||!done.endedAt().equals(Instant.parse("2026-10-09T23:56:48.112404Z")))throw new IOException("fixed completion refused");
        System.out.println("PG1042_GRAPH originalCompleted=true twoRead=true runAuthority=false");
        return Boolean.TRUE;
      });
      System.out.println("PG1042_DONE allScopesNormal=true runAuthority=false reads="+reads+" nameScopes="+names);
    }catch(Exception|Error failure) {
      System.err.println("PG1042_REFUSED phase="+phase+" type="+failure.getClass().getName()+" reads="+reads+" nameScopes="+names+" diagnosticsRedacted=true");
      throw new IllegalStateException("fixed readonly probe refused");
    }
  }
}
