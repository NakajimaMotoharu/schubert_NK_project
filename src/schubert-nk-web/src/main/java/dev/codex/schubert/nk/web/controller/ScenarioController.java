package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.*;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.form.ScenarioSearchForm;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.messaging.ScenarioWireException;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * Protected GET hierarchy; API revalidates context. NK-WEB-002/SCR004..006/FUN004/AUT/SYS006;
 * UI221..223/234/264; SS313/314/323/352; SSC071/PG194/PT-SCR-001..016. Nullable endpoint returns
 * mean only HTTP already handled by Spring MVC; helpers are non-null.
 */
@Controller
@NullMarked
public final class ScenarioController {
  private final ScenarioWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();

  public ScenarioController(ScenarioWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
  }

  /** SCR003/FUN003/UI223,234/SS313/SSC072/PG203/PT-SCR034..045. */
  @GetMapping("/search")
  public @Nullable String search(
      @RequestParam MultiValueMap<String, String> parameters,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    var form = ScenarioSearchForm.bind(parameters);
    if (!form.isValid()) {
      response.setStatus(400);
      model.addAttribute("page", ScenarioSearchViewModel.invalid(actor, form));
      return "search";
    }
    var query = form.toRequest();
    var search =
        exchange(
            new TypedPayloadValues(new LayoutId("SRCREQ01"), query, List.of()),
            actor,
            request,
            response);
    if (search.isEmpty()) return null;
    var games =
        exchange(
            new TypedPayloadValues(new LayoutId("GAMREQ01"), new GameListRequestData(), List.of()),
            actor,
            request,
            response);
    if (games.isEmpty()) return null;
    var speakers =
        exchange(
            new TypedPayloadValues(
                new LayoutId("SPKREQ01"), new SpeakerListRequestData(query.gameCode()), List.of()),
            actor,
            request,
            response);
    if (speakers.isEmpty()) return null;
    final ScenarioSearchViewModel page;
    try {
      page =
          ScenarioSearchViewModel.success(
              actor,
              form,
              games.orElseThrow().records().stream().map(record -> (GameRecord) record).toList(),
              speakers.orElseThrow().records().stream()
                  .map(record -> (SpeakerRecord) record)
                  .toList(),
              (PagedResponseData) search.orElseThrow().data(),
              search.orElseThrow().records().stream()
                  .map(record -> (ScenarioSearchRecord) record)
                  .toList());
    } catch (IllegalArgumentException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "search";
  }

  @GetMapping("/scenarios")
  public @Nullable String games(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    var result =
        exchange(
            new TypedPayloadValues(new LayoutId("GAMREQ01"), new GameListRequestData(), List.of()),
            actor,
            request,
            response);
    if (result.isEmpty()) return null;
    var records =
        result.orElseThrow().records().stream().map(record -> (GameRecord) record).toList();
    model.addAttribute("page", GameListViewModel.from(actor, records));
    return "scenarios";
  }

  @GetMapping("/scenarios/{game:NUKITASHI[12]}")
  public @Nullable String routes(
      @PathVariable("game") String game,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    var selected = game(game);
    var result =
        exchange(
            new TypedPayloadValues(
                new LayoutId("RTEREQ01"), new RouteListRequestData(selected), List.of()),
            actor,
            request,
            response);
    if (result.isEmpty()) return null;
    var records =
        result.orElseThrow().records().stream().map(record -> (RouteRecord) record).toList();
    if (records.isEmpty()) {
      response.sendError(404);
      return null;
    }
    model.addAttribute("page", RouteListViewModel.from(actor, selected, records));
    return "scenario-routes";
  }

  @GetMapping("/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}")
  public @Nullable String files(
      @PathVariable("game") String game,
      @PathVariable("prefix") String prefix,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    var selected = game(game);
    Objects.requireNonNull(prefix, "prefix");
    if (!prefix.matches("[0-9]{2}")) throw new IllegalArgumentException("invalid route prefix");
    int number = Integer.parseInt(prefix);
    var result =
        exchange(
            new TypedPayloadValues(
                new LayoutId("SCFREQ01"),
                new ScenarioFileListRequestData(selected, number),
                List.of()),
            actor,
            request,
            response);
    if (result.isEmpty()) return null;
    var payload = result.orElseThrow();
    var data = (ScenarioFileListResponseData) payload.data();
    if (data.gameCode() != selected || data.prefix() != number) {
      response.sendError(503);
      return null;
    }
    var records = payload.records().stream().map(record -> (ScenarioFileRecord) record).toList();
    if (records.isEmpty()) {
      response.sendError(404);
      return null;
    }
    model.addAttribute(
        "page", ScenarioFileListViewModel.from(actor, selected, number, data.routeName(), records));
    return "scenario-files";
  }

  private Optional<TypedPayloadValues> exchange(
      TypedPayloadValues input,
      SessionPrincipal actor,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    final ScenarioWireClient.Result result;
    try {
      result = client.exchange(input, actor.authenticationContext());
    } catch (ScenarioWireException failure) {
      response.sendError(503);
      return Optional.empty();
    }
    if (result.resultCode() == ResultCode.SESSION_INVALID) {
      invalid.handle(request, response);
      return Optional.empty();
    }
    int status = mapper.httpStatus(result.resultCode());
    if (status != 200) {
      response.sendError(status);
      return Optional.empty();
    }
    return result.payload();
  }

  private static SessionPrincipal actor(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(principal, "principal");
    Objects.requireNonNull(model, "model");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(principal instanceof SessionPrincipal actor)) throw new SessionStoreException();
    return actor;
  }

  private static GameCode game(String value) {
    Objects.requireNonNull(value, "game");
    return switch (value) {
      case "NUKITASHI1" -> GameCode.NUKITASHI_1;
      case "NUKITASHI2" -> GameCode.NUKITASHI_2;
      default -> throw new IllegalArgumentException("unsupported game");
    };
  }
}
