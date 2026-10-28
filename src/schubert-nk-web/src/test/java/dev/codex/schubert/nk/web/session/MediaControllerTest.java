package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.head;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.MediaMvcConfiguration;
import dev.codex.schubert.nk.web.controller.MediaController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebMediaAudit;
import dev.codex.schubert.nk.web.media.MediaDeliveryException;
import dev.codex.schubert.nk.web.media.MediaRangeService;
import dev.codex.schubert.nk.web.media.MediaResponseDecoder;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import jakarta.servlet.ServletOutputStream;
import jakarta.servlet.WriteListener;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.Principal;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** UI232/235 literal byte oracle + SS333 HTTP/stream oracle. PG-D-343/PT-MED-HTTP001..010. */
class MediaControllerTest {
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_HEAD_DEE4F10B = "HEAD";
  private static final String FIXTURE_DOWNLOAD_9638BA4D = "download";
  private static final String FIXTURE_TRACK1_3926438E = "track1";
  private static final String FIXTURE_AUD_5C44DBC9 = "AUD";
  private static WebLogDatabaseFixture db;
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-02T19:00:00Z"), ZoneOffset.UTC);
  private static final String HASH = "0123456789abcdef".repeat(4);
  private static final byte[] FILE = "abcdefghijkl".getBytes(StandardCharsets.US_ASCII);
  private static final List<String> PATHS =
      List.of(
          "/audio/7",
          "/audio/7/download",
          "/animation/media/opening",
          "/music/media/track1",
          "/music/download/track1");
  @TempDir Path root;

