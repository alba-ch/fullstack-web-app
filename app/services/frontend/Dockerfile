FROM node:lts-alpine

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

RUN npm install @vue/cli@5.0.8 -g
RUN npm install -g postcss-loader postcss postcss-import postcss-url
RUN npm install -g @vue/cli-service

COPY package.json .
COPY package-lock.json .
RUN npm install

CMD ["npm", "run", "serve"]
