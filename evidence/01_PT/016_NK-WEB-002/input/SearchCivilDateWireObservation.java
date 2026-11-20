import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

/** PT-NTF-HTTP003/PT-QRY-HTTP003, date-only inputs on the isolated form-to-wire boundary. */
public final class SearchCivilDateWireObservation {
  private SearchCivilDateWireObservation() {}

  public static void main(String[] args) {
    int mismatches = 0;
    mismatches += check("CIVIL-WIRE-001", "0001-01-01", "00010101000000000", "00010101235959999");
    mismatches += check("CIVIL-WIRE-002", "2024-02-29", "20240229000000000", "20240229235959999");
    if (mismatches != 0) System.exit(1);
  }

  private static int check(String test, String day, String expectedFrom, String expectedTo) {
    var input = Map.of("from", List.of(day), "to", List.of(day));
    var notifications = NotificationSearchForm.bind(input);
    var questions = QuestionSearchForm.bind(input, UserRole.USER);
    if (!notifications.isValid() || !questions.isValid()) {
      throw new IllegalStateException("An in-range Gregorian calendar day did not bind");
    }
    return compare(test, "NTSREQ01", notifications.toRequest(), 12, expectedFrom, expectedTo)
        + compare(test, "QSSREQ01", questions.toRequest(), 332, expectedFrom, expectedTo);
  }

  private static int compare(
      String test,
      String layout,
      PayloadData request,
      int offset,
      String expectedFrom,
      String expectedTo) {
    var values = new TypedPayloadValues(new LayoutId(layout), request, List.of());
    var payload = PayloadCodec.standard().encode(PayloadTypeCatalog.encode(values), false);
    var bytes = payload.copyData();
    String from = new String(bytes, offset, 17, StandardCharsets.US_ASCII);
    String to = new String(bytes, offset + 17, 17, StandardCharsets.US_ASCII);
    boolean same = expectedFrom.equals(from) && expectedTo.equals(to);
    System.out.printf(
        "%s\t%s\t%s\t%s\t%s\t%s\t%s%n",
        test, layout, expectedFrom, from, expectedTo, to, same ? "PASS" : "FAIL");
    return same ? 0 : 1;
  }
}
