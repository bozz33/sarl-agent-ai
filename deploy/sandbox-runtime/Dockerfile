FROM nikolaik/python-nodejs:python3.11-nodejs20

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV NODE_PATH=/usr/local/lib/node_modules

RUN npm install -g playwright \
    && playwright install --with-deps chromium \
    && chmod -R a+rX /ms-playwright /usr/local/lib/node_modules/playwright
