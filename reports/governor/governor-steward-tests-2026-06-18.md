# Tests governor et stack-steward - 18 juin 2026

## Governor

Entree simulee :

- projet absent ;
- modele premium pour resume ;
- secret dans sortie ;
- validation humaine absente.

Detections :

```text
projet absent
cout premium injustifie
exposition secret
validation humaine absente
```

Le secret test n'a pas ete repete dans la sortie.

## Stack steward

Entree simulee :

- stack saine ;
- MCP memoire en staging ;
- daemon sandbox absent.

Sortie :

- etat ;
- ecarts ;
- risques ;
- patch propose ;
- `APPLIQUE: non`.

Aucun outil ni changement execute.
