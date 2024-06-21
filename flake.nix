# taken from https://github.com/DeterminateSystems/zero-to-nix/blob/main/nix/templates/dev/python/flake.nix
{
  description = "Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pname = "python dev environment";
      pkgs = import nixpkgs {inherit system;};
      python = pkgs.python311;
    in {
      formatter = pkgs.alejandra;

      # Development environment output
      devShell = pkgs.mkShell rec {
        # The Nix packages provided in the environment
        packages = [
          # Python plus helper tools
          (python.withPackages (ps: with ps; [virtualenv pip]))
          # specific to this project
          pkgs.geckodriver
        ];
        nativeBuildInputs = with pkgs; [
          gcc.cc
          zlib
        ];

        shellHook = ''
          if [[ ! -d .venv ]]; then
            echo "No virtual env found at ./.venv, creating a new virtual env linked to the Python site defined with Nix. Make sure to install your requirements."
            ${python}/bin/python -m venv .venv
          fi
          source .venv/bin/activate
          echo "Nix development shell loaded."

          # to be able to import numpy, on aarch64 linux
          export LD_LIBRARY_PATH="${pkgs.lib.strings.makeLibraryPath (with pkgs; [ gcc.cc zlib ])}"

          # specific to this project
          export PATH="$PATH:/Applications/Firefox.app/Contents/MacOS"
        '';
      };

      # Ideally, we could run the panel app in the flake output,
      # but i have not managed to make it work yet
      # packages.client = pkgs.writeScriptBin "client-script" ''
      #   ${python}/bin/python --version
      # '';
      # apps = {
      #   type = "app";
      #   program = "${self.packages.runme}/bin/runme";
      #   #          program = "${pkgs.python3}/bin/python";
      #   #          args = [ "--version" ];
      #   #          src = "./.";
      # };
    });
}
