package dev.codex.schubert.nk.batch.file;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/** Isolated public zero-byte marker fixtures, synthetic Root metadata; no VM authority. */
public final class BackupInterruptedStartRecoveryTest {
  private static int assertions;
  private static void check(boolean value) { if(!value)throw new AssertionError("literal marker oracle differs");assertions++; }
  private static BackupPublicationFixture fixture(Path temp)throws Exception {
    var f=new BackupPublicationFixture(temp);
    f.metadata=(role,m)->{m.put("uid",0);m.put("gid",0);};
    Files.createFile(f.parent.resolve("backup-start.intent"));
    Files.setPosixFilePermissions(f.parent.resolve("backup-start.intent"),java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    Files.writeString(f.parent.resolve("backup-request"),"PUBLIC_OLD_REQUEST_NOT_AUTHORITY\n");
    return f;
  }
  private static void retained(BackupPublicationFixture f)throws Exception {
    check(Files.readString(f.parent.resolve("backup-request")).equals("PUBLIC_OLD_REQUEST_NOT_AUTHORITY\n"));
    f.root.atDirectory(p->{check(Files.isDirectory(p));return Boolean.TRUE;});
  }
  public static void main(String[] args)throws Exception {
    Path temp=Files.createTempDirectory("pg480-marker-oracle-");
    try(var f=fixture(temp)) {
      var inside=new ArrayList<Boolean>();
      BackupInterruptedStartRecovery.retire(f.root,f,f,p->{
        boolean present=Files.exists(f.parent.resolve("backup-start.intent"));
        if(p==BackupInterruptedStartRecovery.Phase.BEFORE_RETIRE && !present)throw new IOException("literal before must be present");
        if(p==BackupInterruptedStartRecovery.Phase.RETIRED && present)throw new IOException("literal after must be absent");
        if(p.name().equals("RETIRING"))inside.add(present);
      });
      check(inside.contains(true) && inside.contains(false));
      check(inside.get(0) && !inside.get(inside.size()-1));retained(f);
    }
    try(var f=fixture(temp)) {
      var phases=new ArrayList<BackupInterruptedStartRecovery.Phase>();
      BackupInterruptedStartRecovery.retire(f.root,f,f,phases::add);
      check(!Files.exists(f.parent.resolve("backup-start.intent")));
      check(phases.get(0)==BackupInterruptedStartRecovery.Phase.OBSERVING);
      check(phases.contains(BackupInterruptedStartRecovery.Phase.BEFORE_RETIRE));
      check(phases.get(phases.size()-1)==BackupInterruptedStartRecovery.Phase.RETIRED);
      retained(f);
      BackupInterruptedStartRecovery.quarantine(f.root,f,f,p->{});
      check(Files.readAllBytes(f.parent.resolve("backup-start.intent")).length==0);
      long ino=(Long)Files.getAttribute(f.parent.resolve("backup-start.intent"),"unix:ino");
      BackupInterruptedStartRecovery.quarantine(f.root,f,f,p->{});
      check((Long)Files.getAttribute(f.parent.resolve("backup-start.intent"),"unix:ino")==ino);
      retained(f);
    }
    for(var failing:List.of(BackupInterruptedStartRecovery.Phase.OBSERVING,BackupInterruptedStartRecovery.Phase.BEFORE_RETIRE,BackupInterruptedStartRecovery.Phase.RETIRING,BackupInterruptedStartRecovery.Phase.RETIRED)) {
      try(var f=fixture(temp)) {
        IOException primary=new IOException("fixed failure");
        try { BackupInterruptedStartRecovery.retire(f.root,f,f,p->{if(p==failing)throw primary;});throw new AssertionError("failure returned success"); }
        catch(IOException actual){check(actual==primary);}
        check(Files.readAllBytes(f.parent.resolve("backup-start.intent")).length==0);retained(f);
      }
    }
    for(Throwable primary:List.of(new IOException("fixed io"),new IllegalStateException("fixed unchecked"),new AssertionError("fixed fatal"))) {
      try(var f=fixture(temp)) {
        var phases=new ArrayList<BackupInterruptedStartRecovery.Phase>();
        try {
          BackupInterruptedStartRecovery.retire(f.root,f,f,p->{phases.add(p);if(p==BackupInterruptedStartRecovery.Phase.RETIRED){
            if(primary instanceof IOException e)throw e;if(primary instanceof RuntimeException e)throw e;throw (Error)primary;
          }});throw new AssertionError("failure returned success");
        }catch(IOException|RuntimeException|Error actual){check(actual==primary);}
        check(phases.contains(BackupInterruptedStartRecovery.Phase.REISOLATING));
        check(phases.contains(BackupInterruptedStartRecovery.Phase.QUARANTINED));
        check(Files.readAllBytes(f.parent.resolve("backup-start.intent")).length==0);retained(f);
      }
    }
    for(boolean same:List.of(false,true)) {
      try(var f=fixture(temp)) {
        IOException primary=new IOException("fixed primary"),secondary=same?primary:new IOException("fixed secondary");
        try { BackupInterruptedStartRecovery.retire(f.root,f,f,p->{if(p==BackupInterruptedStartRecovery.Phase.RETIRED)throw primary;if(p==BackupInterruptedStartRecovery.Phase.REISOLATING)throw secondary;});throw new AssertionError("unknown succeeded"); }
        catch(IOException actual){check(actual==primary);check(actual.getSuppressed().length==(same?0:1));if(!same)check(actual.getSuppressed()[0]==secondary);}
        retained(f); // Missing quarantine is NOT success; caller must keep M/A.
      }
    }
    for(String invalid:List.of("nonempty","symlink","missing","mode")) {
      try(var f=fixture(temp)) {
        Path marker=f.parent.resolve("backup-start.intent");
        switch(invalid){case "nonempty"->Files.writeString(marker,"x");case "symlink"->{Files.delete(marker);Files.createSymbolicLink(marker,Path.of("backup-request"));}case "missing"->Files.delete(marker);case "mode"->Files.setPosixFilePermissions(marker,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r-----"));default->throw new AssertionError();}
        try{BackupInterruptedStartRecovery.retire(f.root,f,f,p->{});throw new AssertionError("invalid admitted");}catch(IOException refused){assertions++;}
        retained(f);
      }
    }
    for(String operation:List.of("unlink","sync")) {
      try(var f=fixture(temp)) {
        f.faults.put(operation+"#1",new IOException("fixed IO fault"));
        try { BackupInterruptedStartRecovery.retire(f.root,f,f,p->{});throw new AssertionError("IO fault succeeded"); }
        catch(IOException refused){assertions++;}
        check(Files.readAllBytes(f.parent.resolve("backup-start.intent")).length==0);retained(f);
      }
    }
    try(var f=fixture(temp)) {
      f.faults.put("sync#1",new IOException("fixed IO fault"));
      f.faults.put("sync#2",new IOException("fixed secondary fault"));
      try { BackupInterruptedStartRecovery.retire(f.root,f,f,p->{});throw new AssertionError("partial re-isolation succeeded"); }
      catch(IOException refused){check(refused.getSuppressed().length==1);}
      retained(f);
    }
    try(var f=fixture(temp)) {
      for(int argument=0;argument<4;argument++) {
        try { BackupInterruptedStartRecovery.retire(argument==0?null:f.root,argument==1?null:f,argument==2?null:f,argument==3?null:p->{});throw new AssertionError("null admitted"); }
        catch(NullPointerException rejected){assertions++;}
        try { BackupInterruptedStartRecovery.quarantine(argument==0?null:f.root,argument==1?null:f,argument==2?null:f,argument==3?null:p->{});throw new AssertionError("null admitted"); }
        catch(NullPointerException rejected){assertions++;}
      }
      for(int argument=0;argument<3;argument++) {
        try { BackupInterruptedStartRecovery.retire(argument==0?null:f.root,argument==1?null:f,argument==2?null:p->{});throw new AssertionError("public null admitted"); }
        catch(NullPointerException rejected){assertions++;}
        try { BackupInterruptedStartRecovery.quarantine(argument==0?null:f.root,argument==1?null:f,argument==2?null:p->{});throw new AssertionError("public null admitted"); }
        catch(NullPointerException rejected){assertions++;}
      }
      check(Files.readAllBytes(f.parent.resolve("backup-start.intent")).length==0);retained(f);
    }
    System.out.println("PG480_MARKER_ORACLE assertions="+assertions+" actual0=true productionPT0=true vmMutation0=true");
  }
}
