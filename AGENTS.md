# pyharvest

Async client for https://help.getharvest.com/api-v2/. anyio, httpx, pydantic.

## Layout

- `src/pyharvest/_session.py`: HTTP, errors, 429 retry, pagination. Resources never touch httpx.
- `src/pyharvest/models/<section>.py`: response models (`HarvestModel`) and request bodies (`HarvestInput`).
- `src/pyharvest/resources/<section>.py`: one thin class per endpoint group, attached in `client.py` as a flat attribute named after the doc page (`invoice_payments`, not `invoices.payments`). Sub-resources take the parent id first.
- `pyharvest.models` exports base types only; sections reuse short names, so import `pyharvest.models.<section>`. Cross-section imports are fine where a type is truly shared (`BudgetBy` from projects).

## Conventions

- Response fields: required when docs and live data agree it is always present. `X | None = None` when permission-gated (member accounts lack rates) or seen null.
- Nested `{id, name}` stubs: `Ref`, or a `Ref` subclass when live adds keys.
- Money and hours in responses: `Decimal`. In inputs: `float` (pydantic's JSON mode dumps Decimal as a string).
- Times of day (`started_time`): `str`; format follows the account's clock setting.
- Closed "Possible values" sets: `StrEnum`, annotated `Open[E]` on responses so a new value stays `str`. Open-ended sets (currencies, kinds, services): plain `str`.
- Wire names that are not valid fields (`from`, `_destroy`): `Field(alias=...)` only; `HarvestInput` already serialises by alias.
- Writes take a `HarvestInput` model; `send()` dumps `exclude_unset=True`, so an explicit `None` sends `null` and clears the field. Never kwargs-with-None-dropped.
- List methods return `AsyncIterator` from `session.paginate`. Query param `from` is spelled `from_`.
- Inside a resource class, `list[...]` in an annotation after `def list` resolves to the method: use `Sequence` or keep list types in models.
- Datetime query params must be timezone-aware; `query()` raises otherwise.

## Adding a resource

1. Doc page to markdown (curl + html2text into the scratchpad); read the attribute and parameter tables.
2. Dump live keys with a GET (never POST/PATCH/DELETE: the account holds real data). Keep raw responses out of the repo.
3. Model, resource, respx test with synthetic fixtures in `tests/fixtures_<section>.py` (`tests/fixtures.py` holds `page()` and the core records).
4. Add `(path, key, Model, params)` to `tests/test_live.py` (single objects go in the objects table); it reports live keys the model lacks.

## Known gaps

- Multipart is unsupported: expense receipt upload, `POST /v2/imports`.
- The dev account is a member: most sections 403 and PTO/approvals/reimbursements are disabled, so those models follow the docs. An admin token run of `tests/test_live.py` validates them.
- Unverified: PTO `user_ids`/`pto_type_ids` are sent comma-joined (Rails may want `user_ids[]`); detailed report `totals` are dropped by `paginate`.

## MCP server

- `src/pyharvest/mcp.py`, mcp 2.x (`MCPServer`, not v1 `FastMCP`; the pinned nixpkgs has 2.2). `create_server(connect)` takes a `Harvest` factory; tests pass one hitting respx.
- `.mcp.json` runs `nix run --file . pyharvest-mcp`; an edit reaches Claude Code on server restart (`/mcp`), after a rebuild. That attr skips tests; `pyharvest` runs them.
- Credentials: inherited env (direnv loads `.privenv`). No `env` block in `.mcp.json`: it is committed.
- stdout is the protocol: never print. `log_level="WARNING"` keeps httpx request logs off stderr.
- Tool args reuse `HarvestInput` models, so update keeps unset-vs-null. Mark writes in docstrings and `ToolAnnotations`.
- Results cost the caller's context: list/write tools return compact `Result` models (`EntryRow`, `AssignedProject`); full records only from `get_time_entry` and `harvest_get`. Shaping is pure functions (`to_row`, `summarise`), tested without a server. Field docstrings reach the output schema (`use_attribute_docstrings`).
- Wrap Harvest calls in `with reported():`. MCPServer hides any exception text except `ToolError`'s.
- `harvest_get` is the escape hatch for every other section; `API_PATH` keeps the token on the Harvest host. No generic write tool: writes go through input models.
- Iterate: edit, `nix build --file . pyharvest-mcp`, then pymux `pane.send` `/mcp reconnect pyharvest` into this session's pane (`tree`, `"here": true`, `no_paste`) and end the turn so it runs.
- Smoke test outside Claude Code: `mcp.Client(StdioServerParameters(command="nix", args=[...], env=dict(os.environ)))`; stdio_client passes a minimal env unless given one.

## Checks

- `pytest` in the direnv shell runs live tests when `HARVEST_TOKEN`/`HARVEST_ACCOUNT` are set (`.privenv`).
- `nix build --file . checks`: build + offline tests, ruff, nixfmt. Live tests skip in the sandbox.
- `pyrefly check src tests`.
