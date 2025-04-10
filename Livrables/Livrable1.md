## 📝 Livrable 1 – Modélisation et proposition d’algorithme

---

## Sommaire

- [📝 Livrable 1 – Modélisation et proposition d’algorithme](#-livrable-1--modélisation-et-proposition-dalgorithme)
- [Sommaire](#sommaire)
  - [🔹 1. Résumé du projet](#-1-résumé-du-projet)
  - [🔹 2. Choix d’un type d’algorithme de base](#-2-choix-dun-type-dalgorithme-de-base)
  - [🔹 3. Définition des contraintes choisies](#-3-définition-des-contraintes-choisies)
    - [🔸 1. Coût ou restriction de passage sur certaines arêtes](#-1-coût-ou-restriction-de-passage-sur-certaines-arêtes)
    - [🔸 2. Routes dynamiques ou perturbations](#-2-routes-dynamiques-ou-perturbations)
  - [🔹 4. Structure des graphes](#-4-structure-des-graphes)
    - [1. **Stockage du graphe**](#1-stockage-du-graphe)
    - [2. **Stockage des poids des arêtes**](#2-stockage-des-poids-des-arêtes)
    - [3. Exemple](#3-exemple)
  - [🔹 5. Pseudo-code de l'algorithme](#-5-pseudo-code-de-lalgorithme)
  - [🧠 Explication de l’algorithme](#-explication-de-lalgorithme)
  - [🔹 6. Calcul de complexité de l’algorithme](#-6-calcul-de-complexité-de-lalgorithme)
    - [🔸 Étapes de l'algorithme et leur complexité :](#-étapes-de-lalgorithme-et-leur-complexité-)
    - [🔸 Nombre total de paliers (refroidissements) :](#-nombre-total-de-paliers-refroidissements-)
  - [🔸 Complexité globale :](#-complexité-globale-)
  - [✅ Conclusion simplifiée :](#-conclusion-simplifiée-)

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

#### 3. Exemple

```python
poids_arêtes = {
    1: {2: 20, 3: 40},  # Poids entre 1 et 2 (ralenti) et entre 1 et 3
    2: {1: 20, 3: float('inf')},  # Route bloquée entre 2 et 3
    3: {1: 40, 2: float('inf')}   # Route bloquée entre 3 et 2
}
```

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

        update_graph(G, t)       // 🆕 Mettre à jour les poids du graphe selon les conditions actuelles

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
        t ← t + 1     // temps évolue → simulateur de trafic évolue aussi

Retourner best_tour
```

### 🧠 Explication de l’algorithme

Cet algorithme de **recuit simulé** cherche une tournée efficace dans un réseau routier où les conditions peuvent changer au cours du temps (ralentissements, blocages…).

Voici le principe :

- On commence par une **solution initiale valide** (une tournée qui respecte les contraintes du graphe au temps `t = 0`).
- À chaque température, on génère plusieurs solutions voisines (en modifiant légèrement la tournée).
- Si une solution est **meilleure**, on l’accepte.
- Si elle est **moins bonne**, on peut quand même l’accepter avec une certaine probabilité liée à la température `T` (ce qui permet d’éviter les minima locaux).
- La **température baisse progressivement** (refroidissement), donc on devient de plus en plus strict dans les choix.
- En parallèle, on **met à jour dynamiquement les poids des routes** à chaque itération (simulateur de trafic), ce qui modifie les coûts de chaque tournée.
- À la fin, on retourne la **meilleure tournée trouvée**.

Ce mécanisme permet de trouver de bonnes solutions même dans un environnement incertain et changeant.

---

### 🔹 6. Calcul de complexité de l’algorithme

L’algorithme de **Recuit Simulé** repose sur deux niveaux de boucle :

1. Une boucle externe de **refroidissement** (`T > T_min`)
2. Une boucle interne de **recherche locale** de `N` voisins à chaque température

---

#### 🔸 Étapes de l'algorithme et leur complexité :

À **chaque température**, on fait les étapes suivantes :

1. `update_graph(G, t)`→ met à jour les poids des arêtes dynamiques→ **Coût : O(|E|)** (on parcourt toutes les arêtes du graphe)
2. Boucle de `N` itérations :

   - `generate_neighbor(tour)` → échange deux sommets→ **O(1)**
   - `is_valid(tour, G, t)` → vérifie si la tournée utilise une route bloquée→ parcourt tous les arcs de la tournée → **O(n)**
   - `compute_cost(tour, G, t)` → somme des coûts des arcs de la tournée
     → **O(n)**

Donc chaque **itération de la boucle interne** coûte **O(n)**
et chaque **palier de température** coûte :
**O(|E| + N × n)**

---

#### 🔸 Nombre total de paliers (refroidissements) :

La température est multipliée à chaque tour par `α < 1`, donc :

- Nombre de paliers
  $$
  k\approx \log_{\alpha} \left(\frac{T_{\text{min}}}{T_{\text{init}}}\right)
  = \frac{\log(T_{\text{min}} / T_{\text{init}})}{\log(\alpha)} = \frac{\log(T_{\text{init}} / T_{\text{min}})}{-\log(\alpha)}
  $$

Pour simplifier, on peut juste dire que le nombre de paliers est **logarithmique** en fonction du ratio entre `T_init` et `T_min` :
→ **k = O(log(T_init / T_min))**

---

### 🔸 Complexité globale :

L’algorithme effectue `k` paliers, et à chaque palier on fait :

$$
\text{Coût} = \mathcal{O}(|E| + N \cdot n)
$$

Donc la complexité globale est :

$$
\mathcal{O}(k \cdot (|E| + N \cdot n))
$$

En remplaçant `k` :

$$
\mathcal{O}\left(\log\left(\frac{T_{\text{init}}}{T_{\text{min}}}\right) \cdot (|E| + N \cdot n)\right)
$$

---

### ✅ Conclusion simplifiée :

- **|E|** : dépend de la densité du graphe (souvent **O(n²)** dans un graphe complet),
- **N** : fixé (paramètre de l’algorithme, typiquement 100 à 1000),
- Le terme **log(T_init / T_min)** reste modéré (quelques dizaines),
- Donc :
  👉 Pour un graphe dense, **complexité ≈ O(n²)**
  👉 Pour un graphe clairsemé, **complexité ≈ O(n)**

---
