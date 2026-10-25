package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.CONTEXT;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.Fixture;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.M0;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.NOW;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.TOKEN;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.request;
import static dev.codex.schubert.nk.api.application.question.QuestionWorkerServiceTest.delivery;
import static dev.codex.schubert.nk.api.application.question.QuestionWorkerServiceTest.event;
import static dev.codex.schubert.nk.api.application.question.QuestionWorkerServiceTest.worker;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.io.TempDir;

/** NK-QST-001/NK-ASY-001; SS312/324/332/354; BUG1592/YKT1345; PT-QWK-GRAPH329001..003. */
@Timeout(value = 20, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class QuestionProviderFailureGraph329Test {
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  void providerBusinessMarkerFatalCannotBecomeBusinessError() throws Exception {
    try (var h = accepted()) {
      var calls = new AtomicInteger();
      var fatal = new AssertionError("PUBLIC fatal");
      var marker = new AnswerBusinessException();
      marker.addSuppressed(new IllegalStateException("PUBLIC wrapped", fatal));
      var worker =
          worker(
              h,
              question -> {
                assertEquals(0, h.live.get());
                calls.incrementAndGet();
                throw marker;
              },
              () -> false);
      assertSame(
          fatal, assertThrows(AssertionError.class, () -> worker.process(event(), delivery(1))));
      assertEquals(1, calls.get());
      assertProcessingWithoutCompletion(h, 0);
    }
  }

  @Test
  void providerRuntimeFatalCannotBecomeFinalDlq() throws Exception {
    try (var h = accepted()) {
      var calls = new AtomicInteger();
      var fatal = new AssertionError("PUBLIC fatal");
      var sql = new SQLException("PUBLIC sql");
      sql.setNextException(new SQLException("PUBLIC next", fatal));
      var failure = new IllegalStateException("PUBLIC wrapped", sql);
      var worker =
          worker(
              h,
              question -> {
                assertEquals(0, h.live.get());
                calls.incrementAndGet();
                throw failure;
              },
              () -> false);
      assertSame(
          fatal, assertThrows(AssertionError.class, () -> worker.process(event(), delivery(4))));
      assertEquals(1, calls.get());
      assertProcessingWithoutCompletion(h, 3);
    }
  }

  @Test
  void nonFatalProviderCyclesKeepApprovedBusinessAndFinalRetryOutcomes() throws Exception {
    for (boolean business : new boolean[] {true, false}) {
      try (var h = accepted()) {
        var calls = new AtomicInteger();
        RuntimeException failure =
            business ? new AnswerBusinessException() : new IllegalStateException("PUBLIC root");
        var alias = new IllegalArgumentException("PUBLIC alias", failure);
        failure.initCause(alias);
        failure.addSuppressed(alias);
        var worker =
            worker(
                h,
                question -> {
                  assertEquals(0, h.live.get());
                  calls.incrementAndGet();
                  throw failure;
                },
                () -> false);
        worker.process(event(), delivery(business ? 1 : 4));
        assertEquals(1, calls.get());
        assertEquals("ERROR", h.text("select state from schubert.async_jobs"));
        assertEquals("ERROR", h.text("select state from schubert.notifications"));
        assertEquals(
            business ? "PROCESS_FAILED" : "SYSTEM_UNAVAIL",
            h.text("select error_code from schubert.notifications"));
        assertEquals(0, h.scalar("select count(*) from schubert.answers"));
        assertEquals(business ? 1 : 2, h.scalar("select count(*) from schubert.mq_outbox"));
        assertEquals(0, h.live.get());
      }
    }
  }

  private static Fixture accepted() throws Exception {
    var h = new Fixture(database);
    boolean returned = false;
    try {
      h.confirmOnSignal(); // Input fixture: own DB SENT proof, never an actual MQ/native claim.
      h.service.process(request("Public fixture", M0, TOKEN, NOW, CONTEXT));
      assertEquals(1, h.scalar("select count(*) from schubert.async_jobs where state='RECEIVED'"));
      assertEquals(1, h.scalar("select count(*) from schubert.mq_outbox"));
      returned = true;
      return h;
    } finally {
      if (!returned) h.close();
    }
  }

  private static void assertProcessingWithoutCompletion(Fixture h, int retryCount)
      throws SQLException {
    assertEquals(
        1,
        h.scalar(
            "select count(*) from schubert.async_jobs j join schubert.notifications n on n.job_id=j.id"
                + " where j.state='PROCESSING' and j.completed_at is null and j.error_at is null"
                + " and n.state='PROCESSING' and n.error_code is null and n.error_message is null"));
    assertEquals(retryCount, h.scalar("select retry_count from schubert.async_jobs"));
    assertEquals(0, h.scalar("select count(*) from schubert.answers"));
    assertEquals(1, h.scalar("select count(*) from schubert.mq_outbox"));
    assertEquals(0, h.live.get());
  }
}
