# Route Scorecard

- total cases: `8`
- accuracy: `1.0`
- ambiguous cases: `0`
- no-route accuracy: `1.0`

## Route Metrics

| Route | Expected | Predicted | Precision | Recall | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: |
| `agent-team-work` | 3 | 3 | 1.0 | 1.0 | 0.938 |
| `project-session-team-bootstrap` | 2 | 2 | 1.0 | 1.0 | 0.958 |
| `no_route` | 3 | 3 | 1.0 | 1.0 | - |

## Confusion Matrix

| Expected \ Predicted | `agent-team-work` | `project-session-team-bootstrap` | `no_route` |
| --- | ---: | ---: | ---: |
| `agent-team-work` | 3 | 0 | 0 |
| `project-session-team-bootstrap` | 0 | 2 | 0 |
| `no_route` | 0 | 0 | 3 |

## Ambiguous Cases

| Family | Expected | Predicted | Margin |
| --- | --- | --- | ---: |
| - | - | - | - |
