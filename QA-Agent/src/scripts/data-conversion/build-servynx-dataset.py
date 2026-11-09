"""
Builds the Servynx trial knowledge base for QA Agent.

Source: a read-only walkthrough of https://www.servynx.com (seeker view) on 2026-11-08.
Stories marked "Observed" were seen in the UI; "Inferred" ones come from on-screen
text (e.g. the Seeker/Provider switch, "when a provider purchases this lead") and
should be confirmed with the TrustyBytes team.

Outputs (same shapes as the existing healthcare data, so every existing script works):
  src/data/servynx/stories.json      -> like src/data/stories.json
  src/data/servynx/testcases.json    -> like src/data/testcases.json
  src/data/servynx/userstories.xlsx  -> same headers as src/data/userstories.xlsx
  src/data/servynx/testcases.xlsx    -> same headers as src/data/testcases.xlsx
  releases/servynx-trial/stories/*.txt

Run:  python3 src/scripts/data-conversion/build-servynx-dataset.py
"""
import json
import os
from datetime import date

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "src", "data", "servynx")
REL = os.path.join(ROOT, "releases", "servynx-trial", "stories")
TODAY = date(2026, 11, 8).isoformat()
NOW = TODAY + "T00:00:00.000Z"
PROJECT = "Servynx"
AUTHOR = "Gopi Rajendran"
VERSION = "servynx-trial-v1"

