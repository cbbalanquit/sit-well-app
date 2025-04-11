FROM node:16-alpine

WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Fix permissions issue with node_modules/.cache
RUN mkdir -p /app/node_modules/.cache && chmod -R 777 /app/node_modules/.cache

# Expose port
EXPOSE 3000

# Start the application in development mode
CMD ["npm", "start"]