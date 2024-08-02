# Contribuer

Le projet en est encore à ses débuts. Si ces données (ou plus généralement le domaine de la RSE et comptabilité environnementale) vous parlent, je serais ravi d'échanger ! Par exemple par e-mail : hi@alxthm.com.

Que vous soyez développeur / développeuse ou non, si vous avez des retours ou suggestions sur le site, vous pouvez également [créer une Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue#creating-an-issue-from-a-repository).

## Développer le projet en local

### Installation

Le projet nécessite python 3.11 (que vous pouvez installer avec [pyenv](https://github.com/pyenv/pyenv) ou autre).

D'abord, installer le virtualenv python avec toutes ses dépendances :

```
make install
```

Pour lancer toutes les commandes suivantes, il faut d'abord activer le virtualenv :

```
source .venv/bin/activate
```

Ensuite, décompresser et pré-traiter les données brutes :

```
make data
```

> Note : si vous utilisez nix et direnv, le fichier `.envrc` s'assure d'activer le virtualenv automatiquement.

### Lancer l'application

Avec le virtualenv activé :

```
make serve
```

### Tests

```
make test
```
