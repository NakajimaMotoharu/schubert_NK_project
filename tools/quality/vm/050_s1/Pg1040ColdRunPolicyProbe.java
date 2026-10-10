package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.util.*;

/** Data-only six-root policy diagnostic; no run Session, mutation, DB, Unit or authority. */
public final class Pg1040ColdRunPolicyProbe {
  static String phase="ENTRY";
  public static void main(String[] args)throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((thread,failure)->
        System.err.println("PG1040_UNCAUGHT type="+failure.getClass().getName()+" diagnosticsRedacted=true"));
    if(args==null||args.length!=0)throw new IllegalArgumentException("fixed readonly diagnostic");
    var privateCalls=LinuxDirectoryCalls.create();var hostCalls=LinuxHostDirectoryCalls.create();
    var security=LinuxInodeSecurity.create();var io=new MaintenanceRunFiles.NioIo();
    var policy=new EnvironmentInodePolicy(security,io);
    var held=new ArrayList<OwnedTransferDirectory>();
    try {
      phase="PRIVATE_VAR";var var=OwnedTransferDirectory.open(privateCalls,Path.of("/var"));held.add(var);
      phase="PRIVATE_LIB";var lib=var.openExistingChild("lib");held.add(lib);
      phase="PRIVATE_APP";var app=lib.openExistingChild("schubert-nk");held.add(app);
      phase="PRIVATE_MAINTENANCE";var maintenance=app.openExistingChild("maintenance");held.add(maintenance);
      phase="PRIVATE_RUNS";var runs=maintenance.openExistingChild("runs");held.add(runs);
      phase="PRIVATE_ATTEMPTS";var attempts=maintenance.openExistingChild("attempts");held.add(attempts);
      var values=new ArrayList<EnvironmentInodePolicy.Snapshot>();
      for(int i=0;i<6;i++) {
        phase="POLICY_PRIVATE_"+i;final boolean shared=i<3;
        final int index=i;
        var value=held.get(i).atDirectory(p->{
          var attributes=io.attributes(p);
          System.out.println("PG1040_NATIVE index="+index+" uid="+attributes.get("uid")+" gid="+attributes.get("gid")
              +" mode="+attributes.get("mode")+" filesystem="+io.filesystem(p)+" readonly="+security.readOnlyFilesystem(p)
              +" aclLength="+security.accessAcl(p,44).length);
          return shared?policy.durableAncestor(p,true):policy.durable(p,true,0);
        });
        values.add(value);
        System.out.println("PG1040_POLICY privateIndex="+i+" filesystem="+value.filesystem()+" readonly="+value.readonly());
      }
      phase="HOST_VAR";var hostVar=OwnedTransferDirectory.open(hostCalls,Path.of("/var"));held.add(hostVar);
      phase="HOST_LIB";var hostLib=hostVar.openExistingChild("lib");held.add(hostLib);
      phase="HOST_APP";var hostApp=hostLib.openExistingChild("schubert-nk");held.add(hostApp);
      for(int i=0;i<3;i++) {
        phase="POLICY_HOST_"+i;var value=held.get(6+i).atDirectory(policy::durableAncestor);
        var privateValue=values.get(i);
        if(!value.metadata().equals(privateValue.metadata())||!value.filesystem().equals(privateValue.filesystem()))throw new IllegalStateException("fixed host-private mismatch");
        System.out.println("PG1040_POLICY hostIndex="+i+" sameMetadataFilesystem=true");
      }
      System.out.println("PG1040_POLICY_DONE sixRootPolicy=true graphNotInspected=true runAuthority=false");
    }catch(Exception|Error failure) {
      System.err.println("PG1040_REFUSED phase="+phase+" type="+failure.getClass().getName()+" diagnosticsRedacted=true");
      throw new IllegalStateException("fixed readonly probe refused");
    }finally {
      for(int i=held.size()-1;i>=0;i--)held.get(i).close();
    }
  }
}
