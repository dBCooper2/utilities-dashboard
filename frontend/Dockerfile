FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy configuration files first
COPY postcss.config.js ./
COPY tailwind.config.js ./
COPY tsconfig.json ./

# Copy the rest of the application
COPY . .

# Create a simple globals.css if it doesn't exist
RUN mkdir -p app && echo "@tailwind base;\n@tailwind components;\n@tailwind utilities;" > app/globals.css

# Expose port
EXPOSE 3000

# Start the application in development mode
CMD ["npm", "run", "dev"]
