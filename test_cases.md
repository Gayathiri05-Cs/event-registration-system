# Test Case Table – Event Registration System

| Test ID | Scenario | Expected result |
|---|---|---|
| TC_EVENT_01 | Open home page | Event cards and details are displayed |
| TC_EVENT_02 | Search for `AI` | Matching event is displayed |
| TC_EVENT_03 | Filter by category `Technology` | Only technology events are displayed |
| TC_EVENT_04 | Filter by location `Chennai` | Only matching location events are displayed |
| TC_EVENT_05 | Open event details | Date, time, venue and available seats are shown |
| TC_EVENT_06 | Register with valid details | Registration saved and confirmation ID shown |
| TC_EVENT_07 | Register with invalid email | Validation error; no registration saved |
| TC_EVENT_08 | Register with invalid phone | Validation error; no registration saved |
| TC_EVENT_09 | Register twice for same event using same email | Second attempt blocked |
| TC_EVENT_10 | Fill all seats then register again | Event full message displayed |
| TC_EVENT_11 | Open organizer dashboard without login | Redirected to organizer login |
| TC_EVENT_12 | Login with valid demo credentials | Organizer dashboard opens |
| TC_EVENT_13 | Login with invalid password | Error message displayed |
| TC_EVENT_14 | Create event with valid data | Event saved and appears in organizer dashboard |
| TC_EVENT_15 | View participants | Registered participants are displayed |
| TC_EVENT_16 | Access another organizer's event participants | Not found / access denied |

## Demo registration data
- Name: Priya Sharma
- Email: priya@example.com
- Phone: 9876543210
