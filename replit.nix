{pkgs}: {
  deps = [
    pkgs.zlib
    pkgs.pkg-config
    pkgs.grpc
    pkgs.c-ares
    pkgs.kubo
    pkgs.postgresql
    pkgs.openssl
  ];
}
