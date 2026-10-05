package dev.codex.schubert.characterization;
public final class NativeNkL01Capture471OracleTest {
  public static void main(String[] args) {
    String[] valid={"/home/mini/codex/project1/work/pgpt-runs/PG379/pg471-l01-v1","717d72dd844fff286b4c696b9d08c41b136f0a6c","/home/mini/codex/project1/work/pgpt-vm/private/pg468-active-account.private.json"};
    int count=1;if(!NativeNkL01Capture471.arguments(valid))throw new AssertionError("literal candidate rejected");
    for(String[] bad:new String[][]{null,new String[]{},new String[]{"x"},new String[]{"x","y"},new String[]{valid[0],valid[1],valid[2],"extra"}}){if(NativeNkL01Capture471.arguments(bad))throw new AssertionError("shape accepted");count++;}
    for(int n=0;n<3;n++)for(String value:new String[]{null,"","foreign",valid[n]+"/.."}){var bad=valid.clone();bad[n]=value;if(NativeNkL01Capture471.arguments(bad))throw new AssertionError("binding accepted");count++;}
    var old=valid.clone();old[1]="bbb244e5191e68adee2f6251dfdbbba53e9b64b4";if(NativeNkL01Capture471.arguments(old))throw new AssertionError("old source accepted");count++;
    System.out.println("PG471_L01_ORACLE independentAssertions="+count+" nativeMutation0=true productionPT0=true");
  }
}
