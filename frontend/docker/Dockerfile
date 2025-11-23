#######################
# stage: development
#######################
FROM node:22-alpine AS development

RUN corepack enable && corepack prepare pnpm@9.15.4 --activate
WORKDIR /app

# Copy dependency files for installation
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy source files
COPY . .

EXPOSE 3000

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]

#######################
# stage: build
#######################
FROM node:22-alpine AS build

RUN corepack enable && corepack prepare pnpm@9.15.4 --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

#######################
# stage: runtime
#######################
FROM node:22-alpine AS runtime

# Install serve globally using npm (simpler than pnpm for single package)
RUN npm install -g serve

WORKDIR /app

# Copy built assets from build stage
COPY --from=build /app/dist ./dist

# Expose port
EXPOSE 3000

# Serve the static files
CMD ["serve", "-s", "dist", "-l", "3000"]
