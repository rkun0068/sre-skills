# Getting Started With The Acme CLI

## Installation:

Please note that the CLI is currently in beta! Simply run the command below and you're done.

```
curl -sSL https://example.com/install.sh | sh
```

To configure, click on **Settings** and add your IP to the whitelist, e.g. `203.0.113.10`.

Run `acme login --token <your-token>` and then `acme deploy --project YOUR_PROJECT_ID`.

For details, click [here](https://example.com/docs). The latest release came out on 03/04/2026.

![](diagram.png)

# Reference

This command is the fastest way to deploy because it uses a seamless pipeline that utilizes caching in order to skip unchanged layers and upload only the files that have changed since the last deployment run.
