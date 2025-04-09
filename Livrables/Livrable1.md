## 📝 Livrable 1 – Modélisation et proposition d’algorithme

---

### 🔹 1. Résumé du projet

Dans le cadre de l’appel à manifestation d’intérêt de l’ADEME, notre équipe **CesiCDP** développe une solution intelligente visant à **optimiser les tournées de livraison** de biens ou services dans un environnement urbain complexe. L’objectif est de **réduire les déplacements** et la **consommation énergétique** tout en prenant en compte des contraintes réalistes et dynamiques du terrain : **routes fermées**, **ralenties**, ou **évoluant dans le temps**.

Nous modélisons ce problème sous forme d’un graphe pondéré représentant un réseau routier. Notre approche repose sur une méthode **approchée**, capable de s’adapter à des situations dynamiques et incomplètes, et d’obtenir de **bonnes solutions rapidement** sans garantie d’optimalité.

---

### 🔹 2. Choix d’un type d’algorithme de base

Le problème que nous traitons est une **généralisation du Problème du Voyageur de Commerce (TSP)**, qui est un **problème NP-difficile**. Trouver une solution optimale est irréaliste pour de grands réseaux. Nous avons donc opté pour une **métaheuristique**, plus précisément le **Recuit Simulé** (Simulated Annealing), pour plusieurs raisons :

- Il s’adapte bien à la recherche dans un espace de solutions complexe.
- Il peut gérer des **coûts variables et des contraintes dynamiques**.
- Il offre un bon **compromis entre performance et qualité de solution**.

---

### 🔹 3. Définition des contraintes choisies

#### 🔸 1. Coût ou restriction de passage sur certaines arêtes

Certaines routes peuvent :

- Être **bloquées** (travaux, incidents, accès interdit),
- Être **coûteuses** (péages, pollution, montée, zone à trafic dense).

Modélisation :

- Si une route est **bloquée** : `c(e) = ∞`
- Si elle est **coûteuse** : `c(e)` est plus élevé que le reste

#### 🔸 2. Routes dynamiques ou perturbations

Les **coûts des routes peuvent évoluer dans le temps** en raison de :

- Variation du trafic (heures de pointe),
- Météo ou incidents,
- Changement de règles de circulation.

Modélisation :

- Chaque arête `(i, j)` a un coût `c_{i,j}(t)` dépendant du **temps** ou d’une **fonction aléatoire/déterministe** simulée.

---

### 🔹 4. Structure des graphes

Pour stocker le graphe et ses poids, on utilise une structure de données qui permet de représenter les arêtes et leurs coûts de manière flexible. Voici comment on peut organiser cela :

#### 1. **Stockage du graphe**

Le graphe est généralement représenté sous forme de **dictionnaire de dictionnaires** où chaque clé est un sommet, et la valeur associée est un autre dictionnaire représentant les voisins de ce sommet avec le poids de l'arête les reliant.

- **Exemple** :
  ```python
  poids_arêtes = {
      1: {2: 10, 3: 20},  # Sommet 1, poids des arêtes vers 2 et 3
      2: {1: 10, 3: 5},   # Sommet 2, poids des arêtes vers 1 et 3
      3: {1: 20, 2: 5}    # Sommet 3, poids des arêtes vers 1 et 2
  }
  ```

#### 2. **Stockage des poids des arêtes**

Les poids des arêtes sont stockés en fonction de deux facteurs principaux :

- **Distance physique** ou **temps de trajet** : le coût de base entre deux sommets.
- **Facteur de ralentissement** : si la route est ralentie (par exemple, travaux ou trafic), on applique un facteur pour ajuster le poids de l'arête.
- **Restrictions de passage** : certaines routes peuvent être bloquées ou interdites, et dans ce cas, le poids est défini comme **infini** (`∞`), rendant l'arête inaccessible.

**Exemple de poids** :

- Si la distance entre les sommets `1` et `2` est de 10, avec un facteur de ralentissement de 2 (trafic ralenti), le poids sera `10 * 2 = 20`.
- Si une route entre `2` et `3` est bloquée, le poids sera `∞` pour indiquer que cette route ne peut pas être utilisée.

#### 3. **Structure de données**

Le graphe et les poids sont donc stockés sous forme de **dictionnaire de dictionnaires**. Par exemple :

```python
poids_arêtes = {
    1: {2: 20, 3: 40},  # Poids entre 1 et 2 (ralenti) et entre 1 et 3
    2: {1: 20, 3: float('inf')},  # Route bloquée entre 2 et 3
    3: {1: 40, 2: float('inf')}   # Route bloquée entre 3 et 2
}
```

