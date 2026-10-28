{
  mkShell,
  python3,
  ruff,
  pyrefly,
  nixfmt,
  pyproject-nix,
  pyharvest,
}:

let
  project = import ./project.nix { inherit pyproject-nix; };
  # Editable, so importlib.metadata finds the dist and edits need no rebuild.
  editable = python3.pkgs.mkPythonEditablePackage {
    inherit (pyharvest) pname version;
    inherit (project.pyproject.project) scripts;
    root = "$PYHARVEST_ROOT/src";
  };
  python = python3.withPackages (
    ps:
    project.renderers.withPackages {
      python = python3;
      extras = [ "mcp" ];
      groups = [ "test" ];
    } ps
    ++ [ editable ]
  );
in
mkShell {
  packages = [
    python
    ruff
    pyrefly
    nixfmt
  ];
  shellHook = ''
    export PYHARVEST_ROOT="$PWD"
  '';
}
