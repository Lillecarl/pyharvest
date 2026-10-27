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

## Development

```sh
nix build --file . pyharvest      # build and run the offline tests
nix build --file . checks         # every check
nix develop --file . shell        # or nix-shell, or direnv
pytest                            # in the shell; live tests run when
                                  # HARVEST_TOKEN and HARVEST_ACCOUNT are set
```
