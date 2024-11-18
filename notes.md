# Notes pour suite du projet

## Layout de representation

Plusieurs layout on été testé, pour le moment les deux qui ressortent son :
  - **graphviz** : nx.nx_agraph.graphviz_layout(G), nécessite pygraphviz d'installé
  - **kamada kawai** : nx.kamada_kawai_layout(G)

## Piste pour autre layout

Etant donné une structure en plusieurs niveau (entité, concept, sous-concept) une structure multipartie pourrait être une solution de representation (à tester)

## Différentiation peinture du même nom

Il n'est pas possible avec Networkx de créer 2 nodes avec le même nom mais des attributs différent, si l'on essaye de le faire, les attributs de la deuxième node au même nom remplaceront ceux de la 1er

Pour palier au problème d'avoir deux tableaux au nom identique, deux solution s'offre à nous :
  - Définir chaque instance de tableaux par un identifiant auquel est rattaché le nom de l'oeuvre ainsi que le reste des concepts
  - Renommé chaque node de tableaux par le nom de l'oeuvre + celui de l'artiste

## Méthode de calcul d'intéret

On règle au début le poids ajouter à chaque type de relation du graphe, 

# Notes mercredi matin

Voir si possibilité d'ordonner concepts (donner valeurs)
création dépend interet utilisateur + connaissance d'expert (permet de garder une structure fixe)
  Dans ce cas plus court chemin possible pour le coté d'expert
  Trouver plus court chemin entre chaque tableau 

Graph donnée par des expert et on chercher a construire depuis le graph 

