# Use official Node image
FROM node:18

# Set working directory
WORKDIR /app

# Copy package files first for better caching during Docker builds
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the source files
COPY . .

# Expose Vite's default dev server port
EXPOSE 5173

# Ensure file system watching works inside Docker (for hot reloading)
ENV CHOKIDAR_USEPOLLING=true

# Run the Vite dev server
CMD ["npm", "run", "dev", "--", "--host"]
