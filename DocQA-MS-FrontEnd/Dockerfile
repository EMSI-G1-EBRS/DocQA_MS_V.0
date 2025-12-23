# 1. Utiliser une image Node légère
FROM node:18-alpine

# 2. Définir le dossier de travail
WORKDIR /app

# 3. Copier les fichiers de dépendances
COPY package.json package-lock.json ./

# 4. Installer les dépendances
RUN npm install

# 5. Copier le reste du code
COPY . .

# 6. Exposer le port 3000
EXPOSE 3000

# 7. Démarrer l'application
CMD ["npm", "start"]