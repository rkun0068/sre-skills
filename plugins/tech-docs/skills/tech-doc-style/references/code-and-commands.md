# 代码、命令与占位符

## 行内代码

用 `code` 字体的内容：
- 代码元素、命令、参数和 flag；
- 文件名和路径、环境变量；
- HTTP 状态码、终端输出、用户需要输入的文本。

代码元素前面加上说明性的名词，读起来更通顺，例如 "the `--force` flag"、"the `config.yaml` file"。不要把代码元素当作动词使用。

## 代码块

- 代码块前用一句话引出：紧跟代码块时用冒号结尾，中间隔着其他内容时用句号。
- 代码块必须标注语言（```` ```bash ````、```` ```python ````、```` ```yaml ````）。
- 每行不超过 80 个字符；缩进遵循该语言的风格指南。
- 省略的代码用该语言的注释标出，例如 `# ...`，不用 `…`。包含省略的代码块不能直接复制运行，要在引导语中说明。
- 代码示例应该能直接复制运行：除了占位符，不要包含其他需要读者修改的内容。

## 命令行

- 多行命令每行都以 `$ ` 开头，不写当前路径。单行命令可以省略 `$`，但如果同一篇文档里既有单行命令又有多行命令，就全部加上 `$`。从本地切换到远程机器时，换用新的提示符。
- 输入和输出放在两个独立的代码块里。输出用 "The output is similar to the following:" 引出；省略的行用单独一行的 `...` 表示。只在输出对读者有用时才展示，例如需要从中复制某个值。
- 长命令用续行符分成多行，续行缩进 4 个空格：Linux / macOS 用 ` \`，Windows 用 ` ^`。
- 在语法说明里：可选参数用 `[ ]`，多选一用 `{a|b}`，可以重复用 `...`。**这些符号不要出现在可复制运行的示例中**。可以为每种情况分别给一个示例，并链接到完整的命令参考。

## 占位符

- 格式：`UPPER_SNAKE_CASE`，名称要说明它代表什么，例如 `PROJECT_ID`、`BUCKET_NAME`。
- 避免：`<project-id>`、`{projectId}`、`YOUR_PROJECT`、`MY_BUCKET`、`xxx`、`foo`。
- Markdown 中行内的占位符：`` *`PROJECT_ID`* ``，即代码字体外面再加斜体。代码块内直接写 `PROJECT_ID`。
- 解释方式：
  - 只有一个占位符时，在代码块之后写一句话："Replace `BUILD_ID` with the ID of the build."
  - 有多个占位符时，在代码块之后写引导语 "Replace the following:"，然后按它们在命令中出现的顺序列出。每项的格式为 `` `NAME`: `` 加上小写开头的说明，需要举例时用 "such as" 引出。

示例：

```bash
gcloud run deploy SERVICE_NAME --region=REGION
```

Replace the following:

- `SERVICE_NAME`: the name of the service to deploy
- `REGION`: the region where the service runs, such as `us-central1`

## 示例中的域名与名称

- 域名用 `example.com`、`example.org`、`example.net`。IP 用文档专用地址段：`192.0.2.0/24`、`198.51.100.0/24`、`203.0.113.0/24`，IPv6 用 `2001:db8::/32`。
- 人名要体现多样性。不要使用真实的用户数据、密钥或内部主机名。
