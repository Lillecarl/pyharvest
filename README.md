# pyharvest

Async Python client for the [Harvest API v2](https://help.getharvest.com/api-v2/).

```python
from pyharvest import Harvest

async with Harvest(
    access_token="...",
    account_id="...",
    user_agent="MyApp (me@example.com)",
) as harvest:
    me = await harvest.me()
```

## Development

```sh
nix build --file . pyharvest      # build and run the tests
nix build --file . checks         # every check
nix develop --file . shell        # or nix-shell
```
