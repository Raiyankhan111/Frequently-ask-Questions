# Testing & Quality Assurance Plan: Enterprise FAQ Copilot

This document provides the test cases, performance benchmarking scripts, and administrative validation guidelines for the **Enterprise FAQ Copilot** solution.

---

## 1. Functional Test Cases

| ID | Test Scenario | Steps | Expected Result | Status |
|---|---|---|---|---|
| **TC-01** | Delegation Search | 1. Enter query "SSPR" in Search Box.<br>2. Verify if results include "Self-Service Password Reset".<br>3. Scroll down to trigger lazy loading. | Results load in <1 second. Lazy loading appends additional matching records automatically. | Pending |
| **TC-02** | Category Filtering | 1. Select "HR & Policies" pill.<br>2. Verify that all listed FAQs have HR category badge. | Gallery filters immediately. Non-matching items are excluded. | Pending |
| **TC-03** | Favorite Syncing | 1. Open FAQ details.<br>2. Toggle Star icon to active.<br>3. Go back to Home Portal.<br>4. Verify FAQ appears under "My Favorites". | Local device storage (`SaveData`) is committed. Item displays on home portal. | Pending |
| **TC-04** | Negative Feedback Trigger | 1. Open FAQ details.<br>2. Click "No, need details".<br>3. Input "Outdated instructions".<br>4. Click "Submit". | Record is created in `cr_FAQFeedback` and `NotifyAdminFlow` triggers successfully. | Pending |
| **TC-05** | Admin CRUD Panel | 1. Navigate to Admin Panel.<br>2. Click "+ Create New".<br>3. Input test data and click "Save".<br>4. Verify record exists in left pane gallery. | Record is created in Dataverse and list is automatically refreshed. | Pending |

---

## 2. Copilot Studio Conversational Test Cases

| ID | Input Query | Expected Bot Response / Action |
|---|---|---|
| **NL-01** | "How do I reset my password?" | Bot returns the specific password reset instructions matching the `IT Support` category. |
| **NL-02** | "Troubleshoot corporate VPN on Windows Laptop in New York" | Bot returns specific VPN instructions and suggests related networking FAQs. |
| **NL-03** | "What is the policy for dental care coverage?" | Bot retrieves health benefits instructions and displays details. |
| **NL-04** | "Where can I park my spaceship?" | Bot triggers **FallbackTopic** (no match found), prompts user to escalate, and alerts admin via email. |

---

## 3. Security & Access Control (RBAC) Verification

### Admin Access Test
- Log in with `admin@company.com` (or user in Admin AD group).
- Verify the **Admin** button is visible in the header.
- Navigate to the admin screen, edit an FAQ, and verify it successfully updates the database.

### End User Access Test
- Log in with standard user email (e.g., `user@company.com`).
- Verify the **Admin** button in the header is invisible.
- Try to navigate directly to the admin screen URL or via browser controls. Verify the app navigates the user back to the Portal screen automatically (enforced in `AdminDashboardScreen.OnVisible`).

---

## 4. Performance & Concurrency Benchmarking

The project requires support for **50+ concurrent users** and search response times **under 2 seconds**. 

### Concurrency Testing (Via JMeter or Azure Load Testing)
To simulate 50+ concurrent users querying the Dataverse search index:
1.  **Configure API endpoint:** Power Automate flow `cr_SearchFAQFlow` is exposed via HTTP POST request.
2.  **Generate Load Test Script (JMeter):**
    - Thread Group: 100 users ramping up in 10 seconds.
    - Loop Count: 10 queries per user.
    - HTTP Request: POST to flow trigger URL with payload `{"query": "reset password", "email": "loadtest@company.com"}`.
3.  **Performance Metrics Target:**
    - Error rate: < 0.5%
    - 95th Percentile Response Time: < 1.5 seconds.
    - Dataverse Search API throttle limit headroom: > 40%.

### Optimization Techniques Verified
- **Delegation:** By pushing all search and filter operations directly to the Dataverse cloud indexing engine, the local client (Canvas App) only handles rendering, minimizing memory overhead and battery usage on mobile devices.
- **Index Optimization:** Ensure text columns in Dataverse (`cr_question`, `cr_keywords`, `cr_tags`) have **Dataverse Search index** enabled in the Power Platform environment settings.
