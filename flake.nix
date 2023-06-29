{
  description = "Spex development environment flake";

  inputs = { nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05"; };

  outputs = { self, nixpkgs }:
    let
      allSystems = [
        "x86_64-linux" # AMD/Intel Linux
        "x86_64-darwin" # AMD/Intel macOS
        "aarch64-linux" # ARM Linux
        "aarch64-darwin" # ARM macOS
      ];

      forAllSystems = fn:
        nixpkgs.lib.genAttrs allSystems
        (system: fn { pkgs = import nixpkgs { inherit system; }; });

      revision = "${self.lastModifiedDate}-${self.shortRev or "dirty"}";
    in {
      # used when calling `nix fmt <path/to/flake.nix>`
      formatter = forAllSystems ({ pkgs }: pkgs.nixfmt);

      packages = forAllSystems ({ pkgs }:
        let
          buildPythonPackage = pkgs.python311Packages.buildPythonPackage;
          fetchPypi = pkgs.python311Packages.fetchPypi;
        in rec {
          gcgen = (buildPythonPackage rec {
                  pname = "gcgen";
                  version = "0.1.0";
                  src = fetchPypi {
                    inherit pname version;
                    sha256 = "533b494e0df66a9b6d0de3b1c92d6ab2bb92d6b8df4283d838f1bb2ac4dd432c";
                  };
                  doCheck = false;
                  propagatedBuildInputs = [];
                  meta = {};
          });
          lxml-stubs = (buildPythonPackage rec {
                  pname = "lxml-stubs";
                  version = "0.4.0";
                  src = fetchPypi {
                    inherit pname version;
                    sha256 = "sha256-GEh3tCEnJWq8K5MrqL0KteqAvQsP7mGNFtqkDgtxq+4=";
                  };
                  doCheck = false;
                  propagatedBuildInputs = [];
          });
          loguru = (buildPythonPackage rec {
                  pname = "loguru";
                  version = "0.7.0";
                  src = fetchPypi {
                    inherit pname version;
                    sha256 = "sha256-FhIFPO1q6E15Wd19XkMaBTJkIjfsIff9g6xz/lOeA+E=";
                  };
                  doCheck = false;
                  propagatedBuildInputs = [];
          });
          spex = (buildPythonPackage rec {
                  pname = "spex";
                  version = revision;
                  src = ./.;
                  doCheck = false;
                  propagatedBuildInputs = (with pkgs.python311Packages; [
                    lxml jsonschema
                  ]) ++ (with self.packages.${pkgs.system}; [
                    lxml-stubs loguru gcgen]);
          });
          dockerImage = pkgs.dockerTools.buildLayeredImage {
            name = "spex";
            tag = revision;
            contents = [
              spex
            ];
          };
      });

      # nix develop <flake-ref>#<name>
      # -- 
      # $ nix develop <flake-ref>#blue
      # $ nix develop <flake-ref>#yellow
      devShells = forAllSystems ({ pkgs }:
        let
          upstream = with pkgs; [
            gcc-unwrapped
            (python311.withPackages (pypkgs: with pypkgs; [
              lxml jsonschema mypy isort black flake8
            ]))];
          custom = with self.packages.${pkgs.system}; [
            gcgen lxml-stubs loguru
          ];
        in {
        default = pkgs.mkShell {
          name = "default";
          nativeBuildInputs =  upstream ++ custom;
          shellHook = ''
            unset SOURCE_DATA_EPOCH
            export SPEX_NIX_ENV=1
          '';
        };
      });
    };
}
