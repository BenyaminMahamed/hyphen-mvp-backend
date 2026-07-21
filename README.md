# Ops Tracker — Django MVP (Part 2)

Backend for the Hyphen take-home assessment: an MVP that helps teams capture meeting notes, extract action items (via a mocked AI integration), assign owners, and track completion — reducing manual admin across spreadsheets and task trackers.

## Tech Stack
- Django 6.0
- Django REST Framework
- SQLite (local dev) — designed to run on PostgreSQL in production, no code changes required beyond `DATABASES` config

## Setup

```
git clone https://github.com/BenyaminMahamed/hyphen-mvp-backend.git
cd hyphen-mvp-backend
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

After creating a superuser, log into `/admin/` and create at least one `Team` and a `Profile` (linking your user to that team with a role of `manager` or `member`) before using the API — a `Profile` is required for permission checks to resolve.

## Apps

- **core** — `Team` and `Profile` (extends Django's built-in `User` via a linked profile rather than swapping `AUTH_USER_MODEL`, which keeps auth handling standard and lower-risk)
- **meetings** — `Meeting`, `MeetingNote`
- **actions** — `ActionItem`
- **ai_integration** — mock AI service (no models — pure service layer)

## Model Relationships & Reasoning

- **Profile → Team**: `ForeignKey` (one team per user). Role (`manager`/`member`) is a fixed field on `Profile`, not derived per-team, so a manager has manager visibility across every team, not just one.
- **Meeting → Team**: `ManyToManyField`. A meeting can span multiple teams (e.g. cross-team syncs), so this can't be a single FK.
- **MeetingNote → Meeting**: `ForeignKey` (many notes per meeting). Multiple people or sessions can log notes against the same meeting.
- **ActionItem → MeetingNote**: `ForeignKey` (not directly to `Meeting`), so every action item traces back to the specific note it was extracted from — this preserves an audit trail even when a meeting has several notes.

### `on_delete` reasoning
- `Profile.team` and `Meeting.created_by` use `PROTECT` — a `Team` or `User` deletion should never silently cascade into deleting meeting history or orphaning accountability records; it forces an explicit reassignment first.
- `MeetingNote.meeting` and `ActionItem.note` use `CASCADE` — a note has no independent meaning if its parent meeting is deleted, and the same logic applies to an action item and its source note.

## Permissions

- **Visibility**: Managers see all meetings, notes, and action items across every team. Members only see records involving their own team.
- **MeetingNote**: any team member can create a note. Editing or deleting an existing note is manager-only — this preserves the integrity of the record once action items have been extracted from it, without blocking the core capture workflow.
- **ActionItem**: completed action items are locked from further edits. The one exception is reassignment (changing `owner`), which only a manager can do on a completed item — matching the brief's rule that "only managers can reassign completed actions."
- **Meeting deletion**: blocked if any linked action item (via its notes) is still open, preventing loss of outstanding accountability.

## AI Integration

`ai_integration/services.py` exposes `generate_summary_and_actions(raw_text)`, which is called automatically when a `MeetingNote` is created. It's structured as the seam where a real AI provider (e.g. an LLM API) would plug in — the function signature and return shape (`{"summary": ..., "action_items": [...]}`) would stay identical if swapped for a real call, so nothing upstream would need to change.

The current mock splits raw text into sentences and flags any containing "to" or "follow" as likely action items, so the output actually varies with input rather than returning static text — useful for demoing live with different notes.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/login/` | POST | Obtain auth token |
| `/api/meetings/` | GET, POST | List / create meetings |
| `/api/meetings/{id}/` | GET, PUT, PATCH, DELETE | Meeting detail, update, delete (blocked if open actions remain) |
| `/api/meeting-notes/` | GET, POST | List / create notes (create triggers mock AI) |
| `/api/meeting-notes/{id}/` | GET, PUT, PATCH, DELETE | Note detail, update/delete (manager-only) |
| `/api/action-items/` | GET, POST | List / create action items |
| `/api/action-items/{id}/` | GET, PUT, PATCH | Action item detail, update (locked once completed, except manager reassignment) |
| `/api/action-items/completed/` | GET | Outgoing feed — all completed action items, for consumption by another internal system |

All endpoints (except login) require a token: `Authorization: Token <token>`.

## Assumptions

- A user belongs to exactly one team; role (manager/member) is global, not per-team.
- A meeting can involve multiple teams, but each note and action item still resolves back to a single team context via its meeting's teams.
- The mock AI service processes notes synchronously on creation, rather than as an async/background task — reasonable for an MVP's scale, would revisit for production with real, potentially slow AI provider calls.
- SQLite is used for local development; the brief specifies PostgreSQL is assumed for production, and no schema changes are required to switch.

## Business Rules Implemented

- Completed action items cannot be edited (except reassignment by a manager).
- Meetings cannot be deleted while linked action items remain open.
- Only managers can reassign a completed action item's owner.
- Only managers can edit or delete meeting notes.