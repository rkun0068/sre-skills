# 词汇表

常用条目，改编自 [Google word list](https://developers.google.com/style/word-list)。表中没有的词，到原文查询。中文对应写法见 chinese-docs.md。

## 用词替换

| 避免 | 改用 | 说明 |
|---|---|---|
| above / below（指代文中或界面上的位置） | preceding / earlier；following / later | 方向性词语对屏幕阅读器用户和翻译都不友好 |
| above / below（指版本范围） | later / earlier | "version 2.0 or later" |
| allows you to / enables you to | lets you | enable 只用于"开启某项功能" |
| e.g. / i.e. | for example / such as；that is | |
| etc. / and so on | 列全，或者用 "including" 引出部分示例 | |
| as（表示"因为"） | because | |
| once（表示"在……之后"） | after | |
| since（表示"因为"） | because | since 只用于表示时间 |
| in order to | to | |
| just / simply / easy / easily / quickly | 删除 | 这些词让任务听起来很简单，读者做不出来时会有挫败感 |
| please / please note / note that | 删除，直接陈述 | |
| currently / presently / as of this writing / now | 删除 | 保持内容不随时间过时 |
| new / newer / latest / old / soon / eventually / in the future / does not yet | 删除，或者写明版本号或日期 | release notes 除外 |
| utilize / leverage | use / build on | |
| execute | run | |
| kill / abort（指停止进程等） | stop / exit / cancel / end | 在描述 `kill` 命令本身时，用 code 字体，不受此限 |
| hit（指按键或点击） | press / click | |
| click on | click | |
| check / uncheck（复选框） | select / clear | 状态写成 selected / not selected |
| check box | checkbox | |
| drop-down（单独作名词） | list / menu | |
| hover over | hold the pointer over | |
| toggle（作动词） | turn on / turn off | |
| grayed out | unavailable | |
| desire / desired | want / need | |
| impact（作动词） | affect | |
| may（表示可能性） | might / can | may 容易和"许可"的意思混淆 |
| could | can | |
| functionality | capability / feature | |
| as per | according to | |
| performant | 用具体指标描述 | |
| login（作动词） | sign in / log in | login 作名词或形容词时可以用 |
| e-mail | email | |
| back-end / front-end | backend / frontend | |
| file name / host name | filename / hostname | |
| and/or | 改写句子 | |
| comprise | consist of / include | |
| learnings | lessons / things you learned | |

## 包容性用词

| 避免 | 改用 |
|---|---|
| whitelist / blacklist | allowlist / denylist（或 blocklist） |
| master / slave | primary / replica、controller、leader，按语境选择 |
| dummy（值、变量） | placeholder、sample |
| sanity check | final check、quick check |
| crazy / insane | unexpected、complex |
| cripple | slow down、degrade |
| hang（指系统卡住） | stop responding、not responding |
| guys | everyone、folks |
| man-hours / manpower | person-hours / staff |
| native（指功能） | built-in |
| first-class citizen | 直接描述具体能力 |

## 夸大的断言

| 避免 | 改用 |
|---|---|
| best / fastest / simplest | 描述具体机制，并给出数据来源 |
| always / never | 只在能验证的范围内使用 |
| ensure / guarantee | 只在确实能保证时使用 |
| is secure / prevents X | is designed for security / helps prevent X |
