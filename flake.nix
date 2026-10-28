{
  description = "Async client for the Harvest API v2";

  inputs = {
    nixpkgs.url = "https://channels.nixos.org/nixpkgs-unstable/nixexprs.tar.xz";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # Read by nix/compat.nix, so default.nix uses this same lock.
    flake-compatish.url = "github:lillecarl/flake-compatish";
  };

  # A wrapper. Every output is an attribute of default.nix.
  outputs =
    inputs:
    let
      inherit (inputs.nixpkgs) lib;

      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      # Not legacyPackages: it reads ~/.config/nixpkgs when evaluation is
      # impure, and flake-compatish evaluates these outputs impurely.
      perSystem = lib.genAttrs systems (system: import ./default.nix { inherit inputs system; });
      forAllSystems = f: lib.mapAttrs (_: f) perSystem;
    in
    {
      packages = forAllSystems (p: {
        inherit (p) default pyharvest pyharvest-mcp;
      });
      devShells = forAllSystems (p: {
        default = p.shell;
      });
      checks = forAllSystems (p: p.checks);
      formatter = forAllSystems (p: p.formatter);
    };
}
