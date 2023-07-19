{
  description = "Python application flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    mach-nix.url = "github:davhau/mach-nix";
  };

  outputs = { self, nixpkgs, mach-nix, flake-utils, ... }:
    let
      pythonVersion = "python39";
    in
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        mach = mach-nix.lib.${system};

        pythonApp =
          let
            pythonEnv = pkgs.python39.withPackages (ps: [
              ps.flask
            ]);
          in
          pkgs.stdenv.mkDerivation {
            name = "wrc";
            packages = [
              pythonEnv
            ];
            src = ./.;
            installPhase = ''
              mkdir -p $out
              cp -rv $src/* $out/
              chmod u+x $out/app/serv.py
            '';
            environment.sessionVariables = "PYTHONPATH=${pythonEnv}";
            
          };

        pythonAppEnv = mach.mkPython {
          python = pythonVersion;
          requirements = "flask";
        };
        pythonAppImage = pkgs.dockerTools.buildLayeredImage {
          name = pythonApp.pname;
          contents = [ pythonApp ];
          config.Cmd = [ "${pythonApp}/bin/main" ];
        };
      in
      rec
      {
        packages = {
          image = pythonAppImage;

          pythonPkg = pythonApp;
          default = packages.pythonPkg;
        };

        apps.default = {
          type = "app";
          program = "${packages.pythonPkg}/app/serv.py";
        };

        devShells.default = pkgs.mkShellNoCC {
          packages = [ pythonAppEnv ];

          shellHook = ''
            export PYTHONPATH="${pythonAppEnv}/bin/python"
          '';
        };
      }
    );
}

