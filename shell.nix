let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.requests
      python-pkgs.beautifulsoup4
      python-pkgs.markdown
      python-pkgs.ebooklib
    ]))
  ];
}
