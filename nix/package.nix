{
  lib,
  python,
  buildPythonPackage,
  pytestCheckHook,
  pyproject-nix,
}:

let
  project = import ./project.nix { inherit pyproject-nix; };
  attrs = project.renderers.buildPythonPackage { inherit python; };
in
buildPythonPackage (
  attrs
  // {
    # Only what the build reads, not the whole projectRoot the renderer sets.
    src = lib.fileset.toSource {
      root = ../.;
      fileset = lib.fileset.unions [
        ../pyproject.toml
        ../README.md
        ../src
        ../tests
      ];
    };

    nativeCheckInputs = [ pytestCheckHook ] ++ attrs.passthru.dependency-groups.test;
    pythonImportsCheck = [ "pyharvest" ];

    meta = attrs.meta // {
      license = lib.licenses.mit;
    };
  }
)
