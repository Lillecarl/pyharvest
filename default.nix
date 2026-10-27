let
  compat = import ./nix/compat.nix;
in
{
  inputs ? compat.inputs,
  system ? builtins.currentSystem,
  # Empty config and overlays: without them nixpkgs reads ~/.config/nixpkgs.
  pkgs ? import inputs.nixpkgs {
    inherit system;
    config = { };
    overlays = [ ];
  },
}:

let
  # Built with the consumer's lib, not the flake's.
  pyproject-nix = import inputs.pyproject-nix { inherit (pkgs) lib; };
  pyharvest = pkgs.python3Packages.callPackage ./nix/package.nix { inherit pyproject-nix; };
in
{
  inherit pyharvest;
  default = pyharvest;

  shell = pkgs.callPackage ./nix/shell.nix { inherit pyproject-nix pyharvest; };
  # callPackages, not callPackage: the latter adds `override` to the set,
  # and `nix flake check` rejects a check that is not a derivation.
  checks = pkgs.callPackages ./nix/checks.nix { inherit pyharvest; };
  formatter = pkgs.nixfmt-tree;
}
