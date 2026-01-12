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
    """Classe de gestion de la connexion et des opérations sur la base de données"""
    
    def __init__(self):
        # Récupération des paramètres de connexion depuis les variables d'environnement
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'carte_grise_db')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.connection = None
    
    def connect(self):
        """Établit la connexion à la base de données MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                use_pure=True,  # Utilise l'implémentation pure Python (compatible avec tous les OS)
                autocommit=False,  # Les transactions doivent être validées manuellement
                connection_timeout=30,
                get_warnings=False,
                raise_on_warnings=False
            )
            # Configuration des variables de session pour gérer les délais d'inactivité
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute("SET SESSION wait_timeout=28800")  # 8 heures
                cursor.execute("SET SESSION interactive_timeout=28800")
                cursor.close()
                logger.info("Connexion réussie à la base de données MySQL")
                return True
        except Error as e:
            logger.error(f"Erreur lors de la connexion à MySQL: {e}")
            return False
    
    def _ensure_connection(self):
        """Vérifie que la connexion est active et la rétablit si nécessaire"""
        try:
            if not self.connection:
                logger.info("Pas de connexion, établissement de la connexion...")
                return self.connect()
            
            # Test si la connexion est active
            if not self.connection.is_connected():
                logger.info("Connexion perdue, tentative de reconnexion...")
                self.disconnect()
                self.connection = None
                return self.connect()
            
            # Ping supplémentaire pour vérifier l'état du serveur
            try:
                self.connection.ping(reconnect=True, attempts=3, delay=1)
            except Error as e:
                logger.warning(f"Ping échoué: {e}, reconnexion en cours...")
                self.disconnect()
                self.connection = None
                return self.connect()
            
            return True
        except Error as e:
            logger.error(f"Erreur lors de la vérification de la connexion: {e}")
            self.connection = None
            return self.connect()
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Connexion MySQL fermée")
    
    def execute_query(self, query, params=None):
        """
        Exécute une requête de modification (INSERT, UPDATE, DELETE)
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres pour la requête (tuple)
            
        Returns:
            ID de la dernière ligne insérée ou True si succès
        """
        self._ensure_connection()
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=False)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()  # Validation de la transaction
            last_id = cursor.lastrowid
            return last_id if last_id else True
        except Error as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            try:
                self.connection.rollback()  # Annule la transaction en cas d'erreur
            except Error as rollback_error:
                logger.error(f"Erreur lors de l'annulation de la transaction: {rollback_error}")
                # Force une reconnexion si l'annulation échoue
                try:
                    self.disconnect()
                except:
                    pass
                self.connection = None
            return False
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error as e:
                    logger.error(f"Erreur lors de la fermeture du curseur: {e}")
    
    def fetch_all(self, query, params=None):
        """
        Exécute une requête SELECT et retourne tous les résultats
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres pour la requête (tuple)
            
        Returns:
            Liste de dictionnaires contenant les résultats
        """
        self._ensure_connection()
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            # Force une reconnexion en cas d'erreur critique
            try:
                self.disconnect()
            except:
                pass
            self.connection = None
            return []
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error as e:
                    logger.error(f"Erreur lors de la fermeture du curseur: {e}")
    
    def fetch_one(self, query, params=None):
        """
        Exécute une requête SELECT et retourne un seul résultat
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres pour la requête (tuple)
            
        Returns:
            Dictionnaire contenant le premier résultat ou None
        """
        self._ensure_connection()
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            # Force une reconnexion en cas d'erreur critique
            try:
                self.disconnect()
            except:
                pass
            self.connection = None
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error as e:
                    logger.error(f"Erreur lors de la fermeture du curseur: {e}")
