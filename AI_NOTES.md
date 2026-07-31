# AI Notes

## Tool used
Claude

## Which part AI-generated and which written by me
- **AI-generated**: The initial structure of `src/main.py` (FastAPI app, the 5 endpoints,
  Pydantic models for `ExpenseCreate` and `Expense`) and `tests/test_main.py`, based on
  the requirements I described.
- **Written/done by me**: I created the project directory and folder structure myself
  before asking Claude for an approach — Claude only gave me the plan for how to structure
  it, I set it up on my own. I made small code changes on top of the generated code
  (not a full rewrite, but I didn't take the AI output blindly either). I entered all the
  test data (expenses, categories, amounts) myself when testing the API — I didn't use
  whatever sample inputs the AI suggested, I typed in my own values so I'd actually
  understand what was happening at each step. I also handled the entire Git/GitHub push
  myself — init, add, commit, branch, remote, push — without asking Claude to walk me
  through it, since I already knew the commands.

## What I validated / tested / changed and why
- I ran `pytest` locally and confirmed all 9 tests passed on my machine.
- I manually tested all 5 endpoints myself using the Swagger UI at `/docs` — added expenses with my own data, filtered by category, checked the totals endpoint, and deleted an expense by id.
- I noticed my totals output showed `"Beverage": 100` instead of `"Food"` — that was just because I labeled my own test entry "Beverage" instead of "Food"/"Coffee", not a bug. Confirmed the category field is free text, not a fixed list, so this was
expected behavior, not something to fix.
- I checked that deleting an id returns `204` and that fetching totals before vs after a delete gives different (correct) numbers — confirmed the total is calculated live off whatever is currently in the list, not cached.
- I went through `main.py` line by line afterward to actually understand the id generation (`itertools.count`), the category filter logic, and the total/by_category calculation, so I could explain it if asked — not just copy-paste it.

## AI suggestions I did NOT use, and why
- Didn't add the optional Docker support — the assignment didn't require it and I wanted to make sure the core 5 endpoints and tests were solid first, given the timeI had.
- Didn't use any of the AI's suggested test/sample data when actually testing — I entered my own expense entries so the testing reflected real understanding, not just re-running what was already given.

## Anything else worth noting
- I set up the project folder and initial structure on my own before getting any AI input on approach.
- I pushed everything to GitHub (init → add → commit → branch → push) myself without asking Claude to guide me through those steps, since I was already comfortable with Git.