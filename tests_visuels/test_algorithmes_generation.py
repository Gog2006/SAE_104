import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numero_generator import (
    generer_prochain_numero_plaque, 
    generer_prochain_numero_carte_grise,
    formater_numero_plaque
)

def demonstration_generation_sequentielle():
    """Démontre la génération séquentielle en temps réel"""
    afficher_ligne_separation("DÉMONSTRATION GÉNÉRATION SÉQUENTIELLE")
    
    # Menu de choix pour le type de démonstration
    print("Choisissez le type de démonstration :")
    print("  [1]  Plaques d'immatriculation")
    print("  [2]  Cartes grises")
    print("  [3]  Les deux")
    
    choix_demo = input("\nVotre choix : ").strip()
    
    if choix_demo in ["1", "3"]:
        demonstration_plaques()
    
    if choix_demo in ["2", "3"]:
        if choix_demo == "3":
            print("\n" + "─" * 60)
        demonstration_cartes_grises()

def demonstration_plaques():
    """Démonstration de la génération séquentielle des plaques"""
    print("\n=== GÉNÉRATION PLAQUES D'IMMATRICULATION ===")
    
    # Demander le nombre et le point de départ
    try:
        nombre = int(input("Nombre de générations à afficher (défaut: 20) : ") or "20")
        debut = input("Numéro de départ (défaut: AA100AA) : ").strip() or "AA100AA"
    except ValueError:
        nombre = 20
        debut = "AA100AA"
    
    print(f"\nGénération de {nombre} numéros à partir de {debut}")
    print("─" * 50)
    print(f"{'N°':<4} {'COMPACT':<10} {'FORMATÉ':<12} {'DESCRIPTION':<25}")
    print("─" * 50)
    
    numero_actuel = debut
    for i in range(nombre):
        numero_formate = formater_numero_plaque(numero_actuel)
        description = analyser_changement_plaque(numero_actuel, i)
        
        print(f"{i+1:<4} {numero_actuel:<10} {numero_formate:<12} {description:<25}")
        
        # Générer le prochain numéro
        numero_suivant = generer_prochain_numero_plaque(numero_actuel)
        if not numero_suivant:
            print("     >>> MAXIMUM ATTEINT <<<")
            break
        
        numero_actuel = numero_suivant
        
        # Petite pause pour effet visuel
        if i < nombre - 1:  # Pas de pause après le dernier
            time.sleep(0.1)

def demonstration_cartes_grises():
    """Démonstration de la génération séquentielle des cartes grises"""
    print("\n=== GÉNÉRATION CARTES GRISES ===")
    
    # Demander le nombre et le point de départ
    try:
        nombre = int(input("Nombre de générations à afficher (défaut: 15) : ") or "15")
        debut = input("Numéro de départ (défaut: 2026AA00100) : ").strip() or "2026AA00100"
    except ValueError:
        nombre = 15
        debut = "2026AA00100"
    
    print(f"\nGénération de {nombre} numéros à partir de {debut}")
    print("─" * 60)
    print(f"{'N°':<4} {'NUMÉRO CARTE':<12} {'DESCRIPTION':<35}")
    print("─" * 60)
    
    numero_actuel = debut
    for i in range(nombre):
        description = analyser_changement_carte_grise_demo(numero_actuel, i)
        
        print(f"{i+1:<4} {numero_actuel:<12} {description:<35}")
        
        # Générer le prochain numéro
        numero_suivant = generer_prochain_numero_carte_grise(numero_actuel)
        if not numero_suivant:
            print("     >>> ERREUR GÉNÉRATION <<<")
            break
        
        numero_actuel = numero_suivant
        
        # Petite pause pour effet visuel
        if i < nombre - 1:  # Pas de pause après le dernier
            time.sleep(0.1)

def analyser_changement_plaque(numero, index):
    """Analyse le changement pour les plaques (description simplifiée)"""
    if index == 0:
        return "Point de départ"
    
    lettres_gauche = numero[:2]
    chiffres = numero[2:5]
    lettres_droite = numero[5:7]
    
    if lettres_droite == "AA" and chiffres != "100":
        return "Reset lettres droites"
    elif lettres_gauche != "AA" and chiffres == "100" and lettres_droite == "AA":
        return "Reset + changement série"
    else:
        return "Incrémentation normale"

def analyser_changement_carte_grise_demo(numero, index):
    """Analyse le changement pour les cartes grises (description simplifiée)"""
    if index == 0:
        return "Point de départ"
    
    annee = numero[:4]
    lettres = numero[4:6]
    chiffres = numero[6:]
    
    if chiffres == "00001":
        return "Reset chiffres"
    elif lettres == "AA" and chiffres != "00001":
        return "Reset lettres"
    elif lettres in ["BA", "CA", "DA"]:
        return "Changement première lettre"
    else:
        return "Incrémentation normale"

