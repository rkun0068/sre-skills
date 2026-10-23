# API 参考与代码注释

## 总则

- 所有公开的类、接口、结构体、常量、字段、枚举和方法都要有说明。方法要说明每个参数、返回值和异常。
- 每个参考页面的顶部放一段 5–20 行的代码示例。
- API 名称、参数名和字符串字面量用 code 字体，名称的拼写和代码完全一致。
- 第一句话之前不要出现句号：很多工具会在第一个句号处截断摘要，所以第一句里用 "for example"，不用 "e.g."。

## 类与接口

第一句简短说明用途，不要重复类名，也不要写 "This class will…"。后面再写：如何创建实例、主要特性、最佳实践、常见的坑。

## 方法

用现在时、第三人称动词开头，第一句说明这个方法做什么。

| 方法类型 | 开头写法 | 示例 |
|---|---|---|
| 返回数据的操作 | 描述操作本身的动词 | Lists the instances in a project. |
| 布尔类型的 getter | Checks whether … | Checks whether the cache is enabled. |
| 其他 getter | Gets the … | Gets the display name. |
| 无返回值的方法 | Sets / Updates / Deletes / Registers … | Deletes the specified bucket. |
| 回调（`on…`） | Called by … / Called when … | Called when the connection closes. |
| 便捷构造函数 | Creates a … | Creates a client with default settings. |

后面的句子说明：为什么以及怎样使用、前提条件、所需权限（以及没有权限时的行为）、相关 API。

## 参数

- 首字母大写，以句号结尾；非布尔参数尽量以 "The" 或 "A" 开头。
- 用于触发某个动作的布尔参数：分别说明 true 和 false 时的行为。
- 用于描述状态的布尔参数："True if …; false otherwise."。true 和 false 不加 code 字体，也不加引号。
- 有默认值时，说明不同取值下的行为，最后写 "Default: …"。

## 返回值与异常

- 返回值：非布尔类型以 "The …" 开头；布尔类型写 "True if …; false otherwise."。详细说明放在类或方法的描述里。
- 异常：如果文档生成工具会自动加上 "Throws"，就以 "If …" 开头；否则以 "Thrown when …" 开头。

## 弃用

第一句写 "Deprecated. Use `newMethod()` instead."，并写明从哪个版本开始弃用。然后说明如何迁移现有代码。只有第一句会出现在摘要和索引里，所以最重要的信息要放在第一句。

## CLI 与配置参考

- 每条命令：一句话说明用途、用法（Synopsis，可以使用 `[ ]`、`{|}`、`...`）、参数表（名称、类型、是否必需、默认值、说明）、可以直接运行的示例、退出码。
- 每个配置项：键名、类型、默认值、可选值或取值范围、修改后是否需要重启、示例。
