# AI Coding Playbook Template

## 1. When I reach for AI first
- Want to write a specific code
- Debugging errors, like in the start Module Back-end the health check was not working cz it was also present in schemas/health.py
- Explaining code logic, after adding the Feature 1 (Due Dates) in Mid-course Project, how it handles incorrect dates

## 2. When I do not reach for AI
- The start of a project, the planning should be a draft done by me, in Module 1, when we wrote the user stories and ADR
- If i want to add features, I will think about new ideas
- If a decision should be made like what specific model to use, or anything additionla I would take the choice not leave it for the AI, Like in Module 2, we chose the ADR without the SQLite

## 3. My non-negotiables
- Review the code written by AI, when i was adding the features in mid course project, the front end will be updated but when i run the tracker, it will be disconnected from the backend
- 1 session (chat) per 1 request, always start a fresh chat, espacially in Module 2 when building the backend
- Keep sensitive or private data out of prompts

## 4. My review rules
- After adding or editing code, re check older features if they got affected by the new addition
- Tests for each feature and for each possible loop/error
- Check the user interface and the user experience

## 5. What I am still figuring out
- How much context I need before I ask for help
- When I should stop and work manually instead of prompting
- I will re-read and update this playbook after 30 days.

Decision Card
- For a new feature I reach for: CLaude for the planning, when writting the user stories and ADR
- For a code review I reach for: If full code review (like the logic) Claude, when giving full context it will get a detailed review
- For debugging I reach for: GitHub co-pilot inside VS Code, has already all context and have access to Git Hub repo, can check and read every line, easy to use
- For infrastructure I reach for: Claude
- I will never paste full code as it is into an AI tool, when i did that in Module 2, the health check was not imported correctly
- My one rule is: Write a detailed prompt + give context before each request
