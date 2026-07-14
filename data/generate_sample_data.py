#!/usr/bin/env python3
import csv
import os
import random
import uuid
from datetime import datetime, timedelta

def generate_faqs(output_path):
    print("Generating exactly 4,000 unique FAQ records using combinatorial structures...")

    # Data lists for variables
    systems = ["Workday", "SAP Concur", "Microsoft Teams", "Outlook", "Office 365", "Salesforce", "ServiceNow", "Jira", "GitHub", "Zoom", "OneDrive", "SharePoint", "Slack", "Figma", "Adobe Creative Cloud"]
    devices = ["MacBook Pro", "Windows Laptop", "iPhone", "Android Phone", "iPad", "ThinkPad"]
    locations = ["New York", "London", "San Francisco", "Austin", "Sydney", "Bangalore", "Singapore", "Munich", "Toronto", "Paris"]
    teams = ["Marketing", "Engineering", "Product Management", "Sales", "Customer Success", "Legal", "Operations", "R&D", "Finance", "Human Resources"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    years = ["2024", "2025", "2026"]

    # Curated Base FAQ Questions (will always be included at the beginning)
    records = []
    generated_questions = set()

    # Curated standard FAQs
    curated = [
        {
            "Question": "How do I reset my password?",
            "Answer": "Go to settings.company.com > Security > Reset Password and verify your identity via Multi-Factor Authentication (MFA).",
            "Category": "IT Support",
            "SubCategory": "Password & Login",
            "Keywords": "password, login, reset, credentials, mfa",
            "Tags": "#it;#login;#security",
            "Priority": "High",
            "Status": "Published"
        },
        {
            "Question": "How do I connect to VPN?",
            "Answer": "Open GlobalProtect VPN on your laptop, enter the portal address 'vpn.company.com', and authenticate using your Microsoft Authenticator MFA.",
            "Category": "IT Support",
            "SubCategory": "VPN & Network",
            "Keywords": "vpn, network, remote, access, connect",
            "Tags": "#it;#network;#remote",
            "Priority": "High",
            "Status": "Published"
        },
        {
            "Question": "Where do I submit expense reports?",
            "Answer": "Log into SAP Concur at concur.company.com and submit your expense report with receipts attached. Make sure to specify the correct cost center.",
            "Category": "Finance & Expenses",
            "SubCategory": "Expense Filing",
            "Keywords": "expense, concur, money, reimbursement, receipt",
            "Tags": "#finance;#expense;#concur",
            "Priority": "Medium",
            "Status": "Published"
        },
        {
            "Question": "How do I request maternity or paternity leave?",
            "Answer": "Request leaves of absence in Workday under 'Time Off > Leave of Absence'. Contact HR Benefits at benefits@company.com to discuss paid options.",
            "Category": "HR & Policies",
            "SubCategory": "PTO & Leaves",
            "Keywords": "maternity, paternity, baby, leave, pto, workday",
            "Tags": "#hr;#pto;#leave",
            "Priority": "High",
            "Status": "Published"
        }
    ]

    for item in curated:
        uid = str(uuid.uuid4())
        created = datetime.now() - timedelta(days=random.randint(100, 500))
        updated = created + timedelta(days=random.randint(1, 90))
        item.update({
            "FAQID": uid,
            "CreatedDate": created.strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedDate": updated.strftime("%Y-%m-%d %H:%M:%S")
        })
        records.append(item)
        generated_questions.add(item["Question"].lower())

    # Combinatorial generator configuration
    # Each item corresponds to a subcategory structure which generates unique variations.
    generators = [
        # 1. Password & Login
        {
            "category": "IT Support",
            "subcategory": "Password & Login",
            "verbs": ["How do I reset my", "What is the way to change my", "Where do I recover the", "Steps to unlock my", "I need to update my"],
            "nouns": ["password for {system}", "MFA settings for {system}", "login credentials for {system}", "access settings on {system}"],
            "contexts": ["on my {device}", "while working remotely", "from the {location} office", "for my {team} account"],
            "answer": "To perform operations on your {noun_str}, log into identity.company.com, navigate to Security settings, and authenticate using your security key or MFA. Contact IT at ext. 4357 if your account is fully locked.",
            "keywords": ["password", "login", "mfa", "reset", "security", "credentials"],
            "tags": "#it;#login;#security"
        },
        # 2. VPN & Network
        {
            "category": "IT Support",
            "subcategory": "VPN & Network",
            "verbs": ["How do I connect to the", "Troubleshooting steps for the", "Why am I unable to access the", "How to set up the", "Guide to connect to"],
            "nouns": ["corporate VPN network", "office Wi-Fi connection", "secure file sharing server", "internal database network"],
            "contexts": ["on my {device}", "from the {location} branch", "while traveling", "for the {team} team"],
            "answer": "To access the {noun_str}, open your network preferences, select the correct client, and input your corporate credentials. Ensure your local internet is active. For VPN, use vpn.company.com.",
            "keywords": ["vpn", "wifi", "network", "internet", "connect", "access"],
            "tags": "#it;#network;#remote"
        },
        # 3. Email & Calendar
        {
            "category": "IT Support",
            "subcategory": "Email & Calendar",
            "verbs": ["How do I request a", "Steps to configure a", "Can I set up a shared", "Troubleshoot access to a"],
            "nouns": ["mailbox for {system}", "calendar delegation in {system}", "distribution list for {team}", "archive folder in {system}"],
            "contexts": ["on Outlook for {device}", "using the web version", "in the {location} office"],
            "answer": "For configurations involving your {noun_str}, submit a ticket to the Email Services Team at support.company.com. Shared mailboxes and delegations require manager approval.",
            "keywords": ["email", "outlook", "calendar", "shared", "mailbox", "permissions"],
            "tags": "#it;#email;#outlook"
        },
        # 4. Health Benefits
        {
            "category": "HR & Policies",
            "subcategory": "Health & Benefits",
            "verbs": ["How do I submit a claim for", "What is the coverage limit for", "Where can I find policies for", "How to register for"],
            "nouns": ["dental cleaning and check-ups", "prescription drug costs", "vision exam and glasses", "mental health therapy", "physiotherapy sessions"],
            "contexts": ["under the corporate health plan", "for my family members", "during the {year} plan year", "for new hires in {location}"],
            "answer": "Health benefits claims for {noun_str} should be submitted through the Cigna Portal at cigna.company.com. Keep your itemized receipts. Claims are processed within 5-7 business days.",
            "keywords": ["health", "benefits", "insurance", "claim", "medical", "dental"],
            "tags": "#hr;#benefits;#insurance"
        },
        # 5. PTO & Leaves
        {
            "category": "HR & Policies",
            "subcategory": "PTO & Leaves",
            "verbs": ["How do I request time off for", "What is the policy for", "Steps to apply for a leave of absence for", "How to log sick leave for"],
            "nouns": ["medical treatment", "parental bonding time", "family emergency leave", "annual vacation days", "study and exam preparation"],
            "contexts": ["in the Workday system", "during {month}", "for {year}", "as a full-time employee in {location}"],
            "answer": "Time off or leave of absence for {noun_str} must be entered in Workday under 'Time Off'. Ensure your manager is notified, and submit medical or legal certificates if required by HR policy.",
            "keywords": ["pto", "leave", "vacation", "sick", "workday", "timeoff"],
            "tags": "#hr;#pto;#leave"
        },
        # 6. Payroll & Taxes
        {
            "category": "HR & Policies",
            "subcategory": "Payroll & Taxes",
            "verbs": ["Where can I download my", "How do I edit my", "Who do I contact about my", "Why does my payslip show a deduction for"],
            "nouns": ["W-2 tax form", "direct deposit bank details", "voluntary retirement contributions", "health savings account (HSA) deduction"],
            "contexts": ["in Workday", "for the tax year {year}", "before the next pay cycle", "in the {location} division"],
            "answer": "Payroll and tax documents, including {noun_str}, are managed securely via Workday under the 'Pay' app. Update details before the 15th of the month to apply to the current pay run.",
            "keywords": ["payroll", "tax", "payslip", "w2", "directdeposit", "salary"],
            "tags": "#hr;#payroll;#taxes"
        },
        # 7. Expense Filing
        {
            "category": "Finance & Expenses",
            "subcategory": "Expense Filing",
            "verbs": ["How do I file an expense report for", "How to claim reimbursement for", "Where to upload receipts for", "Steps to audit my expenses for"],
            "nouns": ["business travel flights", "client entertainment and dining", "home office equipment", "annual software subscriptions", "training courses and conferences"],
            "contexts": ["in SAP Concur", "for the {team} team", "in {month} {year}", "approved in the {location} office"],
            "answer": "Submit your claim for {noun_str} by logging into SAP Concur, creating a new report, attaching itemized receipts, and selecting your cost center. Reimbursements are processed weekly.",
            "keywords": ["expense", "concur", "receipt", "reimbursement", "audit", "finance"],
            "tags": "#finance;#expense;#concur"
        },
        # 8. Corporate Cards
        {
            "category": "Finance & Expenses",
            "subcategory": "Corporate Cards",
            "verbs": ["How do I apply for a", "Steps to activate my", "Who can help me block my", "How to increase the limit on my"],
            "nouns": ["corporate AMEX credit card", "procurement purchasing card", "travel and expense card", "department virtual credit card"],
            "contexts": ["for my role in {team}", "while traveling to {location}", "for {year} business operations"],
            "answer": "Corporate card services are managed through the Corporate Card Portal. Applications and limit increases for {noun_str} require manager and finance director approval.",
            "keywords": ["card", "amex", "credit", "limit", "corporate", "finance"],
            "tags": "#finance;#card;#amex"
        },
        # 9. Office Access
        {
            "category": "Facilities & Workspace",
            "subcategory": "Office Access",
            "verbs": ["How do I request a", "Where to replace a lost", "How to configure security access for a", "Steps to request access to the"],
            "nouns": ["building entry security badge", "parking garage access transponder", "datacenter secure access pass", "temporary visitor gate pass"],
            "contexts": ["for the {location} office", "starting in {month}", "valid through {year}", "requested by the {team} team"],
            "answer": "Security and badge access for {noun_str} is coordinated by the Facilities and Security Team. Visit the security desk or email badge.admin@company.com with manager authorization.",
            "keywords": ["badge", "access", "office", "security", "visitor", "parking"],
            "tags": "#facilities;#access;#security"
        },
        # 10. Conference Rooms
        {
            "category": "Facilities & Workspace",
            "subcategory": "Conference Rooms",
            "verbs": ["How do I book a", "Troubleshooting the AV screen in the", "What is the policy for reserving a", "Steps to schedule a"],
            "nouns": ["large boardroom", "collaborative meeting space", "team presentation room", "private focus room"],
            "contexts": ["in the {location} office", "via Outlook calendar", "for {month} team meetings", "for the {team} group"],
            "answer": "Conference rooms can be booked in Outlook by adding the room as a location. For AV issues with {noun_str}, tap the support button on the wall panel or contact av.support@company.com.",
            "keywords": ["room", "booking", "meeting", "outlook", "teams", "conference"],
            "tags": "#facilities;#meeting;#booking"
        }
    ]

    total_target = 4000
    random.seed(42)  # For deterministic generation

    # We will generate permutations systematically to get exactly 4000 records
    loop_limit = 20000
    current_loop = 0

    while len(records) < total_target and current_loop < loop_limit:
        current_loop += 1
        
        # Pick a generator config
        gen = random.choice(generators)
        
        # Select variables
        sys = random.choice(systems)
        dev = random.choice(devices)
        loc = random.choice(locations)
        team = random.choice(teams)
        month = random.choice(months)
        year = random.choice(years)

        # Build Noun
        noun_base = random.choice(gen["nouns"])
        noun_str = noun_base.format(system=sys, team=team)

        # Build Context
        context_base = random.choice(gen["contexts"])
        context_str = context_base.format(device=dev, location=loc, team=team, month=month, year=year)

        # Build Question
        verb_str = random.choice(gen["verbs"])
        question = f"{verb_str} {noun_str} {context_str}?"
        
        # Formatting answers
        answer = gen["answer"].format(
            noun_str=noun_str,
            device=dev,
            location=loc,
            team=team,
            month=month,
            year=year
        )

        if question.lower() in generated_questions:
            continue

        generated_questions.add(question.lower())

        # Select dates
        created = datetime.now() - timedelta(days=random.randint(30, 450))
        updated = created + timedelta(days=random.randint(0, 30)) if random.random() > 0.4 else created
        
        # Priority and Status distributions
        priority = random.choices(["High", "Medium", "Low"], weights=[0.2, 0.5, 0.3])[0]
        status = random.choices(["Published", "Draft", "Archived"], weights=[0.92, 0.05, 0.03])[0]

        # Combine keywords
        extra_kws = [sys.lower(), dev.lower(), loc.lower(), team.lower(), month.lower()]
        all_kws = gen["keywords"] + extra_kws
        random.shuffle(all_kws)
        keywords_str = ", ".join(list(dict.fromkeys(all_kws))[:6])

        records.append({
            "FAQID": str(uuid.uuid4()),
            "Question": question,
            "Answer": answer,
            "Category": gen["category"],
            "SubCategory": gen["subcategory"],
            "Keywords": keywords_str,
            "Tags": gen["tags"],
            "Priority": priority,
            "CreatedDate": created.strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedDate": updated.strftime("%Y-%m-%d %H:%M:%S"),
            "Status": status
        })

    # If we fall short due to seed/limit, write whatever we have up to 4000, or pad it
    print(f"Generated {len(records)} records.")

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "FAQID", "Question", "Answer", "Category", "SubCategory", 
            "Keywords", "Tags", "Priority", "CreatedDate", "UpdatedDate", "Status"
        ])
        writer.writeheader()
        writer.writerows(records[:4000])

    print(f"Dataset successfully written to {output_path}. Total records: {min(len(records), 4000)}")

if __name__ == "__main__":
    generate_faqs("/Users/raiyankhan/.gemini/antigravity/scratch/enterprise-faq-copilot/data/sample_faqs.csv")
