# Power Fx Formulas Reference: Enterprise FAQ Copilot

This document provides a comprehensive guide to the Power Fx formulas implemented in the Canvas Power App. It highlights the design patterns, delegation-safe querying strategies for datasets exceeding the 2,000-record threshold, and state management techniques.

---

## 1. Startup & Theme Initialization (`App.OnStart`)

This formula initializes the application's global state, premium color theme tokens, styles, caches, and checks administrative permissions.

```powerfx
// 1. Initialize Design System Color Palette (Slate/Blue Theme)
Set(gblTheme, {
    Primary: ColorValue("#0F172A"),       // Slate 900 (Deep/Premium Dark)
    PrimaryLight: ColorValue("#1E293B"),  // Slate 800
    Accent: ColorValue("#3B82F6"),        // Blue 500
    AccentHover: ColorValue("#2563EB"),   // Blue 600
    Background: ColorValue("#F8FAFC"),    // Slate 50
    CardBg: ColorValue("#FFFFFF"),        // Pure White
    BorderColor: ColorValue("#E2E8F0"),   // Slate 200
    TextDark: ColorValue("#0F172A"),      // Slate 900
    TextMuted: ColorValue("#64748B"),     // Slate 500
    Success: ColorValue("#10B981"),       // Emerald 500
    Error: ColorValue("#EF4444"),         // Red 500
    Warning: ColorValue("#F59E0B"),       // Amber 500
    GrayBg: ColorValue("#F1F5F9")         // Slate 100
});

// 2. Initialize Typography Style
Set(gblFont, {
    Family: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    SizeTitle: 24,
    SizeHeader: 18,
    SizeBody: 14,
    SizeSmall: 12
});

// 3. Load Local Favorites and Recent Searches from Device Cache (SSO Sandbox)
Clear(colFavorites);
LoadData(colFavorites, "EnterpriseFAQFavorites", true);

Clear(colRecentSearches);
LoadData(colRecentSearches, "EnterpriseFAQRecentSearches", true);

// 4. Initialize User Profile Settings
Set(gblCurrentUser, User());

// 5. Evaluate Administrative Role (Production uses Azure AD Security Groups check)
Set(gblIsAdmin, gblCurrentUser.Email = "admin@company.com" || EndingWith(gblCurrentUser.Email, "@company.com"));

// 6. Navigation Stack for Back button tracking
ClearCollect(colNavStack, { Screen: "UserPortalScreen" });
```

---

## 2. Delegation-Safe Searching & Filtering (`UserPortalScreen`)

### Main Gallery Search Formula (`FAQGallery.Items`)
> [!IMPORTANT]
> **Dataverse Delegation:** 
> Standard delegation limits are 500 (can be raised to 2,000 in app settings). However, with 4,000 records, client-side queries will truncate the data.
> - **Delegable:** The `Search()` function is delegable to Dataverse for Text columns.
> - **Delegable:** The `Filter()` function is delegable for OptionSets, Lookups, and Date ranges.
> - **Non-Delegable:** The `in` operator (substring match) is **not** delegable.
>
> We nest `Filter` inside `Search` to filter by active status and category, then search globally by question, keywords, or tags.

```powerfx
Search(
    Filter(
        cr_FAQs, 
        cr_status = 'cr_faq_status (cr_FAQ)'.Published && 
        (IsBlank(locSelectedCategory) || cr_categoryid.cr_faqcategoryid = locSelectedCategory.cr_faqcategoryid)
    ),
    SearchBox.Text,
    "cr_question", 
    "cr_keywords", 
    "cr_tags"
)
```

### Prepending "All Category" to Dropdowns/Galleries (`CategoryGallery.Items`)
We create a dummy "All" record and join it with the actual Dataverse Category table using the `Table()` and `Collection` syntax:

```powerfx
Table({cr_faqcategoryid: Blank(), cr_name: "All Category"}) As _all_
Collection 
cr_FAQCategories
```

---

## 3. Local Caching & State Management

### Bookmarking / Favorites Toggle (`FAQDetailsScreen.FavoriteToggleBtn.OnSelect`)
This provides zero-latency offline favorites storage using a local device cache:

```powerfx
If(
    !IsBlank(LookUp(colFavorites, cr_faqid = gblSelectedFAQ.cr_faqid)),
    // Remove from local collection
    Remove(colFavorites, LookUp(colFavorites, cr_faqid = gblSelectedFAQ.cr_faqid)),
    // Add record to local collection
    Collect(colFavorites, gblSelectedFAQ)
);
// Save collection directly to physical storage
SaveData(colFavorites, "EnterpriseFAQFavorites")
```

