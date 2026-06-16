# Fish Ecology Assistant — Docker Deployment
FROM node:22-alpine

WORKDIR /app

# Copy project files
COPY .reasonix/ .reasonix/
COPY config/ config/
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --production

# Default command: IMA knowledge base server
CMD ["node", ".reasonix/mcp-servers/ima-server.mjs"]
