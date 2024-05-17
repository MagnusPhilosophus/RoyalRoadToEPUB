let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  nativebuildInputs = with pkgs.buildPackages; [
    playwright
    playwright-driver.browsers
  ];
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.requests
      python-pkgs.beautifulsoup4
      python-pkgs.markdown
      python-pkgs.ebooklib
      python-pkgs.playwright
    ]))
  ];
  shellHook = ''
      export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
      export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
  '';
}
