{
  inputs.systems.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.mach-nix = {
    url = "github:DavHau/mach-nix/8d903072c7b5426d90bc42a008242c76590af916";
  };

  outputs = { self, flake-utils, nixpkgs, mach-nix, ... }:
    let
      pythonVersion = "python39";
    in
    flake-utils.lib.eachDefaultSystem (system: 
      let
        inherit (nixpkgs.lib) optional;
        pkgs = import nixpkgs { inherit system; };
        mach = mach-nix.lib.${system};

        pythonApp = mach.buildPythonApplication ./.;
        pythonAppEnv = mach.mkPython {
          python = pythonVersion;
          requirements = builtins.readFile ./requirements.txt;
        };
        pythonAppImage = pkgs.dockerTools.buildLayeredImage {
          name = pythonApp.pname;
          contents = [ pythonApp ];
          config.Cmd = [ "${pythonApp}/bin/main" ];
        };
      in
      rec {
        packages = rec {
          pythonPkg  = pythonApp;
          default = packages.pythonPkg;
        };

        apps.default = rec {
          type = "app";
          program = "${packages.pythonPkg}/bin/serv.py";
        };
      });
}
