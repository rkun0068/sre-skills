# NAME reference

<!-- Use one of the following section patterns: commands, configuration, or both. Keep entries in a predictable order (alphabetical or by workflow). -->

<!-- One sentence: what this reference covers. -->

## Commands

### `TOOL SUBCOMMAND`

<!-- One sentence starting with a verb in third person: "Creates a ...". -->

**Synopsis**

```text
TOOL SUBCOMMAND NAME [--flag=VALUE] [--force]
```

**Arguments and flags**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `NAME` | string | Yes | | The name of the ... |
| `--flag` | string | No | `value` | ... |

**Examples**

<!-- Runnable examples only: no [ ], { | }, or ... in copyable commands. -->

```bash
TOOL SUBCOMMAND example-name
```

**Exit codes**

| Code | Meaning |
|---|---|
| `0` | Success. |

## Configuration

### `KEY_NAME`

| Property | Value |
|---|---|
| Type | |
| Default | |
| Allowed values | |
| Requires restart | |

<!-- Description: what the setting controls and how each value changes behavior. Add an example. -->

```yaml
```

<!--
Self-check:
- [ ] Every public command, flag, and setting is listed, and names match the code exactly.
- [ ] Defaults and allowed values come from the code, not memory.
- [ ] Boolean descriptions state behavior for both true and false.
- [ ] Deprecated items say what to use instead and since which version.
-->