# (key, epic, module, summary, description, [acceptance criteria], priority, risk, basis)
STORIES = [
    ("SVX-001", "Authentication & Account", "Login",
     "Sign in and land on the seeker dashboard",
     "As a seeker, I want to sign in with my email so that I land on my dashboard with my account details shown in the header.",
     ["Given valid credentials, when the user signs in, then they are redirected to /dashboard and their email is shown in the header.",
      "Given invalid credentials, when the user signs in, then a clear error is shown and no session is created.",
      "Given a signed-out user, when they open /dashboard directly, then they are sent to sign in and returned to /dashboard afterwards."],
     "P1", "High", "Observed"),
    ("SVX-002", "Seeker Dashboard", "Dashboard",
     "Dashboard summary tiles",
     "As a seeker, I want summary tiles for Total Requirements, Active, Providers Interested and Invites Sent so that I can see my activity at a glance.",
     ["Given a new account, when the dashboard loads, then all four tiles show 0 (never a dash or blank once loading finishes).",
      "Given posted requirements, when the dashboard loads, then each tile matches the counts on My Requirements and Invitations Sent.",
      "While data is loading, tiles show a loading state rather than stale values."],
     "P2", "Medium", "Observed"),
    ("SVX-003", "Seeker Dashboard", "Dashboard",
     "Recent requirements and empty state",
     "As a seeker, I want to see my recent requirements on the dashboard, with a clear call to action when I have none.",
     ["Given no requirements, then the 'No requirements yet' message and a 'Post your first requirement' link to /requirements/new are shown.",
      "Given requirements exist, then the most recent ones are listed and 'View all' opens /requirements."],
     "P3", "Low", "Observed"),
    ("SVX-004", "AI Requirement Intake", "Quick Post",
     "Quick Post from the dashboard",
     "As a seeker, I want to describe my need in one sentence on the dashboard so that AI categorises it and pre-fills the requirement form.",
     ["Given text in Quick Post, when the user clicks Next or presses Ctrl+Enter, then they reach the requirement form with category and description pre-filled.",
      "Given an empty Quick Post, when the user clicks Next, then the action is blocked with a prompt to describe the need.",
      "'Fill Form Instead' opens /requirements/new with an empty form."],
     "P1", "High", "Observed"),
    ("SVX-005", "Post Requirement", "Post Requirement",
     "Select service category and subcategory",
     "As a seeker, I want to search and pick a category and subcategory (e.g. IT & Digital Services > Software Testing / QA) so that the matching requirement form loads.",
     ["Given the category search, when the user types a term (e.g. 'website'), then matching subcategories are listed with their parent group.",
      "Given a subcategory is chosen, then its versioned form loads (e.g. 'Software Testing / QA - Standard v1').",
      "Given a term with no match, then an empty-result message is shown."],
     "P1", "High", "Observed"),
    ("SVX-006", "Post Requirement", "Post Requirement",
     "Validate service location postal code by region",
     "As a seeker, I want my postal code validated against my region so that providers in the right area see my requirement.",
     ["Given valid codes for supported regions (e.g. 600001 India, M5H 2N2 Canada, 10001 US), then the code is accepted.",
      "Given an invalid or mismatched code, then an inline error is shown and submission is blocked.",
      "Leading/trailing spaces and lowercase Canadian codes are normalised."],
     "P1", "High", "Observed"),
    ("SVX-007", "Post Requirement", "Post Requirement",
     "Complete and submit the requirement form",
     "As a seeker, I want to enter what I need, budget, timeline and notes, then submit so that providers can respond.",
     ["'Describe what you need' is mandatory; submission is blocked with an inline message when empty.",
      "Timeline offers As soon as possible, Within a week, Within a month and Flexible.",
      "Budget accepts only valid non-negative amounts.",
      "On successful submit, the requirement appears on My Requirements as OPEN and dashboard counts update."],
     "P1", "Critical", "Observed"),
    ("SVX-008", "Post Requirement", "Attachments",
     "Attach supporting files to a requirement",
     "As a seeker, I want to attach up to 5 files of 10MB each so that providers understand my need.",
     ["Up to 5 files of up to 10MB each are accepted.",
      "A 6th file, or a file over 10MB, is rejected with a clear message and the others are kept.",
      "Executable or unsupported file types are rejected."],
     "P2", "High", "Observed"),
    ("SVX-009", "Settings & Privacy", "Post Requirement",
     "Control which contact details providers see after unlocking",
     "As a seeker, I want to choose whether Email, Phone and/or Chat are shared when a provider unlocks my lead.",
     ["Only the checked channels are revealed to a provider after unlocking.",
      "With nothing checked, all channels are shared (as the form states).",
      "The choice is stored with the requirement and shown when it is viewed later."],
     "P1", "Critical", "Observed"),
    ("SVX-010", "AI Requirement Intake", "Just Say",
     "Just Say free-text intake",
     "As a seeker, I want to describe my need in up to 1000 characters so that AI suggests a category and pre-fills the form.",
     ["The counter shows n/1000 and input stops at 1000 characters.",
      "Next suggests a category and pre-fills the form, which the user can still edit.",
      "Vague or off-topic text yields a request for more detail rather than a wrong category."],
     "P2", "Medium", "Observed"),
    ("SVX-011", "AI Requirement Intake", "Voice",
     "Voice intake",
     "As a seeker, I want to speak my requirement so that it is transcribed and used to pre-fill the form.",
     ["Microphone permission is requested; if denied, a helpful message points to Fill Form or Just Say.",
      "The transcript is shown and editable before the form is pre-filled."],
     "P3", "Medium", "Observed"),
    ("SVX-012", "My Requirements", "My Requirements",
     "Track posted requirements",
     "As a seeker, I want a list of my requirements with their status so that I can follow up and unlock provider contacts.",
     ["Each requirement shows title, category, status and date.",
      "Refresh reloads the list without a full page reload.",
      "'Post new' opens /requirements/new; the empty state links to posting."],
     "P2", "Medium", "Observed"),
    ("SVX-013", "Provider Discovery", "Find Providers",
     "Search providers by category, region and postal code",
     "As a seeker, I want to filter providers by category, region (Canada, US, India, Middle East, UK, EU) and postal code.",
     ["Filters can be combined, and results show only providers with completed work in that category and region.",
      "With no results, '0 providers found' and a hint to change filters are shown.",
      "A 'Searching…' state is shown during the query and replaced by results or the empty state."],
     "P2", "Medium", "Observed"),
    ("SVX-014", "Invitations", "Invitations Sent",
     "Invite providers and track invitations",
     "As a seeker, I want to invite providers to my requirement and track invitations as Pending, Accepted or Declined.",
     ["The All, Pending, Accepted and Declined tabs show only matching invitations.",
      "A new invitation appears as Pending and increments the dashboard's Invites Sent.",
      "An empty tab shows an empty-state message rather than a blank area."],
     "P2", "Medium", "Observed"),
    ("SVX-015", "Connects & Chat", "My Connects",
     "View connected providers",
     "As a seeker, I want a list of providers I have connected with so that I can open a chat with any of them.",
     ["The list loads, and 'Loading…' is replaced by results or an empty state within a reasonable time.",
      "'All Chats' opens /chat."],
     "P3", "Medium", "Observed"),
    ("SVX-016", "Connects & Chat", "Chat",
     "Chat with connected providers",
     "As a seeker, I want to message my connected providers so that we can agree scope and price.",
     ["Only connected providers can be messaged.",
      "Messages are delivered and shown in order with timestamps; Refresh fetches new messages.",
      "Contact details hidden by the privacy settings are not exposed through chat metadata."],
     "P2", "High", "Observed"),
    ("SVX-017", "Credits & Payments", "Credits",
     "Buy credits",
     "As a seeker, I want to buy credits (quick select 25, 50, 100, 250, 500 or a custom amount) so that I can unlock provider contact details.",
     ["Quick select fills the amount; a custom amount accepts only positive whole numbers within limits.",
      "The price follows the user's pricing region and the Pricing Tiers table.",
      "After a successful payment, Available Credits and the header balance update and a Transaction History row is added.",
      "A failed or cancelled payment leaves the balance unchanged and shows a clear message."],
     "P1", "Critical", "Observed"),
    ("SVX-018", "Credits & Payments", "Credits",
     "Unlock provider contact details with credits",
     "As a seeker, I want to spend credits to unlock a provider's contact details.",
     ["Unlocking deducts the stated credits exactly once (no double charge on double click or refresh).",
      "With too few credits, the unlock is blocked and the user is offered Buy Credits.",
      "Only the channels permitted by the other party's privacy settings are revealed."],
     "P1", "Critical", "Inferred"),
    ("SVX-019", "Settings & Privacy", "Settings",
     "Edit profile, country and pricing region",
     "As a user, I want to set my full name, display name, country and pricing region so that postal validation and pricing are correct.",
     ["Full name (max 100) and display name (max 60, shown publicly) are mandatory, with live counters.",
      "Selecting a country auto-sets the pricing region, which can be overridden.",
      "Save Profile persists the changes and shows a confirmation.",
      "Verified contact details on file are shown; the signed-in email should appear rather than 'No email on file'."],
     "P2", "Medium", "Observed"),
    ("SVX-020", "Settings & Privacy", "Settings",
     "Change password",
     "As a user, I want to change my password from Settings so that I can keep my account secure.",
     ["The current password is required; the new password must meet the strength rules and be confirmed.",
      "Other sessions are signed out after a change (or the user is offered this)."],
     "P1", "High", "Observed"),
    ("SVX-021", "Settings & Privacy", "Settings",
     "Delete account with typed confirmation",
     "As a user, I want to permanently delete my account with a typed confirmation so that my data is anonymised.",
     ["'Delete My Account' stays disabled until the exact text DELETE MY ACCOUNT is typed.",
      "After deletion, the user is signed out, cannot sign in again, and personal data is anonymised."],
     "P1", "Critical", "Observed"),
    ("SVX-022", "Role Switch & Provider Leads", "Role Switch",
     "Switch between Seeker and Provider roles",
     "As a user, I want to switch between Seeker and Provider views so that one account can both post and respond to requirements.",
     ["The header badge shows the current role, and Switch toggles the navigation to the other role's menu.",
      "The role persists across page reloads.",
      "Seeker-only pages are not reachable in Provider view and vice versa."],
     "P2", "High", "Inferred"),
    ("SVX-023", "Role Switch & Provider Leads", "Provider Leads",
     "Provider purchases a lead",
     "As a provider, I want to see matching requirements and purchase a lead with credits so that I can contact the seeker.",
     ["Providers see only requirements matching their categories and region.",
      "Purchasing a lead deducts credits and reveals only the contact channels the seeker allowed.",
      "The seeker's 'Providers Interested' count increases."],
     "P1", "Critical", "Inferred"),
    ("SVX-024", "Notifications", "Notifications",
     "In-app notifications",
     "As a user, I want notifications for invitations, provider interest and new chat messages.",
     ["The bell shows an unread indicator for new events, and opening it lists them newest first.",
      "Clicking a notification opens the related page and marks it read."],
     "P3", "Low", "Observed"),
]

