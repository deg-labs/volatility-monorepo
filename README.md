<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [リリース / デプロイ方法](#%E3%83%AA%E3%83%AA%E3%83%BC%E3%82%B9--%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4%E6%96%B9%E6%B3%95)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## リリース / デプロイ方法

このリポジトリは GitHub Actions の `deploy-to-gce` ワークフローで GCE インスタンスへデプロイされます。

1. `main` ブランチから作業ブランチを作成し、変更を実施します。
2. `main` 向けにプルリクエストを作成します。
3. レビューと必要な保護ルールを通過した変更を `main` へマージします。
4. `dev` / `stg` はPRへのラベル付与でデプロイできます。本番は`main`へのpush、またはActionsの手動実行でデプロイします。
5. 本番の手動実行は`main` refに限定され、Workload Identity Federationで認証後にインスタンスへ `docker compose` でデプロイされます。
6. デプロイ先は選択したenvironmentで保護されます。
