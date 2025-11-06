FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

# Копируем остальные файлы
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
