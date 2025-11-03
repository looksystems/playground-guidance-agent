# ========================================
# Stage 1: Build Stage
# ========================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Install dependencies for building (including native modules if needed)
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the Nuxt application
# This creates the .output directory with the production build
RUN npm run build

# ========================================
# Stage 2: Production Stage
# ========================================
FROM node:20-alpine AS production

# Set working directory
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init curl

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nuxt -u 1001

# Copy built application from builder
COPY --from=builder --chown=nuxt:nodejs /app/.output /app/.output

# Set environment variables
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000 \
    NUXT_PUBLIC_API_BASE=http://backend:8000

# Expose port
EXPOSE 3000

# Switch to non-root user
USER nuxt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the Nuxt production server
CMD ["node", ".output/server/index.mjs"]
