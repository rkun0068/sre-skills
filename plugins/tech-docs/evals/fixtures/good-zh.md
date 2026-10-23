# 安装 Acme CLI

本页介绍如何安装 Acme CLI 并部署第一个服务。

## 准备工作

确保你拥有 Acme 账号和创建项目的权限。

## 安装 CLI

要安装 CLI，请按以下步骤操作：

1. 下载安装脚本：

    ```bash
    curl -sSL https://example.com/install.sh -o install.sh
    ```

1. 运行安装脚本：

    ```bash
    sh install.sh
    ```

## 部署服务

```bash
acme deploy --project=PROJECT_ID
```

将 `PROJECT_ID` 替换为你的项目 ID。

部署完成后，服务最多保留 30 天的日志，日志大小上限为 10 GB。

如需了解详情，请参阅[部署选项](https://example.com/docs/deploy)。