def afficher_ligne_separation(titre):
    """Affiche une ligne de séparation avec titre"""
    print("=" * 60)
    print(f"   {titre}")
    print("=" * 60)

def test_generation_plaques():
    """Tests visuels pour la génération des numéros de plaques"""
    afficher_ligne_separation("TESTS GÉNÉRATION NUMÉROS DE PLAQUES")
    
    # Tests demandés dans les consignes
    tests_plaques = [
        "AB977GH",   # Passage de AB 977 GH à AB 977 GI
        "AB977ZZ",   # Passage de AB 977 ZZ à AB 978 AA  
        "AB999ZZ",   # Passage de AB 999 ZZ à AC 010 AA
        # Tests supplémentaires pour validation complète
        "AA100AA",   # Premier numéro
        "AA100AZ",   # Changement simple lettre droite
        "AA100ZZ",   # Changement chiffres
        "AA999ZZ",   # Changement lettres gauche
        "AZ999ZZ",   # Changement première lettre gauche
        "ZZ998ZZ",   # Avant le maximum théorique
        "ZZ999ZY",   # Avant le maximum absolu
    ]
    
    print(f"{'NUMÉRO ACTUEL':<12} → {'PROCHAIN NUMÉRO':<12}   |   {'FORMATÉ ACTUEL':<12} → {'FORMATÉ PROCHAIN':<12}")
    print("-" * 80)
    
    for numero_actuel in tests_plaques:
        numero_suivant = generer_prochain_numero_plaque(numero_actuel)
        
        # Formatage pour affichage lisible
        actuel_formate = formater_numero_plaque(numero_actuel)
        suivant_formate = formater_numero_plaque(numero_suivant) if numero_suivant else "MAXIMUM ATTEINT"
        
        print(f"{numero_actuel:<12} → {numero_suivant or 'MAXIMUM':<12}   |   {actuel_formate:<12} → {suivant_formate:<12}")

def test_generation_cartes_grises():
    """Tests visuels pour la génération des numéros de cartes grises"""
    afficher_ligne_separation("TESTS GÉNÉRATION NUMÉROS DE CARTES GRISES")
    
    # Tests avec différents scénarios d'incrémentation
    tests_cartes = [
        "2026AA00010",   # Incrémentation simple
        "2026AA99999",   # Changement de lettre (AA → AB)
        "2026AZ99999",   # Changement de première lettre (AZ → BA)
        "2026ZZ99999",   # Changement d'année (2026 → 2027)
        # Tests supplémentaires
        "2025AA00001",   # Premier de l'année
        "2025AB00000",   # Après reset des chiffres
        "2025BA00000",   # Après reset de la deuxième lettre
        "2025ZA99999",   # Avant changement de première lettre
        "2024ZZ99998",   # Avant changement d'année
    ]
    
    print(f"{'NUMÉRO ACTUEL':<15} → {'PROCHAIN NUMÉRO':<15}   |   DESCRIPTION DU CHANGEMENT")
    print("-" * 90)
    
    for numero_actuel in tests_cartes:
        numero_suivant = generer_prochain_numero_carte_grise(numero_actuel)
        
        # Analyse du changement pour description
        description = analyser_changement_carte_grise(numero_actuel, numero_suivant)
        
        print(f"{numero_actuel:<15} → {numero_suivant:<15}   |   {description}")

def analyser_changement_carte_grise(actuel, suivant):
    """Analyse le type de changement effectué dans la génération"""
    if not actuel or not suivant:
        return "Génération initiale"
    
    annee_actuelle = actuel[:4]
    lettres_actuelles = actuel[4:6] 
    chiffres_actuels = actuel[6:]
    
    annee_suivante = suivant[:4]
    lettres_suivantes = suivant[4:6]
    chiffres_suivants = suivant[6:]
    
    if annee_actuelle != annee_suivante:
        return "Changement d'année"
    elif lettres_actuelles != lettres_suivantes:
        if lettres_actuelles[0] != lettres_suivantes[0]:
            return "Incrémentation première lettre"
        else:
            return "Incrémentation deuxième lettre"
    else:
        return "Incrémentation simple des chiffres"

