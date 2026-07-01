# Note de Sécurité — Perturbation J3 : Injection de Prompt Indirecte

## 1. Diagnostic de la vulnérabilité
La vulnérabilité identifiée par le testeur sécurité est une **Prompt Injection Indirecte** (classée **LLM01:2025** au Top 10 de l'OWASP LLM). 

L'attaque a fonctionné car le backend de l'application concaténait initialement les consignes de l'application (le *System Prompt*) et le texte du cours fourni par l'utilisateur (l' *User Input*) au sein d'une seule et unique chaîne de caractères brute (`string`) envoyée au LLM. 

En insérant la consigne malveillante en blanc sur fond blanc (« *IGNORE TOUTES LES INSTRUCTIONS PRÉCÉDENTES...* ») dans un document PDF, le texte a été extrait normalement lors du parsing du document. Le LLM, fonctionnant de manière probabiliste et sémantique, n'a pas fait la distinction entre les métadonnées de structure (les ordres des développeurs) et les données textuelles brutes (le cours). Il a traité l'instruction de l'attaquant comme une priorité absolue, écrasant le comportement attendu de l'application pour forcer toutes les bonnes réponses sur l'option A.

---

## 2. Stratégie défensive mise en place
Pour neutraliser cette faille avant la livraison du MVP, nous avons déployé une architecture de remédiation en **4 couches successives** côté backend :

* **Couche 1 : Séparation stricte des rôles via l'API Messages** Le backend n'utilise plus aucune concaténation de chaînes. Nous exploitons l'interface structurée native du client LLM Ollama en séparant formellement les objets de contexte. Le prompt de l'application est envoyé sous le rôle `"system"`, tandis que le contenu du cours extrait est relégué sous le rôle `"user"`.
* **Couche 2 : Isolation sémantique et Délimiteurs stricts** Dans le *System Prompt*, le texte de l'utilisateur est désormais encapsulé de manière hermétique entre des délimiteurs XML explicites (`<user_content>...</user_content>`). Une instruction défensive impérative interdit formellement au modèle d'interpréter ou d'exécuter tout ordre, commande ou modification de structure situé à l'intérieur de ces balises. Le contenu y est traité comme une donnée purement passive.
* **Couche 3 : Validation Post-LLM et Analyse de Schéma** La réponse générée par le LLM subit un contrôle strict avant d'être envoyée au front-end ou enregistrée en base de données. Un script valide la structure JSON : vérification de la présence de 4 options uniques par question et d'une seule bonne réponse. De plus, une règle heuristique bloque la validation si une anomalie statistique est détectée (par exemple, si 100 % des réponses valides pointent vers l'option A).
* **Couche 4 : Mécanisme de Re-prompt automatique** Si la couche 3 détecte une non-conformité du schéma ou une anomalie de génération suite à une tentative d'injection, l'application intercepte l'erreur, nettoie le contexte et sollicite une nouvelle génération auprès du LLM (limité à un maximum de 2 essais). En cas d'échecs consécutifs, une exception propre est levée pour l'utilisateur, empêchant l'affichage d'un quiz corrompu.

---

## 3. Limites résiduelles
Bien que notre stratégie en 4 couches bloque efficacement les injections directes, les jailbreaks textuels simples et l'altération grossière des réponses, des risques demeurent ouverts :

1. **Injections sémantiques complexes (Attaques par obfuscation) :** Des attaques avancées utilisant du chiffrement léger (Base64, substitution), des langages alternatifs peu communs, ou des métaphores complexes (ingénierie sociale inversée) peuvent passer à travers les filtres du *System Prompt* si le modèle sous-jacent est assez puissant pour les décoder en cours de route.
2. **Empoisonnement invisible des données (Data Poisoning indirect) :** Si le cours contient des informations factuellement fausses mais structurellement valides, le LLM générera un quiz basé sur ces faussetés. Le patch valide la *forme* et la *cohérence logique* de la sortie, mais ne peut pas auditer la véracité encyclopédique du cours.
3. **Dépendance au modèle (Modèle probabiliste) :** La sécurité absolue n'existe pas avec les technologies de LLM. Une mise à jour du modèle sous-jacent ou une dérive sémantique peut modifier la façon dont les délimiteurs XML sont interprétés, réduisant l'efficacité de la Couche 2. Une veille active sur les évolutions de l'OWASP LLM reste indispensable.
