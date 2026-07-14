# Deployment & Configuration Guide: Enterprise FAQ Copilot

This document outlines the step-by-step process for deploying the **Enterprise FAQ Copilot** solution into a Microsoft Power Platform environment.

---

## 1. Prerequisites & Environment Setup

### Environment Requirements
- A Power Platform environment with a **Dataverse Database** enabled.
- **Power Apps Premium** or **Power Apps per-app** licenses for users accessing the Canvas app.
- **Microsoft Copilot Studio** license for virtual agent hosting.
- **Office 365 Outlook** and **Microsoft Teams** user accounts with permissions to send emails and post to channels.

### Security Role Assignments
Create or assign the following security roles in the Power Platform Admin Center:

1.  **FAQ Admin Role:**
    - Read, Write, Create, and Delete access on `cr_FAQ`, `cr_FAQCategory`, `cr_FAQFeedback`, and `cr_FAQChatLog`.
    - Access to run the bulk import flow.
2.  **FAQ User Role:**
    - Read access on `cr_FAQ` and `cr_FAQCategory`.
    - Write/Create access on `cr_FAQFeedback` and `cr_FAQChatLog`.

---

## 2. Importing the Solution Package

We package the schema, flows, canvas app, and virtual agents into a single Power Platform solution zip.

### Option A: Import via Power Apps Portal (Recommended)
1.  Log in to [make.powerapps.com](https://make.powerapps.com).
2.  Select your target environment in the top right corner (e.g., *Production* or *UAT*).
3.  Go to **Solutions** on the left navigation pane.
4.  Click **Import Solution** from the top ribbon.
5.  Browse and select the `EnterpriseFAQCopilotSolution_1_0_0_0.zip` file.
6.  Click **Next**. The portal will display solution metadata from [solution_manifest.xml](file:///Users/raiyankhan/.gemini/antigravity/scratch/enterprise-faq-copilot/deployment/solution_manifest.xml).
7.  **Establish Connection References:** The portal will prompt you to map connections for:
    - **Microsoft Dataverse Connection:** Select/create a Dataverse admin connection.
    - **Office 365 Outlook Connection:** Select/create an email sender connection.
    - **Microsoft Teams Connection:** Select/create a Teams poster connection.
    - **SharePoint Connection:** Select/create a SharePoint reader connection (used for bulk imports).
8.  Click **Import**. The process will take 2-5 minutes.

### Option B: Import via Power Platform CLI (PAC)
Ensure you are authenticated via PAC:
```bash
pac auth create --url https://yourorg.crm.dynamics.com
pac solution import --path ./deployment/EnterpriseFAQCopilotSolution_1_0_0_0.zip
```

---

## 3. Data Ingestion: Bulk Import 4,000 FAQs

To populate the database with the generated dataset in [sample_faqs.csv](file:///Users/raiyankhan/.gemini/antigravity/scratch/enterprise-faq-copilot/data/sample_faqs.csv):

### Method 1: Dataverse Excel/CSV Import Tool (Fastest)
1.  Go to **Dataverse > Tables** inside the solution.
2.  Open the **FAQ** (`cr_FAQ`) table.
3.  Click **Import > Import data from Excel** in the top ribbon.
4.  Upload the `sample_faqs.csv` file.
5.  **Map Columns:** Verify that the CSV columns map accurately to the Dataverse schema:
    - `FAQID` -> *FAQ (Primary Key)*
    - `Question` -> *Question*
    - `Answer` -> *Answer*
    - `Keywords` -> *Keywords*
    - `Tags` -> *Tags*
    - `Priority` -> *Priority (Map values High/Medium/Low)*
    - `Status` -> *Status (Map values Published/Draft/Archived)*
6.  Click **Import**. The import runs asynchronously in the cloud and takes about 1-2 minutes for 4,000 records.

### Method 2: SharePoint Ingestion Flow
1.  Upload the `sample_faqs.csv` file into the designated SharePoint library (configured in [ImportFAQsFlow.json](file:///Users/raiyankhan/.gemini/antigravity/scratch/enterprise-faq-copilot/power-automate/ImportFAQsFlow.json)).
2.  The `ImportFAQsFlow` triggers automatically, parses the rows, checks for category existence, creates categories if missing, and commits records to the `cr_FAQ` table.

---

## 4. Canvas App Configuration

1.  Open the **FAQ Portal App** in Edit mode inside the Power Apps Studio.
2.  Verify the Dataverse connections are healthy. The tables `cr_FAQs`, `cr_FAQCategories`, and `cr_FAQFeedbacks` should show in the Data pane.
3.  Publish the application: Click **Publish** > **Publish this version**.
4.  **Sharing:** Share the app with all enterprise user security groups. Ensure they are assigned the **FAQ User** security role so they have permission to access the Dataverse tables.

---

## 5. Copilot Studio Chatbot Configuration

1.  Go to **Copilot Studio** ([copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)).
2.  Open the newly imported **Enterprise FAQ Copilot** bot.
3.  **Topic Binding:** Ensure that the [SearchFAQTopic.yaml](file:///Users/raiyankhan/.gemini/antigravity/scratch/enterprise-faq-copilot/copilot-studio/SearchFAQTopic.yaml) and [FallbackTopic.yaml](file:///Users/raiyankhan/.gemini/antigravity/scratch/enterprise-faq-copilot/copilot-studio/FallbackTopic.yaml) topics are active.
4.  **Generative Answers Configuration (Optional for supplementary AI-driven fallback):**
    - Go to **Conversational Boosting** topic.
    - Set the Data source to query the Dataverse table `cr_FAQ` directly, selecting `cr_question` and `cr_answer` as search targets.
5.  Click **Publish** in Copilot Studio.
6.  **Deploy Bot Channels:** Add the bot to your enterprise channels (e.g., Microsoft Teams, SharePoint Intranet portal, or embed in the Power Apps Canvas App directly).

---

## 6. ALM & Release Best Practices

- **Always Export as Managed:** In your Development sandbox, keep the solution **Unmanaged**. When deploying to UAT or Production, export the solution as **Managed** to block direct edits in production and ensure clean uninstall/update paths.
- **Connection References:** Configure Connection References in the target environment post-import. Do not hardcode connection settings inside Power Automate or Power Apps.
