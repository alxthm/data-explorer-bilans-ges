let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
    packages = [pkgs.geckodriver];
    shellHook = ''
        export PATH="$PATH:/Applications/Firefox.app/Contents/MacOS"
    '';
}