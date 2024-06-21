# taken from https://github.com/DeterminateSystems/zero-to-nix/blob/main/nix/templates/dev/python/flake.nix
{
  description = "Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      allSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      # Helper to provide system-specific attributes
      forAllSystems = f: nixpkgs.lib.genAttrs allSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in
    {
      # Development environment output
      devShells = forAllSystems ({ pkgs }: {
        default =
          let
            python = pkgs.python311;
          in
          pkgs.mkShell {
            # The Nix packages provided in the environment
            packages = [
              # Python plus helper tools
              (python.withPackages (ps: with ps; [
                virtualenv
                pip
              ]))
              # specific to this project
              pkgs.geckodriver
            ];

            shellHook = ''
            if [[ ! -d .venv ]]; then
              echo "No virtual env found at ./.venv, creating a new virtual env linked to the Python site defined with Nix. Make sure to install your requirements."
              ${python}/bin/python -m venv .venv
            fi
            source .venv/bin/activate
            echo "Nix development shell loaded."

            # specific to this project
            export PATH="$PATH:/Applications/Firefox.app/Contents/MacOS"
          '';
          };
      });
    };
}