# test cases per story: (title, preRequisites, steps[], expected, type, automation)
TESTS = {
    "SVX-001": [
        ("Valid sign-in redirects to dashboard", "Registered seeker account",
         ["Open https://www.servynx.com", "Sign in with valid email and password"],
         "User lands on /dashboard; header shows the user's email and the Seeker badge.", "Functional", "Automated"),
        ("Invalid password is rejected", "Registered seeker account",
         ["Open sign-in", "Enter valid email and wrong password", "Submit"],
         "Error message shown; user stays signed out; no session cookie set.", "Negative", "Automated"),
        ("Deep link to dashboard while signed out", "Signed out",
         ["Open /dashboard directly"],
         "User is sent to sign-in and, after signing in, returned to /dashboard.", "Security", "Automated"),
    ],
    "SVX-002": [
        ("New account shows zero counts", "New seeker account with no activity",
         ["Sign in", "Wait for dashboard to finish loading"],
         "Total Requirements, Active, Providers Interested and Invites Sent all show 0, not '—'.", "Functional", "Automated"),
        ("Tile counts match list pages", "Seeker with 2 requirements and 1 invite",
         ["Note dashboard tile values", "Open My Requirements and Invitations Sent and count rows"],
         "Tile values equal the counts on the list pages.", "Integration", "Automated"),
    ],
    "SVX-003": [
        ("Empty state call to action", "Seeker with no requirements",
         ["Open dashboard", "Click 'Post your first requirement'"],
         "'No requirements yet' shown; link opens /requirements/new.", "Functional", "Automated"),
        ("View all opens My Requirements", "Seeker with requirements",
         ["Open dashboard", "Click 'View all' in Recent Requirements"],
         "/requirements opens listing all requirements.", "Functional", "Automated"),
    ],
    "SVX-004": [
        ("Quick Post pre-fills form", "Signed-in seeker",
         ["Type 'I need regression testing for my web app in Toronto' in Quick Post", "Click Next"],
         "Requirement form opens with IT & Digital Services > Software Testing / QA and the description pre-filled.", "Functional", "Manual"),
        ("Ctrl+Enter submits Quick Post", "Signed-in seeker",
         ["Type a need in Quick Post", "Press Ctrl+Enter"],
         "Same result as clicking Next.", "Functional", "Automated"),
        ("Empty Quick Post is blocked", "Signed-in seeker",
         ["Leave Quick Post empty", "Click Next"],
         "No navigation; user is prompted to describe the need.", "Negative", "Automated"),
    ],
    "SVX-005": [
        ("Search finds subcategory", "On /requirements/new",
         ["Click Service Category", "Type 'testing'"],
         "'IT & Digital Services / Software Testing / QA' appears in the list.", "Functional", "Automated"),
        ("Selecting subcategory loads versioned form", "On /requirements/new",
         ["Select Software Testing / QA"],
         "Form 'Software Testing / QA - Standard v1' loads with description, budget, timeline, notes, attachments and privacy fields.", "Functional", "Automated"),
        ("Unknown search term", "On /requirements/new",
         ["Type 'zzzz' in category search"],
         "An empty-result message is shown; no form loads.", "Negative", "Automated"),
    ],
    "SVX-006": [
        ("Valid postal codes per region", "On requirement form",
         ["Enter 600001 (India)", "Enter M5H 2N2 (Canada)", "Enter 10001 (US)"],
         "Each code is accepted for its region.", "Functional", "Automated"),
        ("Invalid postal code blocked", "On requirement form",
         ["Enter 'ABC'", "Try to submit"],
         "Inline error shown; submission blocked.", "Negative", "Automated"),
        ("Canadian code normalisation", "On requirement form, region Canada",
         ["Enter ' m5h2n2 '"],
         "Accepted and shown as 'M5H 2N2'.", "Boundary", "Automated"),
    ],
    "SVX-007": [
        ("Submit with all fields", "Category, valid postal code chosen",
         ["Fill description, budget 500, timeline 'Within a week', notes", "Click Submit Requirement"],
         "Success shown; requirement listed as OPEN on My Requirements; dashboard Total and Active increase by 1.", "End-to-end", "Automated"),
        ("Mandatory description", "Category chosen",
         ["Leave description empty", "Click Submit Requirement"],
         "Inline error on description; nothing posted.", "Negative", "Automated"),
        ("Budget rejects negative and non-numeric values", "Category chosen",
         ["Enter -100 in budget", "Enter 'abc' in budget"],
         "Both values are rejected with a message.", "Boundary", "Automated"),
        ("Double click does not create duplicates", "Valid form",
         ["Double-click Submit Requirement quickly"],
         "Exactly one requirement is created.", "Negative", "Automated"),
    ],
    "SVX-008": [
        ("Upload 5 files within limit", "On requirement form",
         ["Attach 5 PDFs of 2MB each"],
         "All 5 are listed and uploaded.", "Functional", "Automated"),
        ("Sixth file rejected", "5 files attached",
         ["Attach a 6th file"],
         "Rejected with a 'max 5 files' message; existing files kept.", "Boundary", "Automated"),
        ("Oversized file rejected", "On requirement form",
         ["Attach an 11MB file"],
         "Rejected with a '10MB limit' message.", "Boundary", "Automated"),
    ],
    "SVX-009": [
        ("Share only chat", "Requirement form",
         ["Check only Chat", "Submit", "As provider, unlock the lead"],
         "Provider sees chat access only; email and phone stay hidden.", "Security", "Manual"),
        ("Nothing checked shares everything", "Requirement form",
         ["Leave Email, Phone and Chat unchecked", "Submit", "As provider, unlock"],
         "All contact channels are revealed, matching the on-screen note.", "Functional", "Manual"),
    ],
    "SVX-010": [
        ("1000 character limit", "Just Say tab",
         ["Paste 1200 characters"],
         "Input stops at 1000; counter shows 1000/1000.", "Boundary", "Automated"),
        ("AI suggests category", "Just Say tab",
         ["Type 'Need someone to set up CI/CD on AWS'", "Click Next"],
         "Cloud & DevOps is suggested; form pre-filled and editable.", "Functional", "Manual"),
    ],
    "SVX-011": [
        ("Microphone permission denied", "Voice tab, browser mic blocked",
         ["Click Voice and start recording"],
         "Helpful message suggests Fill Form or Just Say; no crash.", "Negative", "Manual"),
    ],
    "SVX-012": [
        ("Requirement list shows status", "Seeker with posted requirement",
         ["Open My Requirements"],
         "Row shows title, category, OPEN status and date.", "Functional", "Automated"),
        ("Refresh reloads list", "On My Requirements",
         ["Post a requirement in another tab", "Click Refresh"],
         "New requirement appears without a full page reload.", "Functional", "Automated"),
    ],
    "SVX-013": [
        ("Combined filters", "Providers exist in IT & Digital Services, Canada",
         ["Open Find Providers", "Select category IT & Digital Services and region Canada"],
         "Only matching providers are listed.", "Functional", "Automated"),
        ("No results state", "No providers in selection",
         ["Select a category and region with no providers"],
         "'0 providers found' and 'No providers found' hint shown; 'Searching…' cleared.", "Negative", "Automated"),
    ],
    "SVX-014": [
        ("Status tabs filter invitations", "Invitations in each status",
         ["Open Invitations Sent", "Click Pending, Accepted, Declined"],
         "Each tab lists only invitations in that status.", "Functional", "Automated"),
        ("Empty tab message", "No declined invitations",
         ["Open Declined tab"],
         "An empty-state message is shown, not a blank area.", "Usability", "Manual"),
    ],
    "SVX-015": [
        ("Connects page leaves loading state", "Seeker with no connects",
         ["Open My Connects", "Wait 10 seconds"],
         "'Loading…' is replaced by an empty state.", "Performance", "Automated"),
    ],
    "SVX-016": [
        ("Send and receive messages", "Seeker connected to a provider",
         ["Open Chat", "Send 'Hello'", "Reply as provider", "Click Refresh"],
         "Messages appear in order with timestamps on both sides.", "End-to-end", "Manual"),
        ("Cannot message non-connected provider", "Provider not connected",
         ["Attempt to open a chat with the provider via URL"],
         "Access is denied; no message is sent.", "Security", "Automated"),
    ],
    "SVX-017": [
        ("Quick select fills amount", "On /credits",
         ["Click 100"],
         "Amount field shows 100 and the price follows the user's region tier.", "Functional", "Automated"),
        ("Invalid custom amounts", "On /credits",
         ["Enter 0", "Enter -5", "Enter 10.5"],
         "Each value is rejected; Buy Credits stays disabled.", "Boundary", "Automated"),
        ("Successful purchase updates balance", "Test payment method",
         ["Buy 25 credits", "Complete payment in test mode"],
         "Available Credits and header balance show 25; Transaction History has a new row.", "End-to-end", "Manual"),
        ("Cancelled payment", "Test payment method",
         ["Start purchase", "Cancel at the payment step"],
         "Balance unchanged; clear cancellation message.", "Negative", "Manual"),
    ],
    "SVX-018": [
        ("Unlock deducts credits once", "Seeker with 50 credits and an interested provider",
         ["Click unlock", "Double-click and refresh during the request"],
         "Credits deducted exactly once; contact details revealed.", "Negative", "Manual"),
        ("Insufficient credits", "Seeker with 0 credits",
         ["Try to unlock a provider"],
         "Blocked with an offer to Buy Credits.", "Negative", "Automated"),
    ],
    "SVX-019": [
        ("Name length limits", "On Settings > Profile",
         ["Enter 101 characters in Full Name", "Enter 61 characters in Display Name"],
         "Input stops at 100 and 60; counters correct.", "Boundary", "Automated"),
        ("Country auto-sets pricing region", "On Settings > Profile",
         ["Select country India"],
         "Pricing region auto-sets to India and can be overridden.", "Functional", "Automated"),
        ("Signed-in email shown in contact details", "Signed in with email",
         ["Open Settings > Profile > Contact Details"],
         "Signed-in email is listed. (Trial observation 2026-11-08: shows 'No email on file' while the header shows the email.)", "Functional", "Manual"),
    ],
    "SVX-020": [
        ("Wrong current password", "On Settings > Password",
         ["Enter wrong current password and a valid new password", "Save"],
         "Rejected; password unchanged.", "Security", "Automated"),
        ("Weak new password", "On Settings > Password",
         ["Enter correct current password and '123' as new password"],
         "Strength rule error shown.", "Negative", "Automated"),
    ],
    "SVX-021": [
        ("Delete button gated by exact phrase", "Test account on Settings",
         ["Type 'delete my account' (lowercase)", "Type 'DELETE MY ACCOUNT'"],
         "Button disabled for the lowercase text and enabled only for the exact phrase.", "Security", "Automated"),
        ("Deleted account cannot sign in", "Disposable test account",
         ["Delete the account", "Try to sign in again"],
         "Sign-in fails; personal data is anonymised.", "End-to-end", "Manual"),
    ],
    "SVX-022": [
        ("Switch role toggles navigation", "Account with both roles",
         ["Click Switch in the header"],
         "Badge changes to Provider and the navigation shows the provider menu.", "Functional", "Manual"),
        ("Role persists after reload", "Provider view active",
         ["Reload page"],
         "Provider view remains.", "Functional", "Automated"),
    ],
    "SVX-023": [
        ("Provider sees only matching leads", "Provider in Software Testing / QA, Canada",
         ["Seeker posts a QA requirement with a Canadian postal code", "Provider opens leads"],
         "The requirement is listed; requirements in other categories or regions are not.", "Integration", "Manual"),
        ("Lead purchase respects seeker privacy", "Seeker shared only Chat",
         ["Provider purchases the lead"],
         "Only chat is available; the seeker's Providers Interested count increases by 1.", "Security", "Manual"),
    ],
    "SVX-024": [
        ("Notification on invitation response", "Seeker with a pending invite",
         ["Provider accepts invitation", "Seeker opens the bell"],
         "Unread notification shown; clicking opens Invitations Sent and marks it read.", "Functional", "Manual"),
    ],
}


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(REL, exist_ok=True)

    stories = []
    for i, (key, epic, module, summary, desc, ac, prio, risk, basis) in enumerate(STORIES, 1):
        stories.append({
            "key": key, "summary": summary, "description": desc,
            "status": {"name": "To Do", "category": "To Do"},
            "priority": {"name": prio, "id": prio[-1]},
            "assignee": None, "reporter": None, "created": NOW, "updated": NOW,
            "components": [module], "labels": ["servynx", basis.lower()], "fixVersions": [VERSION],
            "storyPoints": None, "project": PROJECT, "epic": epic,
            "acceptanceCriteria": "\n".join(ac), "businessValue": "", "risk": risk,
            "dependencies": "", "notes": f"{basis} during Servynx trial walkthrough {TODAY}",
            "sprint": None, "team": None, "issueLinks": [], "url": "https://www.servynx.com",
            "sourceType": "excel", "importedAt": NOW, "originalRowIndex": i,
        })
        with open(os.path.join(REL, f"{key.lower()}.txt"), "w") as f:
            f.write(f"User Story: {key} — {summary}\n\nSummary:\n{desc}\n\nEpic:\n{epic}\n\n"
                    "Acceptance Criteria:\n\n" + "\n\n".join(ac) +
                    f"\n\nPriority: {prio}\nRisk: {risk}\nStatus: To Do\nBasis: {basis}\n")

    module_of = {s[0]: s[2] for s in STORIES}
    risk_of = {s[0]: s[7] for s in STORIES}
    prio_of = {s[0]: s[6] for s in STORIES}
    tests, n = [], 0
    for key, cases in TESTS.items():
        for title, pre, steps, expected, ttype, auto in cases:
            n += 1
            tests.append({
                "module": module_of[key], "id": f"SVX_TC_{n:03d}", "preRequisites": pre,
                "title": title, "description": f"Verify {title[0].lower() + title[1:]}",
                "steps": "\r\n".join(f"{j}.{s}" for j, s in enumerate(steps, 1)),
                "expectedResults": expected, "automationManual": auto, "priority": prio_of[key],
                "createdBy": AUTHOR, "createdDate": TODAY, "lastModifiedDate": TODAY,
                "risk": risk_of[key], "version": VERSION, "type": ttype, "linkedStories": key,
            })

    json.dump(stories, open(os.path.join(OUT, "stories.json"), "w"), indent=2, ensure_ascii=False)
    json.dump(tests, open(os.path.join(OUT, "testcases.json"), "w"), indent=2, ensure_ascii=False)

    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "UserStories"
    ws.append(["summary", "projectName", "description", "acceptanceCriteria", "storyId", "parentSummary",
               "statusCategory", "priority", "risk", "createdDate", "lastModifiedDate"])
    for s in stories:
        ws.append([s["summary"], PROJECT, s["description"], s["acceptanceCriteria"], s["key"], s["epic"],
                   "To Do", s["priority"]["name"], s["risk"], TODAY, TODAY])
    wb.save(os.path.join(OUT, "userstories.xlsx"))

    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "TestCases"
    ws.append(["module", "testCaseId", "preRequisites", "title", "description", "steps", "expectedResults",
               "priority", "risk", "createdBy", "createdDate", "lastModifiedDate", "linkedStories",
               "automationManual", "version", "type"])
    for t in tests:
        ws.append([t["module"], t["id"], t["preRequisites"], t["title"], t["description"], t["steps"],
                   t["expectedResults"], t["priority"], t["risk"], t["createdBy"], t["createdDate"],
                   t["lastModifiedDate"], t["linkedStories"], t["automationManual"], t["version"], t["type"]])
    wb.save(os.path.join(OUT, "testcases.xlsx"))

    print(f"Servynx dataset: {len(stories)} stories, {len(tests)} test cases -> {OUT}")


if __name__ == "__main__":
    main()
