# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

{
  description = "Spex development environment flake";

  inputs = { nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11"; };

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

      revision = "${self.shortRev or "dirty"}";

      # packages only necessary for a development/CI environment
      devPackages = pkgs:
        (with pkgs.python311Packages; [
          pip
          jsonschema
          mypy
          isort
          black
          flake8
          sphinx
          sphinx-copybutton
          furo
          twine
          wheel
          build
        ]) ++ (with pkgs; [
          # tools needed directly or indirectly by Makefile and ./scripts
          gnugrep
          gnumake
          gawk
          bash
        ]);

      # package necessary for Spex to run
      spexDeps = pkgs:
        (with pkgs.python311Packages; [ lxml ])
        ++ (with self.packages.${pkgs.system}; [ lxml-stubs loguru gcgen types-jsonschema ]);
    in {
      # used when calling `nix fmt <path/to/flake.nix>`
      formatter = forAllSystems ({ pkgs }: pkgs.nixfmt);

      packages = forAllSystems ({ pkgs }:
        let
          buildPythonPackage = pkgs.python311Packages.buildPythonPackage;
          fetchPypi = pkgs.python311Packages.fetchPypi;
        in rec {
          # third-party dependencies
          gcgen = (buildPythonPackage rec {
            pname = "gcgen";
            version = "0.1.0";
            src = fetchPypi {
              inherit pname version;
              sha256 =
                "533b494e0df66a9b6d0de3b1c92d6ab2bb92d6b8df4283d838f1bb2ac4dd432c";
            };
            doCheck = false;
            propagatedBuildInputs = [ ];
            meta = { };
          });
          lxml-stubs = (buildPythonPackage rec {
            pname = "lxml-stubs";
            version = "0.4.0";
            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-GEh3tCEnJWq8K5MrqL0KteqAvQsP7mGNFtqkDgtxq+4=";
            };
            doCheck = false;
            propagatedBuildInputs = [ ];
          });
          loguru = (buildPythonPackage rec {
            pname = "loguru";
            version = "0.7.0";
            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-FhIFPO1q6E15Wd19XkMaBTJkIjfsIff9g6xz/lOeA+E=";
            };
            doCheck = false;
            propagatedBuildInputs = [ ];
          });
          types-jsonschema = (buildPythonPackage rec {
            pname = "types-jsonschema";
            version = "4.21.0.20240331";
            src = fetchPypi {
              inherit pname version;
              sha256 = "3a5ed0a72ab7bc304ca4accbb709272c620f396abf2fb19570b80d949e357eb6";
            };

            # Package does not have any tests
            doCheck = false;
            propagatedBuildInputs = [];

            meta = {
              description = "Typing stubs for jsonschema";
              homepage = "https://github.com/python/typeshed";
              license = pkgs.lib.licenses.asl20;
            };
          });

          # spex packages
          spex = (buildPythonPackage rec {
            pname = "spex";
            version = revision;
            format = "setuptools";
            src = ./.;
            doCheck = false;
            propagatedBuildInputs = (spexDeps pkgs);
          });
          dockerImage = pkgs.dockerTools.buildLayeredImage {
            name = "spex";
            tag = revision;
            contents = [ spex ];
          };
        });

      # nix develop <flake-ref>#<name>
      # -- 
      # $ nix develop <flake-ref>#blue
      # $ nix develop <flake-ref>#yellow
      devShells = forAllSystems ({ pkgs }:
        let
        in {
          default = pkgs.mkShell {
            name = "default";
            nativeBuildInputs = (spexDeps pkgs) ++ (devPackages pkgs);
            shellHook = ''
              unset SOURCE_DATE_EPOCH
              export SPEX_NIX_ENV=1
              # run spex from module in src dir
              alias spex="PYTHONPATH=./src:$PYTHONPATH python -m spex"
            '';
          };
        });
    };
}
