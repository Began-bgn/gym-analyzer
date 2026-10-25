## Weekly automation

`flask generate-review` creates (or reuses) the AI review for the last full Mon-Sun week.

### macOS / Linux (cron)

Run `crontab -e` and add (Mondays at 08:00):

    0 8 * * 1 cd /Users/began/gym-analyzer && /Users/began/gym-analyzer/venv/bin/flask generate-review >> review.log 2>&1

cron starts with an empty environment and the wrong folder, so the line must
`cd` into the project (the database path is relative) and call the venv's
`flask` by full path. If the Mac is asleep at 08:00, the job is skipped.

### Windows (Task Scheduler)

Create a basic task, trigger Weekly on Monday 08:00, action "Start a program":

- Program: `C:\path\to\gym-analyzer\venv\Scripts\flask.exe`
- Arguments: `generate-review`
- Start in: `C:\path\to\gym-analyzer`
