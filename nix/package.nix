{
  lib,
  python,
  buildPythonPackage,
  pytestCheckHook,
  pyproject-nix,
  extras,
}:

let
  project = import ./project.nix { inherit pyproject-nix; };
  attrs = project.renderers.buildPythonPackage { inherit python extras; };
in
buildPythonPackage (
  attrs
  // {
    # Only what the build reads, not the whole projectRoot the renderer sets.
    src = lib.fileset.toSource {
      root = ../.;
      fileset = lib.fileset.unions [
        ../LICENSE
        ../pyproject.toml
        ../README.md
        ../src
        ../tests
      ];
    };

    nativeCheckInputs = [ pytestCheckHook ] ++ attrs.passthru.dependency-groups.test;
    pythonImportsCheck = [ "pyharvest" ];

    meta = attrs.meta // {
      license = lib.licenses.asl20;
      mainProgram = "pyharvest-mcp";
    };
  }
)
