# Système de Gestion de Bibliothèque

## Description
Application de gestion de bibliothèque développée en Python avec interface graphique Tkinter. Elle permet la gestion complète des documents, des emprunts et des utilisateurs d'une bibliothèque.

## Fonctionnalités Principales

### 1. Gestion des Documents
- Consultation du catalogue complet
- Ajout, modification et suppression de documents (admin)
- Support de différents types de documents :
  * Livres
  * Magazines
  * Journaux
  * Documents multimédia (CD/DVD)
- Suivi du statut des documents (disponible/emprunté)

### 2. Système d'Emprunt
- Demande d'emprunt par les utilisateurs
- Validation des demandes par les administrateurs
- Gestion des retours
- Calcul automatique des pénalités de retard
- Historique des emprunts

### 3. Gestion des Utilisateurs
- Système d'authentification sécurisé
- Deux niveaux d'accès :
  * Administrateur (gestion complète)
  * Utilisateur (consultation et emprunts)
- Gestion des profils utilisateurs

### 4. Interface Utilisateur
- Design moderne et intuitif
- Navigation simplifiée
- Recherche avancée dans le catalogue
- Messages d'aide et tooltips contextuels

## Architecture Technique

### Technologies Utilisées
- Python 3.8+
- Tkinter pour l'interface graphique
- SQLite pour la base de données
- Architecture MVC (Modèle-Vue-Contrôleur)

### Structure du Projet 
bibliotheque/
├── main.py # Point d'entrée de l'application
├── controllers/ # Logique de contrôle
├── models/ # Modèles de données
├── views/ # Interfaces utilisateur
├── database/ # Gestion de la base de données
├── utils/ # Utilitaires
└── image/ # Ressources graphiques
## Installation et Démarrage

1. Prérequis
- bash
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

2. Installation des dépendances
- bash "pip install Pillow"

3. Initialisation de la base de données
- bash "python init_db.py"

4. Lancement de l'application
- bash "python main.py"

## Utilisation

### Connexion
- **Admin par défaut**
  * Identifiant : admin
  * Mot de passe : admin123

### Navigation
- **Catalogue** : Consultation des documents disponibles
- **Emprunts** : Gestion des emprunts en cours
- **Recherche** : Recherche avancée dans le catalogue
- **Administration** : Gestion des documents et utilisateurs (admin uniquement)

## Sécurité
- Hashage des mots de passe (SHA-256)
- Gestion des sessions utilisateurs
- Validation des entrées utilisateur
- Gestion des droits d'accès

## Fonctionnalités Détaillées

### Catalogue
- Vue d'ensemble de tous les documents
- Filtrage par type de document
- Informations détaillées sur chaque document
- Statut de disponibilité en temps réel

### Gestion des Emprunts
- Demande d'emprunt en un clic
- Suivi des demandes en cours
- Historique des emprunts
- Système de notification pour les retards

### Administration
- Gestion complète du catalogue
- Supervision des emprunts
- Gestion des utilisateurs
- Rapports et statistiques (en cours)

### Interface Graphique
- Design responsive
- Thème moderne possible (à améliorer avec CustomTkinter dans une v2)
- Messages d'erreur explicites
- Confirmations des actions importantes

## Maintenance

### Base de Données
- Sauvegarde automatique
- Système de journalisation
- Gestion des erreurs

### Performance
- Chargement optimisé des données
- Interface réactive
- Gestion efficace de la mémoire