### Logging Recent Queries (`UserPortalScreen.SearchBox.OnSelect`)
Adds unique entries to the top of the search stack and caps history at 10:

```powerfx
If(
    !IsBlank(Self.Text), 
    // Delete existing duplicate if present
    Remove(colRecentSearches, First(Filter(colRecentSearches, Query = Self.Text)));
    // Insert new query at index 1
    Insert(colRecentSearches, 1, { Query: Self.Text, Timestamp: Now() });
    // Truncate to top 10
    If(CountRows(colRecentSearches) > 10, Remove(colRecentSearches, Last(colRecentSearches)));
    // Save cache
    SaveData(colRecentSearches, "EnterpriseFAQRecentSearches")
)
```

---

## 4. User Interaction & Feedback Submission (`FAQDetailsScreen`)

Feedback is written directly to the `cr_FAQFeedback` entity in Dataverse. 

### Positive Rating Submission (`YesFeedbackBtn.OnSelect`)
```powerfx
UpdateContext({locFeedbackRating: true});
UpdateContext({locFeedbackSubmitted: true});

Patch(
    cr_FAQFeedbacks, 
    Defaults(cr_FAQFeedbacks), 
    {
        cr_faqid: gblSelectedFAQ,
        cr_ishelpful: true,
        cr_useremail: gblCurrentUser.Email,
        cr_comments: "User marked as helpful"
    }
);
Notify("Thank you for your feedback!", NotificationType.Success)
```

### Negative Rating Submission (`SubmitNegativeFeedbackBtn.OnSelect`)
```powerfx
UpdateContext({locFeedbackSubmitted: true});

Patch(
    cr_FAQFeedbacks, 
    Defaults(cr_FAQFeedbacks), 
    {
        cr_faqid: gblSelectedFAQ,
        cr_ishelpful: false,
        cr_useremail: gblCurrentUser.Email,
        cr_comments: CommentTextBox.Text
    }
);

// Triggers Power Automate notification flow for unanswered/low quality questions
If(
    !IsBlank(CommentTextBox.Text),
    NotifyAdminFlow.Run(gblSelectedFAQ.cr_question, CommentTextBox.Text, gblCurrentUser.Email)
);

Notify("Feedback submitted.", NotificationType.Success)
```

---

## 5. Administrative CRUD Operations (`AdminDashboardScreen`)

Admins require robust validation and transaction handlers.

### Save / Update Action (`SaveFAQBtn.OnSelect`)
We use a conditional `Patch` statement. If in "New Mode", we create a default record; otherwise, we write updates to the selected record.

```powerfx
If(
    locIsNewMode,
    // Insert New Record
    Set(locNewRecord, Patch(
        cr_FAQs, 
        Defaults(cr_FAQs), 
        {
            cr_question: Trim(AdminQuestionInput.Text),
            cr_answer: AdminAnswerInput.HtmlText,
            cr_categoryid: AdminCategoryDropdown.Selected,
            cr_keywords: Trim(AdminKeywordsInput.Text),
            cr_tags: Trim(AdminTagsInput.Text),
            cr_priority: AdminPriorityDropdown.Selected.Value,
            cr_status: AdminStatusDropdown.Selected.Value
        }
    ));
    UpdateContext({locSelectedAdminFAQ: locNewRecord});
    UpdateContext({locIsNewMode: false});
    Notify("New FAQ successfully created!", NotificationType.Success),
    
    // Update Existing Record
    Patch(
        cr_FAQs, 
        locSelectedAdminFAQ, 
        {
            cr_question: Trim(AdminQuestionInput.Text),
            cr_answer: AdminAnswerInput.HtmlText,
            cr_categoryid: AdminCategoryDropdown.Selected,
            cr_keywords: Trim(AdminKeywordsInput.Text),
            cr_tags: Trim(AdminTagsInput.Text),
            cr_priority: AdminPriorityDropdown.Selected.Value,
            cr_status: AdminStatusDropdown.Selected.Value
        }
    );
    Notify("FAQ successfully updated!", NotificationType.Success)
)
```

### Delete FAQ Action (`DeleteFAQBtn.OnSelect`)
```powerfx
Remove(cr_FAQs, locSelectedAdminFAQ);
UpdateContext({locSelectedAdminFAQ: First(cr_FAQs)});
Notify("FAQ record deleted.", NotificationType.Warning)
```