Ici, les poids sont calculés en fonction des distances et des conditions de trafic, et les routes bloquées sont représentées par `∞`.

### Résumé

- **Le graphe** est stocké sous forme de dictionnaire où chaque sommet est associé à ses voisins et à leurs poids.
- **Les poids** des arêtes sont calculés en fonction de la distance et des facteurs comme le ralentissement ou les restrictions de passage.

---

### 🔹 5. Pseudo-code de l'algorithme

Voici le **pseudo-code** de l'algorithme de Recuit Simulé avec contraintes dynamiques :

```plaintext
Entrée :
    - G(V, E) : graphe routier avec arêtes pondérées (poids = coût dynamique)
    - s ∈ V : sommet de départ
    - T_init : température initiale
    - T_min : température minimale
    - α ∈ (0,1) : facteur de refroidissement
    - N : nombre maximal d'itérations à température constante

Fonctions :
    - compute_cost(tour, G, t) : retourne le coût total de la tournée à l’instant t
        (en tenant compte des routes bloquées et des ralentissements dynamiques)
    - is_valid(tour, G, t) : retourne Vrai si aucune arête bloquée (c = ∞) n’est utilisée
    - generate_neighbor(tour) : génère une nouvelle tournée en permutant deux villes

Algorithme :

Début :
    t ← 0                         // temps initial
    T ← T_init                    // température initiale
    current_tour ← tournée aléatoire valide depuis s
    best_tour ← current_tour
    best_cost ← compute_cost(best_tour, G, t)

    Tant que T > T_min :
        Pour i de 1 à N :
            neighbor ← generate_neighbor(current_tour)
        
            Si is_valid(neighbor, G, t) :
                cost_neighbor ← compute_cost(neighbor, G, t)
                cost_current ← compute_cost(current_tour, G, t)

                Δ ← cost_neighbor - cost_current

                Si Δ < 0 :
                    current_tour ← neighbor
                    Si cost_neighbor < best_cost :
                        best_tour ← neighbor
                        best_cost ← cost_neighbor
                Sinon :
                    p ← exp(-Δ / T)
                    Si random(0,1) < p :
                        current_tour ← neighbor

        T ← α × T     // refroidissement
        t ← t + 1     // le temps évolue → les coûts dynamiques changent

Retourner best_tour
```

### 🔹 6. Calcul de complexité de l’algorithme

Voici le **calcul de complexité** de l’algorithme de **Recuit Simulé avec contraintes dynamiques**, étape par étape :

---

## 🔹 **Hypothèses de base**

- `n` = nombre de sommets (villes à visiter)
- `L` = longueur de la tournée (≈ `n`)
- `k` = nombre total d'itérations (dépend de T_init, T_min et α)

💡 Nombre d’**itérations `k`** ≈ `log(T_min / T_init) / log(α)`
(en pratique, ce nombre est fixé à un maximum ou mesuré)

---

## 🔹 **Analyse par étape**

| Étape                                 | Complexité  | Détails                                            |
| -------------------------------------- | ------------ | --------------------------------------------------- |
| Générer solution initiale            | O(n)         | Génération d'une permutation valide de n sommets  |
| Calcul du coût initial                | O(n)         | Coût = somme des poids d’un chemin de n-1 arêtes |
| Générer un voisin                    | O(1) à O(n) | Permutation simple (ex: swap 2 villes)              |
| Vérifier si le voisin est valide      | O(n)         | Vérifier que chaque arête n’a pas `poids = ∞` |
| Calcul du coût du voisin              | O(n)         | Recalcul du coût sur n arêtes max                 |
| Comparaison, probabilité, acceptation | O(1)         | Simple calcul et tirage                             |
| Mise à jour de T                      | O(1)         | Produit scalaire                                    |

💡 Ces étapes sont faites **à chaque itération**, donc on les multiplie par `k`.

---

## 🔹 **Complexité totale**

\[
\boxed{
O(k \times n)
}
\]

### Où :

- `n` est le nombre de sommets,
- `k` est le nombre d'itérations de l'algorithme (lié à la température et au facteur de refroidissement).

---

## ✅ **Interprétation**

- Le recuit simulé est **linéaire par itération**, et le nombre d’itérations est **logarithmique dans l’évolution de température**, ou fixé à une **valeur maximale** pour des raisons pratiques.
- Pour `n = 100` villes et `k = 10 000` itérations : l'algorithme reste **praticable sur une machine classique**.

---
