FROM node:22-bookworm-slim AS web-build
WORKDIR /build
ENV NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
RUN npm ci
COPY app ./app
COPY lib ./lib
COPY data ./data
COPY public ./public
COPY next.config.ts tsconfig.json postcss.config.mjs ./
RUN npm run build

FROM python:3.11-slim-bookworm AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libstdc++6 libatomic1 && rm -rf /var/lib/apt/lists/*
COPY --from=web-build /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY backend/requirements.lock ./backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY backend ./backend
COPY scripts/run.mjs ./scripts/run.mjs
COPY --from=web-build /build/.next/standalone ./web
COPY --from=web-build /build/.next/static ./web/.next/static
COPY --from=web-build /build/public ./web/public
RUN useradd --create-home --uid 10001 nivaar && chown -R nivaar:nivaar /app
USER nivaar
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PYTHONUNBUFFERED=1 STANDALONE_SERVER=/app/web/server.js PORT=10000
EXPOSE 10000
CMD ["node","scripts/run.mjs","start"]