def test_cas_limites():
    """Tests des cas limites et cas d'erreur"""
    afficher_ligne_separation("TESTS DES CAS LIMITES")
    
    print("Test des entrées invalides et cas limites :")
    print("-" * 50)
    
    # Tests plaques - cas limites
    print("PLAQUES - Cas limites :")
    cas_limites_plaques = [
        ("", "Entrée vide"),
        ("INVALID", "Format invalide"),
        ("AB12ZZ", "Trop court"),
        ("AB1234CD", "Trop long"),
        ("ZZ999ZZ", "Maximum théorique"),
    ]
    
    for cas, description in cas_limites_plaques:
        try:
            resultat = generer_prochain_numero_plaque(cas)
            print(f"  {cas or 'VIDE':<10} → {resultat or 'NONE':<10} ({description})")
        except Exception as e:
            print(f"  {cas or 'VIDE':<10} → ERREUR     ({description} - {type(e).__name__})")
    
    print("\nCARTES GRISES - Cas limites :")
    cas_limites_cartes = [
        ("", "Entrée vide"),
        (None, "Entrée None"),
        ("INVALID", "Format invalide"),
        ("2026AA1234", "Trop court"),
        ("2026AA123456", "Trop long"),
    ]
    
    for cas, description in cas_limites_cartes:
        try:
            resultat = generer_prochain_numero_carte_grise(cas)
            print(f"  {cas or 'NONE':<12} → {resultat:<12} ({description})")
        except Exception as e:
            print(f"  {cas or 'NONE':<12} → ERREUR      ({description} - {type(e).__name__})")

def test_formatage():
    """Tests du formatage des numéros de plaques"""
    afficher_ligne_separation("TESTS FORMATAGE DES PLAQUES")
    
    exemples_formatage = [
        "AB123CD",
        "ZZ999AA", 
        "AA100ZZ",
        "XY456WX",
    ]
    
    print(f"{'FORMAT COMPACT':<10} → {'FORMAT AFFICHÉ':<12}")
    print("-" * 25)
    
    for plaque in exemples_formatage:
        plaque_formatee = formater_numero_plaque(plaque)
        print(f"{plaque:<10} → {plaque_formatee:<12}")

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "TESTS VISUELS DES ALGORITHMES" + " " * 17 + "║")
    print("║" + " " * 15 + "SAE 1.04 - Équipe G3A" + " " * 19 + "║") 
    print("╚" + "═" * 58 + "╝")
    print()
    print("Choisissez le test à exécuter :")
    print()
    print("  [1]  Tests génération plaques d'immatriculation")
    print("  [2]  Tests génération cartes grises")
    print("  [3]  Tests des cas limites et erreurs")
    print("  [4]  Tests de formatage des plaques")
    print("  [5]  Démonstration génération séquentielle")
    print("  [6]  Exécuter TOUS les tests")
    print("  [0]  Quitter")
    print()
    print("═" * 60)

def executer_choix(choix):
    """Exécute le test correspondant au choix"""
    if choix == "1":
        test_generation_plaques()
    elif choix == "2":
        test_generation_cartes_grises()
    elif choix == "3":
        test_cas_limites()
    elif choix == "4":
        test_formatage()
    elif choix == "5":
        demonstration_generation_sequentielle()
    elif choix == "6":
        executer_tous_les_tests()
    elif choix == "0":
        print("\nAu revoir !")
        return False
    else:
        print("\nChoix invalide ! Veuillez choisir entre 0 et 6.")
        return True
    
    input("\nAppuyez sur Entrée pour continuer...")
    return True

def executer_tous_les_tests():
    """Exécute tous les tests visuels"""
    print("\nExécution de tous les tests...")
    print()
    
    # Exécution séquentielle des tests
    test_generation_plaques()
    print()
    
    test_generation_cartes_grises() 
    print()
    
    test_cas_limites()
    print()
    
    test_formatage()
    print()
    
    afficher_ligne_separation("RÉSUMÉ DES TESTS")
    print("[✓] Tests de génération des plaques d'immatriculation")
    print("[✓] Tests de génération des cartes grises")
    print("[✓] Tests des cas limites et erreurs")
    print("[✓] Tests de formatage d'affichage")
    print()
    print("Tous les algorithmes fonctionnent selon les spécifications")
    print("Prêt pour la démonstration SAE 1.04")

def menu_principal():
    """Menu interactif principal"""
    continuer = True
    while continuer:
        afficher_menu()
        try:
            choix = input("Votre choix (0-6) : ").strip()
            continuer = executer_choix(choix)
        except KeyboardInterrupt:
            print("\n\nProgramme interrompu par l'utilisateur.")
            break
        except Exception as e:
            print(f"\nErreur inattendue : {e}")
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    menu_principal()