package dev.codex.schubert.nk.api.application.question;

/** Replaceable provider only; NK-ASY-001/QST003/101; UI224/236; SS311/312; PG190/STB001..005. */
@FunctionalInterface
public interface AnswerProvider {
  AnswerResult answer(String question);
}
