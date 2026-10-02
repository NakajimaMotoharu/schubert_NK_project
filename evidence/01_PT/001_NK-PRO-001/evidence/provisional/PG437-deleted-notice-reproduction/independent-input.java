import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import java.time.Instant;
import java.util.*;

/** BUG562 independent input/expected rejection; diagnostic only, not coverage or formal PT. */
class Pg437DeletedNoticeProbe {
  public static void main(String[] args) {
    var at = Instant.parse("2026-10-03T00:00:00Z");
    var layout = new LayoutId("NTDRSP01");
    var bad = new NotificationDetailResponseData(new NotificationId(1),
        "0123456789ABCDEFGHJKMNPQRS", NotificationType.COMPLETED,
        NotificationState.COMPLETED, at, Optional.of(at), Optional.of(at),
        Optional.empty(), Optional.empty(), true, Optional.empty(),
        Optional.of("independent deleted answer must be rejected"), Optional.empty(),
        Optional.empty(), Optional.empty());
    PayloadSemanticValidator.validate(new TypedPayloadValues(layout, bad, List.of()));
    System.out.println("BUG562 semantic: accepted invalid deleted answer (expected rejection)");
    var wire = PayloadCodec.standard().encode(new PayloadValues(layout, bad.fields(), List.of()), ResultCode.SUCCESS);
    System.out.println("BUG562 encode: accepted invalid deleted answer (expected rejection)");
    PayloadCodec.standard().decode(layout, wire.copyData(), List.of(), ResultCode.SUCCESS);
    System.out.println("BUG562 decode: accepted invalid deleted answer (expected rejection)");
  }
}
