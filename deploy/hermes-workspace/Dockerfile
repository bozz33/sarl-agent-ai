# Reconstruction de sarl/hermes-workspace depuis le source.
#
# IMPORTANT — lire deploy/hermes-workspace/README.md.
# Clone l'upstream au commit epingle, applique les patches SARL versionnes dans
# patches/ (sarl13-no-global-sse), puis build. Reproduit l'image en production
# (tag d04e1f3-sarl13-no-global-sse).
#
# Build : docker build -t sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse deploy/hermes-workspace
# (volontairement HORS docker-compose pour ne pas ecraser l'image en prod par un
#  `docker compose up --build`.)

FROM node:22-slim AS build

ARG HERMES_WORKSPACE_REPO=https://github.com/outsourc-e/hermes-workspace.git
ARG HERMES_WORKSPACE_REF=d04e1f3

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN corepack enable

WORKDIR /app

# Source upstream epingle.
RUN git clone "${HERMES_WORKSPACE_REPO}" . \
    && git checkout "${HERMES_WORKSPACE_REF}"

# Patches SARL (optionnels tant qu'ils ne sont pas recuperes — cf. README).
COPY patches/ /tmp/sarl-patches/
RUN if ls /tmp/sarl-patches/*.patch >/dev/null 2>&1; then \
        for p in /tmp/sarl-patches/*.patch; do echo "apply $p"; git apply "$p"; done; \
    fi

RUN pnpm install --frozen-lockfile \
    && pnpm build

FROM node:22-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app ./
EXPOSE 3000
CMD ["node", "server-entry.js"]
