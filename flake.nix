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

    in {
      # used when calling `nix fmt <path/to/flake.nix>`
      formatter = forAllSystems ({ pkgs }: pkgs.nixfmt);

      # nix develop <flake-ref>#<name>
      # -- 
      # $ nix develop <flake-ref>#blue
      # $ nix develop <flake-ref>#yellow
      devShells = forAllSystems ({ pkgs }: {
        default = pkgs.mkShell {
          name = "default";
          venvDir = "./.venv";
          nativeBuildInputs = with pkgs; [
            gcc-unwrapped
            (python311.withPackages (pypkgs: with pypkgs; [
              virtualenv pip venvShellHook lxml jsonschema
              (buildPythonPackage rec {
                pname = "gcgen"; 
                version = "0.1.0";
                src = fetchPypi {
                  inherit pname version;
                  sha256 = "533b494e0df66a9b6d0de3b1c92d6ab2bb92d6b8df4283d838f1bb2ac4dd432c";
                };
                doCheck = false;
                propagatedBuildInputs = [];
                meta = {};
              })
              (buildPythonPackage rec {
                pname = "lxml-stubs";
                version = "0.4.0";
                src = fetchPypi {
                  inherit pname version;
                  sha256 = "sha256-GEh3tCEnJWq8K5MrqL0KteqAvQsP7mGNFtqkDgtxq+4=";
                };
                doCheck = false;
                propagatedBuildInputs = [
                ];
              })
              (buildPythonPackage rec {
                pname = "loguru";
                version = "0.7.0";
                src = fetchPypi {
                  inherit pname version;
                  sha256 = "sha256-FhIFPO1q6E15Wd19XkMaBTJkIjfsIff9g6xz/lOeA+E=";
                };
                doCheck = false;
                propagatedBuildInputs = [];
              })
            ]))
          ];
          postVenv = ''
            unset SOURCE_DATA_EPOCH
          '';
          postShellHook = ''
            PYTHONPATH=$PWD/$venvDir/${pkgs.python311.sitePackages}:$PYTHONPATH
          '';
        };
      });
    };
}
