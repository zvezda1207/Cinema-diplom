FROM node:18-alpine

WORKDIR /app

# Копируем только package.json сначала
COPY package.json ./

# Устанавливаем зависимости (это создаст package-lock.json)
RUN npm install

# Копируем остальные файлы
COPY . .

EXPOSE 3000

CMD ["npm", "start"]