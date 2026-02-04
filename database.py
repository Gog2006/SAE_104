# Modules pour la connexion MySQL et gestion des erreurs
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du logging (enregistrement des événements)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Database:
    """Classe de gestion de la connexion et des opérations sur la base de données (optimisée pour serverless)"""
    
    def __init__(self):
        # Récupération des paramètres de connexion depuis les variables d'environnement
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'carte_grise_db')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.connection = None
    
    def connect(self):
        """Établit la connexion à la base de données MySQL (optimisée pour Vercel/Aiven)"""
        try:
            # Configuration pour Aiven MySQL avec SSL
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True,  # Autocommit pour serverless (pas de transactions persistantes)
                connection_timeout=10,  # Timeout réduit pour serverless
                pool_size=1,  # Pas de pooling en serverless
                pool_name='serverless_pool',
                ssl_disabled=False,  # Active SSL pour Aiven
                consume_results=True  # Consomme automatiquement les résultats
            )
            
            if self.connection.is_connected():
                logger.info("Connexion réussie à la base de données MySQL")
                return True
        except Error as e:
            logger.error(f"Erreur lors de la connexion à MySQL: {e}")
            return False
    
    def _ensure_connection(self):
        """Vérifie que la connexion est active et la rétablit si nécessaire"""
        try:
            if not self.connection or not self.connection.is_connected():
                return self.connect()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la connexion: {e}")
            return self.connect()
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("Connexion MySQL fermée")
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture: {e}")
        finally:
            self.connection = None
    
    
    def execute_query(self, query, params=None):
        """
        Exécute une requête de modification (INSERT, UPDATE, DELETE)
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres pour la requête (tuple)
            
        Returns:
            ID de la dernière ligne insérée ou True si succès
        """
        if not self._ensure_connection():
            return False
            
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            last_id = cursor.lastrowid
            return last_id if last_id else True
        except Error as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            return False
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def fetch_all(self, query, params=None):
        """
        Exécute une requête SELECT et retourne tous les résultats
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres pour la requête (tuple)
            
        Returns:
            Liste de dictionnaires contenant les résultats
        """
        if not self._ensure_connection():
            return []
            
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return []
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def fetch_one(self, query, params=None):
        """
        Exécute une requête SELECT et retourne un seul résultat
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres pour la requête (tuple)
            
        Returns:
            Dictionnaire contenant le premier résultat ou None
        """
        if not self._ensure_connection():
            return None
            
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

