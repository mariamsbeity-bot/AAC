## What I Shared With AI
| Item | Module | Risk Level | Reason |
|---|---|---|---|
| Task Tracker code | 2-5 | High | the backend was the start so it had to be perfect and solid thus spent much time to make sure every edge case was covered, the start with health check was not working |
| Test output and stack traces | 2-4 | High | some tests were missing so had to re-prompt to include each and every case |
| Frontend code | 3 | Medium | the only thinf here is the connection with the backend |
| Dockerfile and CI YAML | 4 | Low | Cause it is build on the project, so it was a solid one no mistakes since everything in the project was validated and tested |
| Any real external data I used by mistake | None | None | None |

## What I Received From AI
| Generated Thing | Module | Do I Understand It Line by Line? | Action |
|---|---|---|---|
| Backend models and validators | 2 | Mostly the routes and models | Everything is done here, the whole app runs here every error is handeled here |
| Frontend board and drag-and-drop logic | 3 | Partially, focused on the app connection | Apply the business rules for the drag and drop logic, and display the Kanban layout as UI  |
| CI workflow | 4 | yes | Contious integration file added so when push/or pull on GitHub, the tests run to validate everything |
| Dockerfile | 4 | yes | It creates a container for the app, then we can run it on any machine |
| Security findings and plans | 5 | yes | these findings alert us to some issues we don't think of, and the plans really make the job easier as it divide the job to several steps and make it more clear |