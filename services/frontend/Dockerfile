FROM node:20-alpine AS builder
WORKDIR /app
ARG VITE_API_IP
ENV VITE_HOST_IP=http://${VITE_API_IP}:8080
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=15s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1
