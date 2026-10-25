package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.api.security.AuthSessionRevocationService;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.api.security.PasswordHasher;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** UI236 literal offsets and independent SS323 §9.3 LP/JCE oracle; PT-ADM-024..027. */
class UserMutationRequestTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;
  static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  static final AuthenticatedActor ACTOR = new AuthenticatedActor(1, "u1", Role.ADMIN);
  static final UUID TOKEN = new UUID(60, 1);
  static final UUID MESSAGE = new UUID(70, 1);
  static final String PASSWORD = "Synthetic-12";
  static final List<String> LAYOUTS =
      List.of("UCRREQ01", "USTREQ01", "URLREQ01", "UPWREQ01", "ULKREQ01");
  static UserCommandService commands;

  record Field(String name, String type, String value) {}

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    commands =
        new UserCommandService(
            new PasswordHasher(), new AuthSessionRevocationService(new ContextHash()));
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  void adm024DecodeAndCanonicalMatchIndependentWireAndHmac() throws Exception {
    for (String layout : LAYOUTS)
      for (boolean positive : new boolean[] {false, true})
        for (long version : new long[] {0, 999_999_999}) {
          byte[] bytes = data(layout, 3, version, positive, "New.User", PASSWORD, TOKEN);
          var wire = message(layout, bytes, MESSAGE);
          try (var request = UserMutationRequest.decode(wire)) {
            Arrays.fill(bytes, (byte) 0);
            assertSame(wire.header(), request.header());
            assertEquals(TOKEN, request.operationToken());
            assertEquals(layout.replace("REQ", "RSP"), request.responseLayoutId().value());
            assertEquals(kind(layout, positive), request.mutation());
            assertEquals(
                layout.equals("UCRREQ01") ? OptionalLong.empty() : OptionalLong.of(3),
                request.targetUserId());
            List<Field> fields =
                fields(layout, version, positive, "New.User", "new.user", PASSWORD);
            check(
                request, ACTOR, layout.equals("UCRREQ01") ? "NEW_USER:new.user" : "USER:3", fields);
          }
        }
    // Role and Enabled are independent fields, not correlated alternatives.
    for (boolean role : new boolean[] {false, true})
      for (boolean enabled : new boolean[] {false, true}) {
        byte[] bytes = data("UCRREQ01", 3, 0, role, "New", PASSWORD, TOKEN);
        bytes[325] = (byte) (enabled ? '1' : '0');
        var expected = new ArrayList<>(fields("UCRREQ01", 0, role, "New", "new", PASSWORD));
        expected.set(4, new Field("enabled", "B1", enabled ? "1" : "0"));
        try (var request = UserMutationRequest.decode(message("UCRREQ01", bytes, MESSAGE))) {
          check(request, ACTOR, "NEW_USER:new", expected);
        }
      }
    for (String layout : List.of("USTREQ01", "URLREQ01", "UPWREQ01", "ULKREQ01"))
      for (long id : new long[] {1, 999_999_999_999L}) {
        try (var request =
            UserMutationRequest.decode(
                message(layout, data(layout, id, 0, true, "New", PASSWORD, TOKEN), MESSAGE))) {
          assertEquals(OptionalLong.of(id), request.targetUserId());
          check(request, ACTOR, "USER:" + id, fields(layout, 0, true, "New", "new", PASSWORD));
        }
      }
    for (String layout : List.of("UCRREQ01", "UPWREQ01")) {
      try (var request =
          UserMutationRequest.decode(
              message(layout, data(layout, 3, 0, true, "New", "é".repeat(128), TOKEN), MESSAGE))) {
        check(
            request,
            ACTOR,
            layout.equals("UCRREQ01") ? "NEW_USER:new" : "USER:3",
            fields(layout, 0, true, "New", "new", "é".repeat(128)));
      }
    }
    // Distinct header, token and sentAt are excluded; exact original username remains included.
    try (var first =
            UserMutationRequest.decode(
                message(
                    "UCRREQ01", data("UCRREQ01", 3, 0, true, "New", PASSWORD, TOKEN), MESSAGE));
        var second =
            UserMutationRequest.decode(
                message(
                    "UCRREQ01",
                    data("UCRREQ01", 3, 0, true, "New", PASSWORD, new UUID(60, 2)),
                    new UUID(70, 2)));
        var different =
            UserMutationRequest.decode(
                message(
                    "UCRREQ01", data("UCRREQ01", 3, 0, true, "NEW", PASSWORD, TOKEN), MESSAGE));
        var a = first.canonical(ACTOR);
        var b = second.canonical(ACTOR);
        var c = different.canonical(ACTOR);
        var keys = keys()) {
      assertArrayEquals(keys.calculate(a).digest(), keys.calculate(b).digest());
      assertFalse(Arrays.equals(keys.calculate(a).digest(), keys.calculate(c).digest()));
      assertEquals(a.target(), c.target());
      try (var otherOwner = first.canonical(new AuthenticatedActor(2, "u2", Role.ADMIN))) {
        assertFalse(Arrays.equals(keys.calculate(a).digest(), keys.calculate(otherOwner).digest()));
      }
    }
  }

  @Test
  void adm025DispatchUsesTheSameDecodedFieldsInRealTransactions() throws Exception {
    for (String layout : LAYOUTS)
      for (boolean positive : new boolean[] {false, true}) {
        seed();
        if (layout.equals("ULKREQ01"))
          sql(
              "update schubert.app_users set failed_count=5,locked_until='2026-09-08T00:02:00Z' where id=3");
        try (var request =
                UserMutationRequest.decode(
                    message(
                        layout, data(layout, 3, 0, positive, "New", PASSWORD, TOKEN), MESSAGE));
            var c = database.transaction()) {
          var actor =
              new AdminCommandAuthenticator(new ContextHash())
                  .verify(
                      c,
                      request.header().authenticationContext().orElseThrow(),
                      request.mutation(),
                      request.targetUserId(),
                      NOW);
          // canonical is independent of the consumed command password clone.
          try (var before = request.canonical(actor);
              var keys = keys()) {
            byte[] fingerprint = keys.calculate(before).digest();
            var result =
                request.apply(commands, c, actor, new UserCommandMetadata(MESSAGE, MESSAGE, NOW));
            assertEquals(ResultCode.SUCCESS, result.resultCode());
            assertEquals(
                layout.equals("UCRREQ01") ? 4 : 3, result.data().orElseThrow().userId().value());
            assertEquals(
                layout.equals("UCRREQ01") ? 0 : 1, result.data().orElseThrow().updatedVersion());
            try (var after = request.canonical(actor)) {
              assertArrayEquals(fingerprint, keys.calculate(after).digest());
            }
          }
          assertFalse(c.isClosed());
          assertFalse(c.getAutoCommit());
          c.commit();
        }
        long target = layout.equals("UCRREQ01") ? 4 : 3;
        try (var c = database.api();
            var s =
                c.prepareStatement(
                    "select role,status,failed_count,password_hash,version,updated_by,updated_at from schubert.app_users where id=?")) {
          s.setLong(1, target);
          try (var r = s.executeQuery()) {
            assertTrue(r.next());
            assertEquals(
                (layout.equals("UCRREQ01") || layout.equals("URLREQ01")) && positive
                    ? "ADMIN"
                    : "USER",
                r.getString("role"));
            assertEquals(
                (layout.equals("UCRREQ01") || layout.equals("USTREQ01")) && !positive
                    ? "DISABLED"
                    : "ACTIVE",
                r.getString("status"));
            assertEquals(0, r.getInt("failed_count"));
            assertEquals(1, r.getLong("updated_by"));
            assertEquals(
                NOW, r.getObject("updated_at", java.time.OffsetDateTime.class).toInstant());
            if (layout.equals("UCRREQ01") || layout.equals("UPWREQ01"))
              UserCommandServiceTest.independentHash(r.getString("password_hash"), PASSWORD);
            else assertEquals("unusable-test-hash", r.getString("password_hash"));
            assertFalse(r.next());
          }
        }
        assertEquals(
            layout.equals("UCRREQ01") || layout.equals("ULKREQ01") ? 0 : 1,
            count("select count(*) from schubert.auth_sessions where user_id=3 and revoked"));
      }
    seed();
    for (String name : List.of("u1", "U1")) {
      try (var request =
              UserMutationRequest.decode(
                  message(
                      "UCRREQ01", data("UCRREQ01", 3, 0, true, name, PASSWORD, TOKEN), MESSAGE));
          var c = database.transaction()) {
        var actor =
            new AdminCommandAuthenticator(new ContextHash())
                .verify(
                    c,
                    request.header().authenticationContext().orElseThrow(),
                    request.mutation(),
                    request.targetUserId(),
                    NOW);
        var result =
            request.apply(commands, c, actor, new UserCommandMetadata(MESSAGE, MESSAGE, NOW));
        assertEquals(ResultCode.CONFLICT, result.resultCode());
        c.commit();
      }
    }
    assertEquals(2, count("select count(*) from schubert.app_users"));
    // UPW's target username is known only in the database; this remains a business 0100.
    sql(
        "update schubert.app_users set username='TargetUser12',username_key='targetuser12' where id=3");
    try (var request =
            UserMutationRequest.decode(
                message(
                    "UPWREQ01",
                    data("UPWREQ01", 3, 0, true, "unused", "targetuser12", TOKEN),
                    MESSAGE));
        var c = database.transaction()) {
      var actor =
          new AdminCommandAuthenticator(new ContextHash())
              .verify(
                  c,
                  request.header().authenticationContext().orElseThrow(),
                  request.mutation(),
                  request.targetUserId(),
                  NOW);
      assertEquals(
          ResultCode.VALIDATION_ERROR, request.apply(commands, c, actor, metadata()).resultCode());
      c.commit();
    }
    assertEquals(
        1,
        count(
            "select count(*) from schubert.app_users where id=3 and version=0 and password_hash='unusable-test-hash'"));
  }

  @Test
  void adm026MalformedNullAndClosedRequestsFailWithoutSecretLeak() throws Exception {
    assertThrows(NullPointerException.class, () -> UserMutationRequest.decode(null));
    for (String layout : LAYOUTS) {
      byte[] bytes = data(layout, 3, 0, true, "New", PASSWORD, TOKEN);
      for (int length : new int[] {bytes.length - 1, bytes.length + 1})
        invalid(message(layout, Arrays.copyOf(bytes, length), MESSAGE));
      byte[] padding = bytes.clone();
      padding[padding.length - 1] = 'X';
      invalid(message(layout, padding, MESSAGE));
      int token =
          switch (layout) {
            case "UCRREQ01" -> 326;
            case "USTREQ01" -> 22;
            case "URLREQ01" -> 26;
            case "UPWREQ01" -> 277;
            case "ULKREQ01" -> 21;
            default -> throw new AssertionError();
          };
      byte[] badToken = bytes.clone();
      badToken[token] = 'Z';
      invalid(message(layout, badToken, MESSAGE));
      var request = UserMutationRequest.decode(message(layout, bytes, MESSAGE));
      try (var c = database.transaction()) {
        // Security memory observation only, not a private-method/coverage shortcut. Keep the
        // production secret private: verify the same owned array is zero after public close.
        var ownedPassword = UserMutationRequest.class.getDeclaredField("password");
        ownedPassword.setAccessible(true);
        char[] memory = (char[]) ownedPassword.get(request);
        assertArrayEquals(
            (layout.equals("UCRREQ01") || layout.equals("UPWREQ01") ? PASSWORD : "").toCharArray(),
            memory);
        assertEquals("UserMutationRequest[REDACTED]", request.toString());
        assertThrows(NullPointerException.class, () -> request.canonical(null));
        for (Executable call :
            List.<Executable>of(
                () -> request.apply(null, c, ACTOR, metadata()),
                () -> request.apply(commands, null, ACTOR, metadata()),
                () -> request.apply(commands, c, null, metadata()),
                () -> request.apply(commands, c, ACTOR, null)))
          assertThrows(NullPointerException.class, call);
        var canonical = request.canonical(ACTOR);
        byte[] retained = canonical.fields().getFirst().value();
        c.setReadOnly(true);
        assertThrows(
            TemporaryInfrastructureException.class,
            () -> request.apply(commands, c, ACTOR, metadata()));
        c.rollback();
        // A failed command consumed a clone, not the request-owned fingerprint input.
        assertArrayEquals(
            (layout.equals("UCRREQ01") || layout.equals("UPWREQ01") ? PASSWORD : "").toCharArray(),
            memory);
        request.close();
        request.close();
        assertArrayEquals(new char[memory.length], memory);
        assertArrayEquals(retained, canonical.fields().getFirst().value());
        canonical.close();
        for (var field : canonical.fields())
          assertArrayEquals(new byte[field.value().length], field.value());
        for (Executable call :
            List.<Executable>of(
                request::header,
                request::mutation,
                request::targetUserId,
                request::operationToken,
                request::responseLayoutId,
                () -> request.canonical(ACTOR),
                () -> request.apply(commands, c, ACTOR, metadata()))) {
          var failure = assertThrows(IllegalStateException.class, call);
          assertFalse(failure.toString().contains(PASSWORD));
          assertNull(failure.getCause());
        }
      } finally {
        request.close();
      }
    }
    invalid(message("GAMREQ01", new byte[0], MESSAGE));
    for (String name : List.of(" New", "bad/name", "é"))
      invalid(message("UCRREQ01", data("UCRREQ01", 3, 0, true, name, PASSWORD, TOKEN), MESSAGE));
    for (String layout : List.of("UCRREQ01", "UPWREQ01"))
      for (String password : List.of("short", "x".repeat(129)))
        invalid(message(layout, data(layout, 3, 0, true, "New", password, TOKEN), MESSAGE));
    for (String layout : List.of("UCRREQ01", "USTREQ01")) {
      byte[] bytes = data(layout, 3, 0, true, "New", PASSWORD, TOKEN);
      bytes[layout.equals("UCRREQ01") ? 325 : 12] = '2';
      invalid(message(layout, bytes, MESSAGE));
    }
    for (String layout : List.of("UCRREQ01", "URLREQ01")) {
      byte[] bytes = data(layout, 3, 0, true, "New", PASSWORD, TOKEN);
      put(bytes, layout.equals("UCRREQ01") ? 320 : 12, "OTHER");
      invalid(message(layout, bytes, MESSAGE));
    }
    for (String layout : List.of("USTREQ01", "URLREQ01", "UPWREQ01", "ULKREQ01"))
      invalid(message(layout, data(layout, 0, 0, true, "New", PASSWORD, TOKEN), MESSAGE));
    byte[] nonNfc = data("UPWREQ01", 3, 0, true, "New", "e\u0301".repeat(12), TOKEN);
    invalid(message("UPWREQ01", nonNfc, MESSAGE));
    byte[] data = data("USTREQ01", 3, 0, true, "New", PASSWORD, TOKEN);
    var response =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("USTREQ01"),
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            MESSAGE,
            MESSAGE,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            60,
            0,
            0,
            316,
            Optional.of(ResultCode.SUCCESS));
    invalid(new WireMessage<>(response, new FixedPayload(data, 0, List.of())));
    var records =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("USTREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            MESSAGE,
            MESSAGE,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            60,
            1,
            1,
            317,
            Optional.empty());
    invalid(new WireMessage<>(records, new FixedPayload(data, 1, List.of(new byte[] {0}))));
  }

  @Test
  void adm027ConcurrentIndependentRequestsNeverShareIdentityOrBuffers() throws Exception {
    try (var pool = Executors.newFixedThreadPool(10)) {
      List<Future<String>> jobs = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        int number = i;
        jobs.add(
            pool.submit(
                () -> {
                  String layout = LAYOUTS.get(number % 5);
                  String name = "new" + number;
                  String password = "Synthetic-" + number + "-value";
                  long target = number + 1;
                  boolean flag = number % 2 == 0;
                  var actor = new AuthenticatedActor(number + 1, "actor" + number, Role.ADMIN);
                  try (var request =
                          UserMutationRequest.decode(
                              message(
                                  layout,
                                  data(
                                      layout,
                                      target,
                                      number,
                                      flag,
                                      name,
                                      password,
                                      new UUID(60, number + 1)),
                                  new UUID(70, number + 1)));
                      var canonical = request.canonical(actor);
                      var keys = keys()) {
                    check(
                        request,
                        actor,
                        layout.equals("UCRREQ01") ? "NEW_USER:" + name : "USER:" + target,
                        fields(layout, number, flag, name, name, password));
                    return HexFormat.of().formatHex(keys.calculate(canonical).digest());
                  }
                }));
      }
      Set<String> hashes = new HashSet<>();
      for (var job : jobs) assertTrue(hashes.add(job.get(30, TimeUnit.SECONDS)));
      assertEquals(100, hashes.size());
    }
  }

  static Mutation kind(String layout, boolean flag) {
    return switch (layout) {
      case "UCRREQ01" -> Mutation.CREATE;
      case "USTREQ01" -> flag ? Mutation.ENABLE : Mutation.DISABLE;
      case "URLREQ01" -> flag ? Mutation.PROMOTE : Mutation.DEMOTE;
      case "UPWREQ01" -> Mutation.RESET_PASSWORD;
      case "ULKREQ01" -> Mutation.UNLOCK;
      default -> throw new AssertionError();
    };
  }

  static List<Field> fields(
      String layout, long version, boolean flag, String name, String key, String password) {
    Field v = new Field("expectedVersion", "N1", Long.toString(version));
    return switch (layout) {
      case "UCRREQ01" ->
          List.of(
              new Field("username", "X1", name),
              new Field("usernameKey", "X1", key),
              new Field("password", "X1", password),
              new Field("role", "X1", flag ? "ADMIN" : "USER"),
              new Field("enabled", "B1", flag ? "1" : "0"));
      case "USTREQ01" -> List.of(new Field("enabled", "B1", flag ? "1" : "0"), v);
      case "URLREQ01" -> List.of(new Field("role", "X1", flag ? "ADMIN" : "USER"), v);
      case "UPWREQ01" -> List.of(new Field("password", "X1", password), v);
      case "ULKREQ01" -> List.of(v);
      default -> throw new AssertionError();
    };
  }

  static void check(
      UserMutationRequest request, AuthenticatedActor actor, String target, List<Field> fields)
      throws Exception {
    try (var canonical = request.canonical(actor);
        var keys = keys()) {
      assertEquals(Long.toString(actor.userId()), canonical.ownerScope());
      assertEquals(target, canonical.target());
      assertEquals("001", canonical.layoutVersion());
      assertEquals(fields.size(), canonical.fields().size());
      var bytes = new ByteArrayOutputStream();
      try (var out = new DataOutputStream(bytes)) {
        out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
        for (String value :
            List.of(
                Long.toString(actor.userId()), request.header().layoutId().value(), "001", target))
          lp(out, value);
        out.writeInt(fields.size());
        for (int i = 0; i < fields.size(); i++) {
          var expected = fields.get(i);
          var actual = canonical.fields().get(i);
          assertEquals(expected.name(), actual.name());
          assertEquals(expected.type(), actual.typeVersion());
          assertArrayEquals(expected.value().getBytes(StandardCharsets.UTF_8), actual.value());
          lp(out, expected.name());
          lp(out, expected.type());
          lp(out, expected.value());
        }
      }
      Mac mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(new byte[32], "HmacSHA256"));
      assertArrayEquals(mac.doFinal(bytes.toByteArray()), keys.calculate(canonical).digest());
    }
  }

  static FingerprintKeyRing keys() {
    return new FingerprintKeyRing("test", new byte[32], null, null);
  }

  static void lp(DataOutputStream out, String value) throws Exception {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    out.writeInt(bytes.length);
    out.write(bytes);
  }

  static UserCommandMetadata metadata() {
    return new UserCommandMetadata(MESSAGE, MESSAGE, NOW);
  }

  static void invalid(WireMessage<FixedPayload> wire) {
    var failure =
        assertThrows(PermanentProtocolException.class, () -> UserMutationRequest.decode(wire));
    assertEquals("user mutation request is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  static WireMessage<FixedPayload> message(String layout, byte[] bytes, UUID id) {
    var h =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW.plusMillis(id.getLeastSignificantBits()),
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            bytes.length,
            0,
            0,
            256 + bytes.length,
            Optional.empty());
    return new WireMessage<>(h, new FixedPayload(bytes, 0, List.of()));
  }

  static byte[] data(
      String layout,
      long id,
      long version,
      boolean flag,
      String username,
      String password,
      UUID token) {
    int size =
        switch (layout) {
          case "UCRREQ01" -> 372;
          case "USTREQ01", "ULKREQ01" -> 60;
          case "URLREQ01" -> 68;
          case "UPWREQ01" -> 324;
          default -> throw new AssertionError();
        };
    byte[] data = new byte[size];
    Arrays.fill(data, (byte) 32);
    String target = String.format(Locale.ROOT, "%012d", id);
    String v = String.format(Locale.ROOT, "%09d", version);
    switch (layout) {
      case "UCRREQ01" -> {
        put(data, 0, username);
        put(data, 64, password);
        put(data, 320, flag ? "ADMIN" : "USER");
        put(data, 325, flag ? "1" : "0");
        put(data, 326, token.toString());
      }
      case "USTREQ01" -> {
        put(data, 0, target);
        put(data, 12, flag ? "1" : "0");
        put(data, 13, v);
        put(data, 22, token.toString());
      }
      case "URLREQ01" -> {
        put(data, 0, target);
        put(data, 12, flag ? "ADMIN" : "USER");
        put(data, 17, v);
        put(data, 26, token.toString());
      }
      case "UPWREQ01" -> {
        put(data, 0, target);
        put(data, 12, password);
        put(data, 268, v);
        put(data, 277, token.toString());
      }
      case "ULKREQ01" -> {
        put(data, 0, target);
        put(data, 12, v);
        put(data, 21, token.toString());
      }
      default -> throw new AssertionError();
    }
    return data;
  }

  static void put(byte[] bytes, int offset, String value) {
    byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(encoded, 0, bytes, offset, encoded.length);
  }

  static void seed() throws Exception {
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_users restart identity cascade");
    }
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) select i,'u'||i,'u'||i,'unusable-test-hash',case when i=1 then 'ADMIN' else 'USER' end,'ACTIVE','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z' from (values(1),(3))n(i)");
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("select setval('schubert.app_users_id_seq',3,true)");
    }
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) values(?,?,?,decode(repeat('00',29),'hex'),'test','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T08:00:00Z','127.0.0.1',?)")) {
      for (int id : new int[] {1, 3}) {
        s.setObject(1, new UUID(0, id));
        s.setInt(2, id);
        s.setString(
            3,
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest(
                            (id == 1 ? "b" : "d").repeat(64).getBytes(StandardCharsets.US_ASCII))));
        s.setObject(4, new UUID(1, id));
        s.executeUpdate();
      }
    }
  }

  static void sql(String text) throws Exception {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.execute(text);
    }
  }

  static long count(String text) throws Exception {
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery(text)) {
      assertTrue(r.next());
      long value = r.getLong(1);
      assertFalse(r.next());
      return value;
    }
  }
}
