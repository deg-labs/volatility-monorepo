# volatility-monorepo

このモノレポ直下の `.env` を使って、`server` と `client` を 1 つの Docker Compose で起動できます。

## 使い方

1. ルートに `.env` を作成

```bash
cp .env.example .env
```

2. 必須値を設定

- `DISCORD_WEBHOOK_URL`

3. 起動

```bash
docker compose up --build
```

`client` (`volatility-ncmma-notifier`) から `server` API への接続先は、Docker 内通信で `http://nginx/volatility` と `http://nginx/volume` を使います。

## CI/CD (GCE Deploy)

`hdm/.github/workflows/deploy.yml` を参考に、同等のラベル駆動デプロイを追加しています。

- Workflow: `.github/workflows/deploy.yml`
- Trigger: PR に `dev` / `stg` / `prd` ラベル付与
- Deploy method: GCE へ `app.tar.gz` + `.env` を転送し、`docker compose up -d --build`

### Required Secrets

- `ORG_GH_APP_ID`, `ORG_GH_APP_PRIVATE_KEY` (GitHub App: Members Read 権限が必要)
- `GCE_ZONE`
- `DEV_GCE_INSTANCE_NAME`, `STG_GCE_INSTANCE_NAME`, `PRD_GCE_INSTANCE_NAME`
- `DEV_GCP_SA_EMAIL`, `STG_GCP_SA_EMAIL`, `PRD_GCP_SA_EMAIL`
- `DEV_GCP_WIF_PROVIDER`, `STG_GCP_WIF_PROVIDER`, `PRD_GCP_WIF_PROVIDER`
- `DEV_APP_ENV`, `STG_APP_ENV`, `PRD_APP_ENV` (複数行 `.env` 本文)

### Optional Variables

- `DEPLOY_TARGET_DIR` (default: `/opt/apps/volatility-monorepo`)
