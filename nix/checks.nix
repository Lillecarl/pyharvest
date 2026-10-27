{
  lib,
  runCommand,
  nixfmt,
  ruff,
  pyharvest,
}:

let
  source =
    filter:
    lib.fileset.toSource {
      root = ../.;
      fileset = lib.fileset.fileFilter filter ../.;
    };
in
{
  inherit pyharvest;

  nixfmt = runCommand "nixfmt-check" { nativeBuildInputs = [ nixfmt ]; } ''
    find ${source (file: file.hasExt "nix")} -name '*.nix' -exec nixfmt --check {} +
    touch $out
  '';

  ruff =
    runCommand "ruff-check"
      {
        nativeBuildInputs = [ ruff ];
        src = source (file: file.hasExt "py" || file.name == "pyproject.toml");
      }
      ''
        cd "$src"
        ruff check --no-cache .
        ruff format --no-cache --check .
        touch $out
      '';
}
