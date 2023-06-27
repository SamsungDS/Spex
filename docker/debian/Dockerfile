FROM debian:bookworm
LABEL maintainer "os@safl.dk"
# This is for pipx
ENV PATH=$PATH:/root/.local/bin
COPY ./docker/debian/pkgs.sh /tmp/.
RUN /tmp/pkgs.sh
