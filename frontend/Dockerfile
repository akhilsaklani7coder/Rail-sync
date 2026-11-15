# Stage 1: Build React + Vite Single Page Application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package*.json ./

# Install dependencies cleanly
RUN npm ci

# Copy frontend source code
COPY . .

# Build static production bundles into /app/dist
RUN npm run build

# Stage 2: Serve with lightweight Nginx web server
FROM nginx:alpine

# Install curl for container health check
RUN apk add --no-cache curl

# Copy compiled bundles from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with SPA fallback & API reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