  @BeforeAll
  static void start(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "reader", role, AuthenticationContext.of("a".repeat(64)), CLOCK.instant());
  }

  @Test
  void http001FiveRoutesFreshApiBothRolesGetHeadAndSuccessProfiles() throws Exception {
    try (var f = new Fixture(root)) {
      var seen = new HashSet<UUID>();
      for (var role : UserRole.values())
        for (var code : List.of(FIXTURE_0000_876EEFE0, "0200"))
          for (var method : List.of(FIXTURE_GET_04F32A7E, FIXTURE_HEAD_DEE4F10B))
            for (var path : PATHS) {
              f.code = code;
              var r = f.request(method, path);
              r.addParameter("password", "synthetic-query-must-not-be-logged");
              var s = new MockHttpServletResponse();
              int sends = f.requests.size();
              call(f.controller, path, actor(role), r, s);
              assertEquals(sends + 1, f.requests.size());
              assertTrue(seen.add(UUID.fromString(ascii(f.requests.getLast(), 24, 36))));
              assertEquals(200, s.getStatus());
              assertEquals("12", s.getHeader("Content-Length"));
              assertEquals("bytes", s.getHeader("Accept-Ranges"));
              assertEquals("private, no-store", s.getHeader("Cache-Control"));
              assertEquals("nosniff", s.getHeader("X-Content-Type-Options"));
              boolean attachment = path.contains(FIXTURE_DOWNLOAD_9638BA4D);
              assertEquals(
                  attachment ? "application/octet-stream" : mime(path), s.getContentType());
              assertTrue(
                  s.getHeader("Content-Disposition")
                      .startsWith(attachment ? "attachment;" : "inline"));
              assertNull(s.getHeader("ETag"));
              assertNull(s.getHeader("Last-Modified"));
              assertArrayEquals(
                  method.equals(FIXTURE_HEAD_DEE4F10B) ? new byte[0] : FILE,
                  s.getContentAsByteArray());
              var event = f.log.events.getLast();
              assertEquals(
                  attachment ? "MEDIA_DOWNLOADED" : "MEDIA_STREAMED",
                  event.get("action").getAsString());
              assertEquals("SUCCESS", event.get("outcome").getAsString());
              assertEquals(role.name(), event.get("actorRole").getAsString());
              assertEquals(
                  method.equals(FIXTURE_HEAD_DEE4F10B) ? 0 : 12,
                  event.get("responseBytes").getAsLong());
              String text = event.toString();
              assertFalse(text.contains(HASH));
              assertFalse(text.contains("synthetic-query"));
              assertFalse(text.contains("authenticationContext"));
              f.erased();
            }
      assertEquals(40, seen.size());
    }
  }

  @Test
  void http002LiteralRangeHeadersAndSlices() throws Exception {
    String[] inputs = {
      "bytes=0-0",
      "bytes=2-4",
      "bytes=10-",
      "bytes=-2",
      "bytes=-99",
      "bytes=2-4,not-valid",
      "bytes=nope,0-1",
      "items=0-1",
      "bytes=12-",
      "bytes=4-2",
      "bytes=-0",
      "bytes=18446744073709551616-",
      "",
      "BYTES=0-99"
    };
    int[] first = {0, 2, 10, 10, 0, 2, -1, -1, -1, -1, -1, -1, -1, 0};
    int[] last = {0, 4, 11, 11, 11, 4, -1, -1, -1, -1, -1, -1, -1, 11};
    try (var f = new Fixture(root)) {
      for (var path : PATHS)
        for (var method : List.of(FIXTURE_GET_04F32A7E, FIXTURE_HEAD_DEE4F10B))
          for (int i = 0; i < inputs.length; i++) {
            var r = f.request(method, path);
            r.addHeader("Range", inputs[i]);
            var s = new MockHttpServletResponse();
            call(f.controller, path, actor(UserRole.USER), r, s);
            boolean download = path.contains(FIXTURE_DOWNLOAD_9638BA4D);
            boolean bad = first[i] < 0;
            int status = download ? 200 : bad ? 416 : 206;
            assertEquals(status, s.getStatus());
            int length = download ? 12 : bad ? 0 : last[i] - first[i] + 1;
            assertEquals(Integer.toString(length), s.getHeader("Content-Length"));
            assertEquals(
                download ? null : bad ? "bytes */12" : "bytes " + first[i] + "-" + last[i] + "/12",
                s.getHeader("Content-Range"));
            byte[] expected =
                method.equals(FIXTURE_HEAD_DEE4F10B) || (!download && bad)
                    ? new byte[0]
                    : download ? FILE : Arrays.copyOfRange(FILE, first[i], last[i] + 1);
            assertArrayEquals(expected, s.getContentAsByteArray());
            assertEquals(
                status == 416
                    ? "MEDIA_RANGE_REJECTED"
                    : download ? "MEDIA_DOWNLOADED" : "MEDIA_STREAMED",
                f.log.events.getLast().get("action").getAsString());
            f.erased();
          }
    }
  }

  @Test
  void http003InvalidAndNullInputsDoNotSendOrOpen() throws Exception {
    try (var f = new Fixture(root)) {
      for (int dependency = 0; dependency < 4; dependency++) {
        final int n = dependency;
        assertThrows(
            NullPointerException.class,
            () ->
                new MediaController(
                    n == 0 ? null : f.client,
                    n == 1 ? null : f.security.handler,
                    n == 2 ? null : f.service,
                    n == 3 ? null : f.audit));
      }
      for (String id : List.of("", "0", "-1", "+1", " 7", "7 ", "1000000000000", "1.0", "１２")) {
        var s = new MockHttpServletResponse();
        f.controller.audio(
            id, actor(UserRole.USER), f.request(FIXTURE_GET_04F32A7E, "/audio/7"), s);
        assertEquals(400, s.getStatus());
      }
      for (String id : List.of("", "a".repeat(65), "字".repeat(22), "bad\n", "bad ")) {
        for (boolean video : List.of(false, true)) {
          var s = new MockHttpServletResponse();
          if (video)
            f.controller.video(
                id, actor(UserRole.USER), f.request(FIXTURE_GET_04F32A7E, PATHS.get(2)), s);
          else
            f.controller.music(
                id, actor(UserRole.USER), f.request(FIXTURE_GET_04F32A7E, PATHS.get(3)), s);
          assertEquals(400, s.getStatus());
        }
      }
      var r = f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst());
      var s = new MockHttpServletResponse();
      assertThrows(
          NullPointerException.class, () -> f.controller.audio(null, actor(UserRole.USER), r, s));
      assertThrows(NullPointerException.class, () -> f.controller.audio("7", null, r, s));
      assertThrows(
          NullPointerException.class, () -> f.controller.audio("7", actor(UserRole.USER), null, s));
      assertThrows(
          NullPointerException.class, () -> f.controller.audio("7", actor(UserRole.USER), r, null));
      assertThrows(
          SessionStoreException.class,
          () -> f.controller.audio("7", (Principal) () -> "reader", r, s));
      assertTrue(f.requests.isEmpty());
      assertEquals(0, f.opens.get());
      f.controller.audio("000000000007", actor(UserRole.USER), r, s);
      assertEquals(200, s.getStatus());
      var normalized = new MockHttpServletResponse();
      f.controller.music(
          "e\u0301",
          actor(UserRole.USER),
          f.request(FIXTURE_GET_04F32A7E, "/music/media/é"),
          normalized);
      assertEquals(200, normalized.getStatus());
      assertEquals(
          "é", new String(f.requests.getLast(), 256, 64, StandardCharsets.UTF_8).stripTrailing());
      f.erased();
    }
  }

  @Test
  void http004ErrorsMalformedTransportKeepFilesClosed() throws Exception {
    String[] codes = {"0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001"};
    int[] statuses = {400, 401, 403, 404, 409, 429, 409, 503, 503};
    try (var f = new Fixture(root)) {
      for (var path : PATHS)
        for (int i = 0; i < codes.length; i++) {
          f.code = codes[i];
          var s = new MockHttpServletResponse();
          call(f.controller, path, actor(UserRole.USER), f.request(FIXTURE_GET_04F32A7E, path), s);
          assertEquals(statuses[i], s.getStatus());
        }
      f.code = FIXTURE_0000_876EEFE0;
      for (int mode = 0; mode < 7; mode++) {
        final int mutation = mode;
        f.reply =
            (id, b) -> {
              if (mutation == 0) throw new jakarta.jms.JMSException("synthetic-private-path");
              if (mutation == 1) return new byte[0];
              var bytes = response(id, b, FIXTURE_0000_876EEFE0);
              if (mutation == 2) put(bytes, 60, new UUID(0, 999).toString());
              if (mutation == 3) bytes[113] = 'b';
              if (mutation == 4) bytes[212] = 'x';
              if (mutation == 5) bytes[256 + 973] = 'x';
              if (mutation == 6) return null;
              return bytes;
            };
        var s = new MockHttpServletResponse();
        call(
            f.controller,
            PATHS.getFirst(),
            actor(UserRole.USER),
            f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst()),
            s);
        assertEquals(503, s.getStatus());
        assertFalse(s.getContentAsString().contains("private-path"));
      }
      assertEquals(0, f.opens.get());
      f.erased();
    }
  }

  @Test
  void http005RequestBindingRejectsOtherDescriptors() throws Exception {
    try (var f = new Fixture(root)) {
      for (var path : PATHS)
        for (int mode = 0; mode < 4; mode++) {
          final int mutation = mode;
          f.reply =
              (id, b) -> {
                var bytes = response(id, b, FIXTURE_0000_876EEFE0);
                if (mutation == 0) {
                  Arrays.fill(bytes, 256, 320, (byte) ' ');
                  put(bytes, 256, "8");
                }
                if (mutation == 1)
                  bytes[256 + 972] = bytes[256 + 972] == 'I' ? (byte) 'A' : (byte) 'I';
                if (mutation == 2) {
                  Arrays.fill(bytes, 320, 832, (byte) ' ');
                  put(bytes, 320, "outside/a.ogg");
                }
                if (mutation == 3) {
                  Arrays.fill(bytes, 1164, 1228, (byte) ' ');
                  put(bytes, 1164, "text/html");
                }
                return bytes;
              };
          var s = new MockHttpServletResponse();
          call(f.controller, path, actor(UserRole.ADMIN), f.request(FIXTURE_GET_04F32A7E, path), s);
          assertEquals(503, s.getStatus());
        }
      assertEquals(0, f.opens.get());
      f.erased();
    }
  }

  @Test
  void http006ApiInvalidClearsActualEncryptedSessionForAllMediaRoutes() throws Exception {
    try (var f = new Fixture(root)) {
      f.code = "0102";
      for (var method : List.of(FIXTURE_GET_04F32A7E, FIXTURE_HEAD_DEE4F10B))
        for (var path : PATHS) {
          var snapshot = f.security.authenticated(actor(UserRole.USER));
          var r = raw(method, path);
          f.expectedPath.set(path);
          r.setCookies(new Cookie("SCHUBERT_NK_SESSION", snapshot.sessionId().cookieValue()));
          var s = new MockHttpServletResponse();
          f.security.run(
              r,
              s,
              (request, response) ->
                  call(
                      f.controller,
                      path,
                      ((HttpServletRequest) request).getUserPrincipal(),
                      (HttpServletRequest) request,
                      (HttpServletResponse) response));
          assertEquals(401, s.getStatus());
          assertNull(s.getHeader("Location"));
          assertTrue(f.security.f.repository.find(snapshot.sessionId()).isEmpty());
          assertTrue(s.getHeader("Set-Cookie").contains("Max-Age=0"));
          assertNull(SecurityContextHolder.getContext().getAuthentication());
        }
      assertEquals(10, f.requests.size());
      assertEquals(0, f.opens.get());
      f.erased();
    }
  }

  @Test
  void http007IoCommitAbortAndTwentyStreamAdmissionRelease() throws Exception {
    try (var f = new Fixture(root)) {
      f.source =
          (descriptor, operation) -> {
            throw new IOException("synthetic-file-path");
          };
      var s = new MockHttpServletResponse();
      call(
          f.controller,
          PATHS.getFirst(),
          actor(UserRole.USER),
          f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst()),
          s);
      assertEquals(503, s.getStatus());
      assertNull(s.getHeader("Retry-After"));
      assertEquals("FILE_IO", f.log.events.getLast().get("errorCode").getAsString());
      var committed = new MockHttpServletResponse();
      f.source =
          (descriptor, operation) -> {
            f.read(descriptor, operation);
            committed.flushBuffer();
            throw new IOException("synthetic-file-path");
          };
      var e =
          assertThrows(
              IOException.class,
              () ->
                  call(
                      f.controller,
                      PATHS.getFirst(),
                      actor(UserRole.USER),
                      f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst()),
                      committed));
      assertEquals("media response interrupted", e.getMessage());
      assertNull(e.getCause());
      assertEquals(200, committed.getStatus());
      assertArrayEquals(FILE, committed.getContentAsByteArray());
      assertEquals(12, f.log.events.getLast().get("responseBytes").getAsLong());
      f.source = f::read;
      var aborted =
          new MockHttpServletResponse() {
            @Override
            public ServletOutputStream getOutputStream() {
              return new ServletOutputStream() {
                @Override
                public boolean isReady() {
                  return true;
                }

                @Override
                public void setWriteListener(WriteListener listener) {
                  throw new AssertionError();
                }

                @Override
                public void write(int value) throws IOException {
                  throw new IOException("synthetic-socket");
                }
              };
            }
          };
      call(
          f.controller,
          PATHS.getFirst(),
          actor(UserRole.USER),
          f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst()),
          aborted);
      assertEquals(503, aborted.getStatus());
      var event = f.log.events.getLast();
      assertEquals("INFO", event.get("level").getAsString());
      assertEquals("CLIENT_ABORT", event.getAsJsonObject("details").get("reason").getAsString());
      assertFalse(event.has("errorCode"));
      var entered = new CountDownLatch(20);
      var release = new CountDownLatch(1);
      var admitted = new Semaphore(0);
      f.source =
          (descriptor, operation) -> {
            entered.countDown();
            admitted.release();
            try {
              assertTrue(release.await(10, TimeUnit.SECONDS));
            } catch (InterruptedException interrupted) {
              Thread.currentThread().interrupt();
              throw new IOException();
            }
            f.read(descriptor, operation);
          };
      try (var workers = Executors.newFixedThreadPool(20)) {
        var jobs = new ArrayList<Future<?>>();
        for (int i = 0; i < 20; i++) {
          jobs.add(
              workers.submit(
                  () -> {
                    try {
                      var response = new MockHttpServletResponse();
                      call(
                          f.controller,
                          PATHS.getFirst(),
                          actor(UserRole.USER),
                          f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst()),
                          response);
                      assertEquals(200, response.getStatus());
                    } catch (Exception failure) {
                      throw new AssertionError(failure);
                    }
                  }));
          assertTrue(admitted.tryAcquire(10, TimeUnit.SECONDS));
        }
        try {
          assertTrue(entered.await(10, TimeUnit.SECONDS));
          var busy = new MockHttpServletResponse();
          call(
              f.controller,
              PATHS.getFirst(),
              actor(UserRole.USER),
              f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst()),
              busy);
          assertEquals(503, busy.getStatus());
          assertEquals("1", busy.getHeader("Retry-After"));
          assertEquals("RESOURCE_THREAD", f.log.events.getLast().get("errorCode").getAsString());
        } finally {
          release.countDown();
        }
        for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      }
      f.source = f::read;
      var normal = new MockHttpServletResponse();
      call(
          f.controller,
          PATHS.getFirst(),
          actor(UserRole.USER),
          f.request(FIXTURE_GET_04F32A7E, PATHS.getFirst()),
          normal);
      assertEquals(200, normal.getStatus());
      f.erased();
    }
  }

  @Test
  void http008MvcFixedGetHeadRoutesAndSecurityRejectsAnonymous() throws Exception {
    try (var f = new Fixture(root);
        var context = new AnnotationConfigWebApplicationContext()) {
      context.setServletContext(new MockServletContext());
      context.register(MediaMvcConfiguration.class);
      context.addBeanFactoryPostProcessor(
          factory -> {
            factory.registerSingleton("mediaDescriptorWireClient", f.client);
            factory.registerSingleton("apiSessionInvalidHandler", f.security.handler);
            factory.registerSingleton("mediaRangeService", f.service);
            factory.registerSingleton("webMediaAudit", f.audit);
          });
      context.refresh();
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      for (var path : PATHS)
        for (boolean head : List.of(false, true)) {
          var r = f.request(head ? FIXTURE_HEAD_DEE4F10B : FIXTURE_GET_04F32A7E, path);
          var result =
              mvc.perform(
                      (head ? head(path) : get(path))
                          .principal(actor(UserRole.USER))
                          .requestAttr(
                              "dev.codex.schubert.nk.web.security.WebRequestContext",
                              r.getAttribute(
                                  "dev.codex.schubert.nk.web.security.WebRequestContext")))
                  .andReturn();
          assertEquals(200, result.getResponse().getStatus());
          assertArrayEquals(
              head ? new byte[0] : FILE, result.getResponse().getContentAsByteArray());
        }
      assertEquals(405, mvc.perform(post(PATHS.getFirst())).andReturn().getResponse().getStatus());
      for (var path : PATHS) {
        int sends = f.requests.size();
        var response = new MockHttpServletResponse();
        f.security.run(
            raw(FIXTURE_GET_04F32A7E, path),
            response,
            (request, res) -> fail("anonymous media reached business"));
        assertEquals(403, response.getStatus());
        assertEquals(sends, f.requests.size());
      }
      f.erased();
    }
  }

  @Test
  void http009ConcurrentRangeAndFreshContextStayIsolated() throws Exception {
    try (var f = new Fixture(root);
        var workers = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Future<?>>();
      for (int i = 0; i < 100; i++) {
        final int sequence = i;
        jobs.add(
            workers.submit(
                () -> {
                  try {
                    String path = PATHS.get(sequence % 5);
                    String context = String.format(Locale.ROOT, "%064x", sequence + 1);
                    f.expectedContext.set(context);
                    var r = f.request(FIXTURE_GET_04F32A7E, path);
                    r.addHeader("Range", "bytes=2-4");
                    var response = new MockHttpServletResponse();
                    call(
                        f.controller,
                        path,
                        new SessionPrincipal(
                            "reader",
                            sequence % 2 == 0 ? UserRole.USER : UserRole.ADMIN,
                            AuthenticationContext.of(context),
                            CLOCK.instant()),
                        r,
                        response);
                    assertEquals(
                        path.contains(FIXTURE_DOWNLOAD_9638BA4D) ? 200 : 206, response.getStatus());
                    assertArrayEquals(
                        path.contains(FIXTURE_DOWNLOAD_9638BA4D)
                            ? FILE
                            : "cde".getBytes(StandardCharsets.US_ASCII),
                        response.getContentAsByteArray());
                  } catch (Exception failure) {
                    throw new AssertionError(failure);
                  }
                }));
      }
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(100, f.requests.size());
      assertEquals(100, f.requests.stream().map(b -> ascii(b, 24, 36)).distinct().count());
      assertEquals(
          100, f.log.events.stream().map(j -> j.get("requestId").getAsString()).distinct().count());
      f.erased();
    }
  }

  @Test
  void http010VerifiedProjectionAndClosedAuditContracts() throws Exception {
    try (var f = new Fixture(root)) {
      var input =
          new TypedPayloadValues(
              new LayoutId("AUDREQ01"),
              new AudioDescriptorRequestData(new AudioId(7), ContentDisposition.INLINE),
              List.of());
      var success = f.client.exchange(input, actor(UserRole.USER).authenticationContext());
      var projected = MediaResponseDecoder.decodeVerified(input, success);
      assertEquals("7", projected.descriptor().orElseThrow().logicalId());
      assertTrue(projected.videoMetadata().isEmpty());
      assertThrows(
          NullPointerException.class, () -> MediaResponseDecoder.decodeVerified(null, success));
      assertThrows(
          NullPointerException.class, () -> MediaResponseDecoder.decodeVerified(input, null));
      for (var bad :
          List.of(
              new TypedPayloadValues(
                  new LayoutId("LOGREQ01"),
                  new dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData(),
                  List.of()),
              new TypedPayloadValues(
                  new LayoutId("VIDREQ01"), new VideoDescriptorRequestData("opening"), List.of()),
              new TypedPayloadValues(
                  new LayoutId("MEDREQ01"),
                  new MusicDescriptorRequestData(
                      FIXTURE_TRACK1_3926438E, ContentDisposition.INLINE),
                  List.of()),
              new TypedPayloadValues(
                  new LayoutId("AUDREQ01"), new VideoDescriptorRequestData("opening"), List.of()),
              new TypedPayloadValues(
                  new LayoutId("VIDREQ01"),
                  new AudioDescriptorRequestData(new AudioId(7), ContentDisposition.INLINE),
                  List.of()),
              new TypedPayloadValues(
                  new LayoutId("MEDREQ01"),
                  new AudioDescriptorRequestData(new AudioId(7), ContentDisposition.INLINE),
                  List.of()),
              new TypedPayloadValues(
                  new LayoutId("AUDREQ01"),
                  new AudioDescriptorRequestData(new AudioId(7), ContentDisposition.INLINE),
                  List.of((PayloadRecord) () -> new FieldValueSet(Map.of()))))) {
        assertEquals(
            MediaDeliveryException.Reason.INVALID_DESCRIPTOR,
            assertThrows(
                    MediaDeliveryException.class,
                    () -> MediaResponseDecoder.decodeVerified(bad, success))
                .reason());
      }
      f.expectedPath.set("/music/media/é");
      var canonicalRequest =
          new TypedPayloadValues(
              new LayoutId("MEDREQ01"),
              new MusicDescriptorRequestData("e\u0301", ContentDisposition.INLINE),
              List.of());
      assertEquals(
          "é",
          MediaResponseDecoder.decodeVerified(
                  canonicalRequest,
                  f.client.exchange(canonicalRequest, actor(UserRole.USER).authenticationContext()))
              .descriptor()
              .orElseThrow()
              .logicalId());
      f.expectedPath.set(PATHS.getFirst());
      f.code = "9000";
      assertTrue(
          MediaResponseDecoder.decodeVerified(
                  input, f.client.exchange(input, actor(UserRole.USER).authenticationContext()))
              .descriptor()
              .isEmpty());
      var descriptor = projected.descriptor().orElseThrow();
      var id = new UUID(0, 1);
      var actor = actor(UserRole.USER);
      assertThrows(NullPointerException.class, () -> new WebMediaAudit(null, CLOCK, "pt", "pt"));
      assertThrows(NullPointerException.class, () -> new WebMediaAudit(f.log, null, "pt", "pt"));
      for (String value : List.of("", "-bad", "bad\n", "a".repeat(65))) {
        assertThrows(
            IllegalArgumentException.class, () -> new WebMediaAudit(f.log, CLOCK, value, "pt"));
        assertThrows(
            IllegalArgumentException.class, () -> new WebMediaAudit(f.log, CLOCK, "pt", value));
      }
      assertThrows(NullPointerException.class, () -> new WebMediaAudit(f.log, CLOCK, null, "pt"));
      assertThrows(NullPointerException.class, () -> new WebMediaAudit(f.log, CLOCK, "pt", null));
      assertThrows(
          NullPointerException.class,
          () -> f.audit.record(null, actor, descriptor, 200, 0, WebMediaAudit.Failure.NONE));
      assertThrows(
          NullPointerException.class,
          () -> f.audit.record(id, null, descriptor, 200, 0, WebMediaAudit.Failure.NONE));
      assertThrows(
          NullPointerException.class,
          () -> f.audit.record(id, actor, null, 200, 0, WebMediaAudit.Failure.NONE));
      assertThrows(
          NullPointerException.class, () -> f.audit.record(id, actor, descriptor, 200, 0, null));
      for (int status : new int[] {199, 201, 502, 503})
        assertThrows(
            IllegalArgumentException.class,
            () -> f.audit.record(id, actor, descriptor, status, 0, WebMediaAudit.Failure.NONE));
      for (long bytes : new long[] {-1, 13})
        assertThrows(
            IllegalArgumentException.class,
            () -> f.audit.record(id, actor, descriptor, 200, bytes, WebMediaAudit.Failure.NONE));
      f.log.fail = true;
      assertThrows(
          IllegalStateException.class,
          () -> f.audit.record(id, actor, descriptor, 200, 0, WebMediaAudit.Failure.NONE));
      f.erased();
    }
  }

  private static void call(
      MediaController c, String path, Principal p, HttpServletRequest r, HttpServletResponse s)
      throws IOException {
    switch (path) {
      case "/audio/7" -> c.audio("7", p, r, s);
      case "/audio/7/download" -> c.audioDownload("7", p, r, s);
      case "/animation/media/opening" -> c.video("opening", p, r, s);
      case "/music/media/track1" -> c.music(FIXTURE_TRACK1_3926438E, p, r, s);
      case "/music/download/track1" -> c.musicDownload(FIXTURE_TRACK1_3926438E, p, r, s);
      default -> throw new AssertionError();
    }
  }

  private static MockHttpServletRequest raw(String method, String path) {
    var r = new MockHttpServletRequest(method, path);
    r.setRemoteAddr("127.0.0.1");
    r.addHeader("X-Forwarded-For", "203.0.113.1");
    r.addHeader("X-Forwarded-Proto", "https");
    return r;
  }

  private static String mime(String path) {
    return path.startsWith("/audio")
        ? "audio/ogg"
        : path.startsWith("/animation") ? "video/mp4" : "audio/wav";
  }

  private static String ascii(byte[] b, int at, int length) {
    return new String(b, at, length, StandardCharsets.US_ASCII);
  }

  private static void put(byte[] b, int at, String value) {
    var bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, b, at, bytes.length);
  }

  private static byte[] response(UUID id, byte[] request, String code) {
    String type = ascii(request, 11, 3);
    boolean video = type.equals("VID");
    int size = video ? 1808 : 1024;
    var b = new byte[256 + size];
    Arrays.fill(b, (byte) ' ');
    put(b, 0, "SCHBNK01001");
    put(b, 11, type + "RSP01");
    put(b, 19, "001SS");
    put(b, 24, new UUID(1, id.getLeastSignificantBits()).toString());
    put(b, 60, id.toString());
    put(b, 96, "20261003040000000");
    put(b, 113, ascii(request, 113, 64));
    put(b, 177, "0256");
    put(b, 181, String.format(Locale.ROOT, "%06d", size));
    put(b, 187, "000000000000");
    put(b, 199, String.format(Locale.ROOT, "%09d", b.length));
    put(b, 208, code);
    boolean ok = code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200");
    put(b, 1088, ok ? "000000000012" : "000000000000");
    if (ok) {
      String logical =
          type.equals(FIXTURE_AUD_5C44DBC9)
              ? Long.toString(Long.parseLong(ascii(request, 256, 12)))
              : new String(request, 256, 64, StandardCharsets.UTF_8).stripTrailing();
      String name = type.equals(FIXTURE_AUD_5C44DBC9) ? "a.ogg" : video ? "a.mp4" : "a.wav";
      put(b, 256, logical);
      put(
          b,
          320,
          (type.equals(FIXTURE_AUD_5C44DBC9) ? "scenario/" : video ? "video/" : "music/") + name);
      put(b, 832, name);
      put(b, 1100, HASH);
      put(
          b,
          1164,
          type.equals(FIXTURE_AUD_5C44DBC9) ? "audio/ogg" : video ? "video/mp4" : "audio/wav");
      b[1228] = (byte) (video ? 'I' : request[type.equals(FIXTURE_AUD_5C44DBC9) ? 268 : 320]);
      if (video) {
        put(b, 1280, "Opening");
        put(b, 1536, "OPENING");
        put(b, 1552, "opening.mp4");
      }
    }
    return b;
  }

  @FunctionalInterface
  private interface Reply {
    byte[] receive(UUID id, byte[] b) throws jakarta.jms.JMSException;
  }

  private final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicInteger ids = new AtomicInteger();
    final AtomicInteger opens = new AtomicInteger();
    final List<byte[]> requests = new CopyOnWriteArrayList<>();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final SessionLoginHandlerTest.Log log = new SessionLoginHandlerTest.Log();
    final WebMediaAudit audit = new WebMediaAudit(log, CLOCK, "pt", "pt");
    final ThreadLocal<String> expectedPath = ThreadLocal.withInitial(PATHS::getFirst);
    final ThreadLocal<String> expectedContext = ThreadLocal.withInitial(() -> "a".repeat(64));
    final MediaRangeService service = new MediaRangeService((d, o) -> this.source.read(d, o));
    final MediaDescriptorWireClient client =
        new MediaDescriptorWireClient(
            wire,
            (id, b) -> {
              buffers.add(b);
              requests.add(b.clone());
              assertEquals("SCHBNK01001", ascii(b, 0, 11));
              assertEquals("001QS", ascii(b, 19, 5));
              assertEquals(id.toString(), ascii(b, 24, 36));
              assertEquals(id.toString(), ascii(b, 60, 36));
              assertEquals("20261003040000000", ascii(b, 96, 17));
              assertEquals(expectedContext.get(), ascii(b, 113, 64));
              String path = expectedPath.get();
              String type =
                  path.startsWith("/audio")
                      ? FIXTURE_AUD_5C44DBC9
                      : path.startsWith("/animation") ? "VID" : "MED";
              assertEquals(type, ascii(b, 11, 3));
              int length = type.equals(FIXTURE_AUD_5C44DBC9) ? 16 : type.equals("VID") ? 64 : 72;
              var expected = new byte[256 + length];
              Arrays.fill(expected, (byte) ' ');
              put(expected, 0, "SCHBNK01001");
              put(expected, 11, type + "REQ01");
              put(expected, 19, "001QS");
              put(expected, 24, id.toString());
              put(expected, 60, id.toString());
              put(expected, 96, "20261003040000000");
              put(expected, 113, expectedContext.get());
              put(expected, 177, "0256");
              put(expected, 181, String.format(Locale.ROOT, "%06d", length));
              put(expected, 187, "000000000000");
              put(expected, 199, String.format(Locale.ROOT, "%09d", expected.length));
              if (type.equals(FIXTURE_AUD_5C44DBC9)) {
                put(expected, 256, "000000000007");
                expected[268] = (byte) (path.contains(FIXTURE_DOWNLOAD_9638BA4D) ? 'A' : 'I');
              } else {
                put(
                    expected,
                    256,
                    path.substring(path.lastIndexOf('/') + 1).equals(FIXTURE_TRACK1_3926438E)
                            || path.endsWith(FIXTURE_DOWNLOAD_9638BA4D)
                        ? FIXTURE_TRACK1_3926438E
                        : path.substring(path.lastIndexOf('/') + 1));
                if (type.equals("MED"))
                  expected[320] = (byte) (path.contains(FIXTURE_DOWNLOAD_9638BA4D) ? 'A' : 'I');
              }
              assertArrayEquals(expected, b);
              var replyBytes = this.reply.receive(id, b);
              if (replyBytes != null) assertTrue(wire.onReply(id, replyBytes));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofSeconds(1));
    final MediaController controller =
        new MediaController(client, security.handler, service, audit);
    volatile String code = FIXTURE_0000_876EEFE0;
    volatile Reply reply = (id, b) -> response(id, b, code);
    volatile MediaRangeService.FileSource source = this::read;
    final Path file;

    Fixture(Path path) throws IOException {
      file = path.resolve("public.bin");
      Files.write(file, FILE);
    }

    MockHttpServletRequest request(String method, String path) throws Exception {
      expectedPath.set(path);
      return security.mock(method, path);
    }

    void read(MediaDescriptor descriptor, MediaRangeService.ReadOperation operation)
        throws IOException {
      opens.incrementAndGet();
      assertEquals(12, descriptor.byteLength());
      assertEquals(HASH, descriptor.sha256());
      try (SeekableByteChannel channel = Files.newByteChannel(file, StandardOpenOption.READ)) {
        operation.execute(channel);
      }
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      buffers.forEach(b -> assertArrayEquals(new byte[b.length], b));
    }

    @Override
    public void close() {
      security.close();
    }
  }
}
