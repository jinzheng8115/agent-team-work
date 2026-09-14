# Failure Cases

These cases are intentionally retained as regression evidence.

| Failure | Trigger | Required response |
| --- | --- | --- |
| Missing verification | A member report omits `verification` or `dispatch_key`. | Keep the task in `rework`; reuse the same member session and increment `attempt`. |
| Premature dependent stage | A prior task is reported but not accepted. | Do not dispatch the dependent stage. |
| Unknown send result | A send or create operation times out or returns an unclear result. | Query the bound task/thread first; do not duplicate the send. |
| Cross-project binding | A member thread or checkout does not match the selected project. | Mark the binding blocked and stop mutation. |
| Explanation near-neighbor | The user asks only for an explanation. | Do not create a project team or call thread tools. |
| Missing native surface | A target only carries metadata and has no client enforcement. | Keep the residual risk visible; do not claim native enforcement. |

### Missing verification

The first smoke run deliberately omitted `verification` and `dispatch_key`; the Leader kept the task in `rework` and reused the same member session.

### Unknown send result

An unclear create or send response remains `unknown` until the bound project/thread is queried; the workflow never retries blindly.
