# pyharvest

Async Python client for the [Harvest API v2](https://help.getharvest.com/api-v2/).

```python
import datetime as dt

from pyharvest import Harvest
from pyharvest.models.time_entries import TimeEntryUpdate

async with Harvest(
    access_token="...",
    account_id="...",
    user_agent="MyApp (me@example.com)",
) as harvest:
    me = await harvest.users.me()
    async for entry in harvest.time_entries.list(
        from_=dt.date(2026, 10, 1), to=dt.date(2026, 10, 31)
    ):
        print(entry.spent_date, entry.project.name, entry.hours)
    # None clears a field; fields left out stay unchanged.
    await harvest.time_entries.update(123, TimeEntryUpdate(notes=None))
```

`Harvest.from_env(user_agent=...)` reads `HARVEST_TOKEN` and `HARVEST_ACCOUNT`.

Each API section is a flat attribute on `Harvest`, named after its doc page
(`harvest.invoices`, `harvest.invoice_payments`, `harvest.reports`, ...). Its
models are in `pyharvest.models.<section>`. List methods return async
iterators that follow pagination for you.

Not supported yet: expense receipt upload and `POST /v2/imports`. Both need
multipart requests.

## MCP server

`pyharvest-mcp` serves one Harvest account to an MCP client over stdio. It
lists your projects and logs, edits and summarises time entries and timers.

Create a personal access token at <https://id.getharvest.com/developers>. The
same page shows your account ID. The server reads both from the environment:

```sh
export HARVEST_TOKEN=...
export HARVEST_ACCOUNT=...
nix run github:Lillecarl/pyharvest#pyharvest-mcp
# without flakes:
nix run --file https://github.com/Lillecarl/pyharvest/archive/main.tar.gz pyharvest-mcp
```

Claude Code:

```sh
claude mcp add pyharvest -- nix run github:Lillecarl/pyharvest#pyharvest-mcp
```

Other clients (`mcpServers` JSON):

```json
{
  "mcpServers": {
    "pyharvest": {
      "command": "nix",
      "args": ["run", "github:Lillecarl/pyharvest#pyharvest-mcp"],
      "env": { "HARVEST_TOKEN": "...", "HARVEST_ACCOUNT": "..." }
    }
  }
}
```

Leave out `env` when the client inherits a shell that already exports both.
Write tools change real data.

## Development

```sh
nix build --file . pyharvest      # build and run the offline tests
nix build --file . checks         # every check
nix develop --file . shell        # or nix-shell, or direnv
pytest                            # in the shell; live tests run when
                                  # HARVEST_TOKEN and HARVEST_ACCOUNT are set
```

## License

Copyright Dynamist AB. Licensed under the [Apache License 2.0](LICENSE).
