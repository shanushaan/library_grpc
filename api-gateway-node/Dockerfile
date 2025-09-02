FROM node:18-alpine

WORKDIR /app

COPY api-gateway-node/package*.json ./
RUN npm install

COPY api-gateway-node/ ./
COPY proto/ ./proto/

EXPOSE 8001

CMD ["npm", "start"]