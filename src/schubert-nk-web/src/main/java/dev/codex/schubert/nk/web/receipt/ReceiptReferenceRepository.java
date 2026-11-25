package dev.codex.schubert.nk.web.receipt;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Objects;
import java.util.Optional;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Owned short transactions using only the restricted Web technical role. Caller must provide
 * genuinely verified IF025 data, then release this transaction before fresh IF030/JMS; neither the
 * locator nor a successful insert proves API authorization. NK-WEB-002; FUN001/AUT004/DAT009;
 * UI241/242; SS313/331§9.4/332; QA048/SSC175; PG-D357; RCPT002/003/005. No business SQL, update,
 * owner, operation token, or snapshots.
 */
@NullMarked
public final class ReceiptReferenceRepository {
  private final DataSource dataSource;

  public ReceiptReferenceRepository(DataSource dataSource) {
    this.dataSource = Objects.requireNonNull(dataSource, "dataSource");
  }

  /** Same PK/same tuple is idempotent; a conflicting tuple never overwrites the first. */
  public void register(ReceiptReference reference) {
    Objects.requireNonNull(reference, "reference");
    transaction(
        connection -> {
          var statement =
              required(
                  connection.prepareStatement(
                      "insert into schubert_web_session.web_receipt_references"
                          + " (receipt_id,question_id,submitted_at) values (?,?,?)"
                          + " on conflict(receipt_id) do nothing"));
          @Nullable Throwable statementFailure = null;
          try {
            statement.setString(1, reference.receiptId());
            statement.setLong(2, reference.questionId());
            statement.setObject(3, reference.submittedAt().atOffset(ZoneOffset.UTC));
            int changed = statement.executeUpdate();
            if (changed < 0 || changed > 1) throw new SQLDataException("receipt insert count");
          } catch (SQLException | RuntimeException | Error failure) {
            statementFailure = failure;
            throw failure;
          } finally {
            try {
              statement.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              propagateCleanupFailure(statementFailure, secondary);
            }
          }
          // READ COMMITTED sees the concurrent winner after ON CONFLICT waits.
          if (!read(connection, reference.receiptId()).equals(Optional.of(reference)))
            throw new ReceiptReferenceException();
          return Boolean.TRUE;
        });
  }

  /** Completes/returns its own transaction before the caller invokes current API auth. */
  public Optional<ReceiptReference> find(String receiptId) {
    ReceiptReference.requireReceiptId(receiptId);
    return transaction(connection -> read(connection, receiptId));
  }

  private static Optional<ReceiptReference> read(Connection connection, String receiptId)
      throws SQLException {
    var statement =
        required(
            connection.prepareStatement(
                "select receipt_id,question_id,submitted_at"
                    + " from schubert_web_session.web_receipt_references where receipt_id=?"));
    @Nullable Throwable statementFailure = null;
    try {
      statement.setString(1, receiptId);
      ResultSet row = required(statement.executeQuery());
      @Nullable Throwable rowFailure = null;
      try {
        if (!row.next()) return Optional.empty();
        String actualId = required(row.getString("receipt_id"));
        Long id = required(row.getObject("question_id", Long.class));
        OffsetDateTime time = required(row.getObject("submitted_at", OffsetDateTime.class));
        ReceiptReference reference;
        try {
          reference = new ReceiptReference(actualId, id, time.toInstant());
        } catch (IllegalArgumentException invalid) {
          throw new SQLDataException("receipt projection invalid");
        }
        if (!actualId.equals(receiptId) || row.next())
          throw new SQLDataException("receipt projection identity");
        return Optional.of(reference);
      } catch (SQLException | RuntimeException | Error failure) {
        rowFailure = failure;
        throw failure;
      } finally {
        try {
          row.close();
        } catch (SQLException | RuntimeException | Error secondary) {
          propagateCleanupFailure(rowFailure, secondary);
        }
      }
    } catch (SQLException | RuntimeException | Error failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      try {
        statement.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        propagateCleanupFailure(statementFailure, secondary);
      }
    }
  }

  private <T> T transaction(Work<T> work) {
    try {
      Connection connection = required(dataSource.getConnection());
      @Nullable Throwable connectionFailure = null;
      try {
        connection.setAutoCommit(false);
        connection.setReadOnly(false);
        connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
        try {
          T result = work.execute(connection);
          connection.commit();
          return result; // owned finally close must also succeed before result escapes.
        } catch (SQLException | RuntimeException | Error failure) {
          try {
            connection.rollback();
          } catch (SQLException | RuntimeException | Error secondary) {
            propagateCleanupFailure(failure, secondary);
          }
          throw failure;
        }
      } catch (SQLException | RuntimeException | Error failure) {
        connectionFailure = failure;
        throw failure;
      } finally {
        try {
          connection.close();
        } catch (SQLException | RuntimeException | Error secondary) {
          propagateCleanupFailure(connectionFailure, secondary);
        }
      }
    } catch (SQLException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new ReceiptReferenceException();
    }
  }

  private static <T> T required(@Nullable T value) {
    if (value == null) throw new ReceiptReferenceException();
    return value;
  }

  /**
   * The owned close and rollback sites pass only their declared SQL, runtime, or error failures.
   * Keep the precedence decision shared across both normal and exceptional cleanup paths.
   */
  private static void propagateCleanupFailure(@Nullable Throwable primary, Throwable secondary)
      throws SQLException {
    if (!replace(primary, secondary)) return;
    if (secondary instanceof SQLException sql) throw sql;
    if (secondary instanceof RuntimeException runtime) throw runtime;
    throw (Error) secondary;
  }

  /** SS331/332: unknown close dominates known SQL; primary unknown retains fixed diagnostics. */
  private static boolean replace(@Nullable Throwable primary, Throwable secondary) {
    // SS312/331/332/354; SSC329; preserve the old unknown-selection policy. Only SQLs that
    // would reach the fixed catalog need this pre-discard graph check. GRAPH329001..003.
    if (primary instanceof SQLException && secondary instanceof SQLException) {
      SessionStoreException.preserveFatal(primary);
      SessionStoreException.preserveFatal(secondary);
    }
    if (primary == null
        || (primary instanceof SQLException && !(secondary instanceof SQLException))) return true;
    if (!(primary instanceof SQLException)) primary.addSuppressed(new ReceiptReferenceException());
    return false;
  }

  @FunctionalInterface
  private interface Work<T> {
    T execute(Connection connection) throws SQLException;
  }
}
