package dev.codex.schubert.nk.api.database;

import java.util.List;

/**
 * Independent approved test oracle, never generated from production files or observed DB values.
 * NK-DAT-001; SS331/PG162; BUG175/YKT136; DB258 and 12 existing migration PT classes.
 */
public final class MigrationInventory {
  public static final List<String> VERSIONS =
      List.of(
          "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013",
          "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024", "025", "026",
          "027", "028", "029");
  public static final String CSV = String.join(",", VERSIONS);
  public static final String COUNT_TEXT = Integer.toString(VERSIONS.size());

  private MigrationInventory() {}
}
