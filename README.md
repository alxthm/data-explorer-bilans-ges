---
title: Data Explorer - Bilans GES ADEME
emoji: 🌍
colorFrom: gray
colorTo: blue
sdk: docker
license: mit
short_description: Analyse et benchmark des données de Bilans GES de l'ADEME
---

# Analyse et benchmark des données de Bilans GES de l'ADEME

# Deployment

The panel app is deployed to huggingface spaces (everything is defined in the `Dockerfile`).

Since huggingface spaces do not support custom domains yet, the `index.html` file is also deployed to gitlab pages, as a wrapper around the panel app, to allow custom domain.

Notes :
* in order for git lfs to work with hf, it seems that using https is necessary (rather than git ssh), see https://discuss.huggingface.co/t/git-lfs-fetch-with-git-protocol-is-failing/84831/5
* to avoid pushing LFS objects to gitlab, on the client side you can run `git config remote.gitlab.lfsurl ""` (if `gitlab` is the name of the remote), and on the server side, in Gitlab project settings (General / Visibility) you can disable LFS
