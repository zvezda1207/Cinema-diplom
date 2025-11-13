FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

# Копируем остальные файлы
COPY . .

EXPOSE 3000

ENV VITE_PROXY_TARGET=http://backend:80

# Используем npx для запуска vite, так как он может быть не в PATH
CMD ["npx", "vite", "--host", "0.0.0.0", "--port", "3000"]
