# Install the Acme CLI

This page shows you how to install the Acme CLI and deploy your first service.

## Before you begin

Make sure that you have an Acme account and permission to create projects.

## Install the CLI

To install the CLI, follow these steps:

1. Download the installer:

    ```bash
    curl -sSL https://example.com/install.sh -o install.sh
    ```

1. Run the installer:

    ```bash
    sh install.sh
    ```

1. Optional: Add the CLI to your `PATH`.

## Deploy a service

In the console, go to the **Services** page, and then click **Create service**.

```bash
acme deploy --project=PROJECT_ID --region=REGION
```

Replace the following:

- `PROJECT_ID`: the ID of your project
- `REGION`: the region where the service runs, such as `us-east1`

The output is similar to the following:

```text
Service deployed to https://service.example.com
```

For more information, see [Deployment options](https://example.com/docs/deploy).

## What's next

- Learn about [service configuration](https://example.com/docs/config).
