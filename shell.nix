let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix/";
    ref = "refs/tags/2.3.0";
  });
in
mach-nix.mkPythonShell {
  python = mach-nix.nixpkgs.python38;
  requirements = builtins.readFile ./requirements.txt;
}
