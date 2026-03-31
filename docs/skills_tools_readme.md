# Marketing Skills & Tool Integrations Reference

Comprehensive review of the [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) skill and integration library — 29 skills and 58 tool integrations covering the full marketing stack.

---

## Table of Contents

- [Skills Overview](#skills-overview)
  - [Content Creation](#1-content-creation-5-skills)
  - [Strategy & Planning](#2-strategy--planning-6-skills)
  - [CRO](#3-cro--conversion-rate-optimization-7-skills)
  - [SEO](#4-seo-5-skills)
  - [Ads & Testing](#5-ads--testing-3-skills)
  - [Product Context & Free Tools](#6-product-context--free-tools-2-skills)
  - [Skill Cross-References](#skill-cross-references)
- [Tool Integrations Overview](#tool-integrations-overview)
  - [Email & Messaging](#a-email--messaging-12-integrations)
  - [Analytics & Data](#b-analytics--data-10-integrations)
  - [SEO Tools](#c-seo-tools-4-integrations)
  - [Advertising Platforms](#d-advertising-platforms-4-integrations)
  - [CRM & Sales](#e-crm--sales-4-integrations)
  - [Outreach & Prospecting](#f-outreach--prospecting-5-integrations)
  - [Billing & Payments](#g-billing--payments-3-integrations)
  - [Referral & Affiliate](#h-referral--affiliate-4-integrations)
  - [Scheduling & Events](#i-scheduling--events-4-integrations)
  - [A/B Testing](#j-ab-testing--experimentation-1-integration)
  - [Social Media](#k-social-media-management-1-integration)
  - [Website & CMS](#l-website--cms-2-integrations)
  - [Forms, Surveys & Reviews](#m-forms-surveys--reviews-2-integrations)
  - [Video & Media](#n-video--media-1-integration)
  - [Automation](#o-automation-1-integration)
- [Skill-to-Integration Mapping](#skill-to-integration-mapping)
- [Summary Matrix](#summary-matrix)

---

## Skills Overview

Each skill lives under `/skills/{name}/SKILL.md` with optional `references/` supplementary files. All skills share a common pattern:

- YAML frontmatter (name, description, version)
- Role-play persona prompt for the LLM
- Initial assessment that checks for `.claude/product-marketing-context.md`
- Core principles, frameworks, and structured output templates

### 1. Content Creation (5 skills)

| Skill | Purpose | Core Approach | References |
|-------|---------|---------------|------------|
| **copywriting** | Write or improve marketing copy — homepages, landing pages, pricing, feature pages, about pages | Clarity over cleverness, benefits over features, specificity over vagueness, customer language over company language | `copy-frameworks.md`, `natural-transitions.md` |
| **copy-editing** | Systematic review of existing copy via multiple focused passes | "Seven Sweeps Framework" — seven sequential passes: Clarity, Voice & Tone, Persuasion, Structure, Readability, Specificity, Polish. Each sweep loops back to verify previous sweeps | `plain-english-alternatives.md` |
| **social-content** | Create and optimize social media content for LinkedIn, X, Instagram, TikTok, Facebook | Content Pillars Framework (3-5 pillars), platform-specific strategies, hook formulas, content repurposing across formats | `platforms.md`, `post-templates.md`, `reverse-engineering.md` |
| **cold-email** | Write B2B cold emails and follow-up sequences that get replies | Write like a peer not a vendor, every sentence earns its place, personalisation connects to the problem, one ask low friction | `benchmarks.md`, `follow-up-sequences.md`, `frameworks.md`, `personalization.md`, `subject-lines.md` |
| **email-sequence** | Create or optimise email sequences — drip campaigns, automated flows, lifecycle programs | One email one job, value before ask, relevance over volume, clear path forward. Covers strategy, timing, copy guidelines per email type | `copy-guidelines.md`, `email-types.md`, `sequence-templates.md` |

### 2. Strategy & Planning (6 skills)

| Skill | Purpose | Core Approach | References |
|-------|---------|---------------|------------|
| **content-strategy** | Plan what content to create — topic clusters, editorial calendars, content mapping | Every piece must be "searchable, shareable, or both." Covers use-case content, comparison content, glossary marketing, topic clusters. Search traffic is the foundation | — |
| **launch-strategy** | Plan product launches, feature announcements, release strategies | "ORB Framework" — Owned, Rented, Borrowed channels. Phased launches (alpha → beta → public). Includes Product Hunt playbook and ongoing launch momentum | — |
| **pricing-strategy** | Pricing decisions, packaging, monetisation strategy for SaaS | Three pricing axes (packaging, pricing metric, price point), value-based pricing. Van Westendorp research method, value metrics, tier structure design | `research-methods.md`, `tier-structure.md` |
| **referral-program** | Create or optimise referral/affiliate programs and word-of-mouth strategies | Referral Loop (Trigger → Share → Convert → Reward → Loop), dual-sided incentives, trigger moment identification. Covers both customer referral and affiliate | `affiliate-programs.md`, `program-examples.md` |
| **marketing-ideas** | Library of 139 proven marketing approaches, filtered by stage and budget | Categorised ideas across Content & SEO, Competitor, Free Tools, Paid Ads, Social, Email, Partnerships, Events, PR, Launches, Product-Led, Unconventional, Platforms, International, Developer, Audience-Specific | `ideas-by-category.md` |
| **marketing-psychology** | Apply 70+ psychological principles and behavioural science to marketing | Foundational models (First Principles, JTBD, Pareto, Inversion), persuasion models (Scarcity, Social Proof, Anchoring), decision-making models, growth models. Each with marketing application examples | — |

### 3. CRO — Conversion Rate Optimization (7 skills)

| Skill | Purpose | Core Approach | References |
|-------|---------|---------------|------------|
| **page-cro** | Optimise any marketing page — homepage, landing, pricing, feature, blog | Priority order: Value Prop Clarity → Headline Effectiveness → CTA Placement/Copy/Hierarchy → Visual Hierarchy/Scannability → Trust Signals/Social Proof | `experiments.md` |
| **signup-flow-cro** | Optimise signup, registration, account creation, trial activation flows | Minimise required fields, show value before asking for commitment, reduce perceived effort, remove uncertainty. Field-by-field optimisation (email, password, name, etc.) | — |
| **onboarding-cro** | Optimise post-signup onboarding, user activation, first-run experience | Time-to-value is everything, one goal per session, do don't show, progress creates motivation. Covers checklist patterns, empty states, progressive disclosure | `experiments.md` |
| **form-cro** | Optimise non-signup forms — lead capture, contact, demo request, application, survey, checkout | Every field has a cost (3 fields baseline, 7+ = 25-50% reduction), value must exceed effort, reduce cognitive load | — |
| **popup-cro** | Create or optimise popups, modals, overlays, slide-ins, banners | Timing is everything, value must be obvious, respect the user. Trigger strategies: time-based, scroll-based, exit intent, click-triggered | — |
| **paywall-upgrade-cro** | Create or optimise in-app paywalls, upgrade screens, upsell modals, feature gates | Value before ask, show don't just tell, friction-free path, respect the no. Covers feature gates, usage limits, trial expiration, time-based prompts | `experiments.md` |
| **churn-prevention** | Reduce churn — cancellation flows, save offers, failed payment recovery, retention strategies | Voluntary churn (cancel flows, save offers, exit surveys) + involuntary churn (dunning, payment recovery, smart retries). Cancel flow: Trigger → Survey → Dynamic Offer → Confirmation → Post-Cancel | `cancel-flow-patterns.md`, `dunning-playbook.md` |

### 4. SEO (5 skills)

| Skill | Purpose | Core Approach | References |
|-------|---------|---------------|------------|
| **seo-audit** | Audit, review, or diagnose SEO issues on a site | Priority: Crawlability & Indexation → Technical Foundations → On-Page Optimisation → Content Quality → Authority & Links. Caveat about schema detection limitations with web_fetch/curl | `ai-writing-detection.md` |
| **ai-seo** | Optimise for AI search engines — Google AI Overviews, ChatGPT, Perplexity, Claude, Gemini (AEO/GEO/LLMO) | Traditional SEO = ranked; AI SEO = cited. Platform-by-platform ranking factors, AI Visibility Audit methodology, content optimisation patterns | `content-patterns.md`, `platform-ranking-factors.md` |
| **programmatic-seo** | Create SEO-driven pages at scale using templates and data | Unique value per page, proprietary data wins, clean URL structure, genuine search intent match. 12 playbooks: Templates, Curation, Conversions, Comparisons, Examples, Locations, Personas, etc. | `playbooks.md` |
| **schema-markup** | Add, fix, or optimise JSON-LD structured data | Accuracy first, use JSON-LD, follow Google's guidelines, validate everything. Covers Organization, WebSite, Article, Product, SoftwareApplication, FAQPage, HowTo, BreadcrumbList, LocalBusiness, Event | `schema-examples.md` |
| **competitor-alternatives** | Create competitor comparison and "alternatives to" pages | Honesty builds trust, depth over surface, help them decide. Four formats: [Competitor] Alternative (singular), [Product] Alternatives (plural), You vs Competitor, Competitor vs Competitor | `content-architecture.md`, `templates.md` |

### 5. Ads & Testing (3 skills)

| Skill | Purpose | Core Approach | References |
|-------|---------|---------------|------------|
| **paid-ads** | Campaign strategy for Google Ads, Meta, LinkedIn, X, TikTok | Platform selection guide (Google = high-intent, Meta = demand gen, LinkedIn = B2B), campaign structure best practices, naming conventions, optimisation frameworks | `ad-copy-templates.md`, `audience-targeting.md`, `platform-setup-checklists.md` |
| **ad-creative** | Generate, iterate, and scale ad creative — headlines, descriptions, primary text | Two modes: Generate from Scratch, or Iterate from Performance Data. Enforces platform character limits (Google RSA: 30ch headlines / 90ch desc; Meta primary: 125ch) | `generative-tools.md`, `platform-specs.md` |
| **ab-test-setup** | Plan, design, and implement A/B tests and experiments | Hypothesis framework: "Because X, we believe Y will cause Z for audience A. We'll know when metric M." Test types: A/B, A/B/n, MVT, Split URL. Sample size calculation | `sample-size-guide.md`, `test-templates.md` |

### 6. Product Context & Free Tools (2 skills)

| Skill | Purpose | Core Approach | References |
|-------|---------|---------------|------------|
| **product-marketing-context** | Create/maintain the shared `.claude/product-marketing-context.md` all other skills reference | Two modes: Auto-draft from codebase (reads README, landing pages, etc.) or Start from Scratch (conversational walkthrough). Covers product overview, target audience, personas, pain points, positioning, brand voice, competitive landscape | — |
| **free-tool-strategy** | Plan or build free tools for marketing (engineering as marketing) — lead gen, SEO, brand | Solve a real problem, adjacent to core product, simple and focused, worth the investment. Tool types: Calculators, Generators, Analyzers, Testers, Libraries, Interactive | `tool-types.md` |

### Skill Cross-References

Skills explicitly hand off to each other:

```
product-marketing-context ──→ ALL SKILLS (foundational context)

copywriting ──→ copy-editing (line-by-line review after drafting)
copywriting ──→ email-sequence (for email copy)
copywriting ──→ popup-cro (for popup copy)
email-sequence ──→ onboarding-cro (for in-app flows)
page-cro ──→ signup-flow-cro, onboarding-cro, form-cro, popup-cro
ab-test-setup ──→ analytics-tracking (for measurement)
paid-ads ──→ ad-creative (for creative generation)
seo-audit ──→ programmatic-seo, schema-markup
ai-seo ──→ seo-audit, schema-markup
churn-prevention ──→ email-sequence (win-back), paywall-upgrade-cro (upsells)
competitor-alternatives ──→ programmatic-seo (page templates at scale)
```

---

## Tool Integrations Overview

Each integration lives under `/tools/integrations/{name}.md` with a consistent structure: tool description, capabilities table (API / MCP / CLI / SDK availability), authentication details, and common API call examples for agent use.

### A. Email & Messaging (12 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **ActiveCampaign** | Email marketing automation + CRM + deals pipeline | API Token | Y | — |
| **Brevo** (Sendinblue) | All-in-one email, SMS, WhatsApp marketing | API Key | Y | — |
| **Customer.io** | Behaviour-based email, push, SMS, in-app messaging | Basic Auth (site_id:api_key) | — | — |
| **Kit** (ConvertKit) | Email marketing for creators/newsletters | API Key/Secret | — | — |
| **Klaviyo** | E-commerce email and SMS marketing | Private API Key (pk_) | Y | — |
| **Mailchimp** | Email campaigns, automation, audience management | API Key / OAuth 2.0 | — | Y |
| **OneSignal** | Push notifications, email, SMS, in-app messaging | REST API Key (Basic Auth) | Y | — |
| **Postmark** | Transactional email delivery | Server Token | Y | — |
| **Resend** | Developer-friendly transactional email | API Key | — | Y |
| **SendGrid** | Email delivery (transactional + marketing) | API Key | — | — |
| **Beehiiv** | Newsletter platform + referral programs | Bearer Token | Y | — |
| **Intercom** | Customer messaging and support platform | Bearer Token | Y | — |

### B. Analytics & Data (10 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Google Analytics 4** | Web analytics — behaviour, conversions | OAuth 2.0 / Service Account | — | Y |
| **Adobe Analytics** | Enterprise cross-channel analytics | OAuth 2.0 (JWT) | — | — |
| **Amplitude** | Product analytics — behaviour, retention, experimentation | API Key + Secret | — | — |
| **Mixpanel** | Product analytics — user behaviour, retention | Project Token / Service Account | — | — |
| **PostHog** | Open-source product analytics + session replay + feature flags | API Key | Y | — |
| **Hotjar** | Heatmaps, session recordings, surveys | OAuth 2.0 Client Credentials | Y | — |
| **Plausible** | Privacy-focused web analytics (no cookies) | Bearer Token | Y | — |
| **Segment** | Customer data platform — collect, route, activate | Write Key / OAuth 2.0 | — | — |
| **Google Search Console** | Search performance and indexing monitoring | OAuth 2.0 / Service Account | — | — |
| **Clearbit** (HubSpot Breeze) | Company/person data enrichment (100+ attributes) | Bearer Token | Y | — |

### C. SEO Tools (4 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Ahrefs** | Backlink analysis, keyword research, competitive research | Bearer Token | — | — |
| **SEMrush** | SEO + competitive analysis, keyword research, site audits | API Key (query param) | — | — |
| **DataForSEO** | SERP results, keyword research, backlinks, on-page analysis | Basic Auth | Y | — |
| **Keywords Everywhere** | Search volume, CPC, competition, related keywords | Bearer Token | Y | — |

### D. Advertising Platforms (4 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Google Ads** | PPC campaigns (search, display, video) | OAuth 2.0 | — | Y |
| **Meta Ads** | Facebook/Instagram advertising | OAuth 2.0 Access Token | — | — |
| **LinkedIn Ads** | B2B advertising with professional targeting | OAuth 2.0 | — | — |
| **TikTok Ads** | Short-form video advertising | Access Token | — | — |

### E. CRM & Sales (4 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **HubSpot** | CRM for marketing, sales, service | Private App Token / OAuth 2.0 | Y | — |
| **Salesforce** | Enterprise CRM | OAuth 2.0 (JWT Bearer) | Y | — |
| **Apollo.io** | B2B prospecting + data enrichment (210M+ contacts) | API Key | Y | — |
| **G2** | Software review platform, buyer intent signals | API Token (JSON:API) | Y | — |

### F. Outreach & Prospecting (5 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Hunter.io** | Email finding and verification | API Key (query param) | Y | — |
| **Instantly.ai** | Cold email platform with warmup + campaign management | API Key | Y | — |
| **Lemlist** | Cold email outreach with personalisation | Basic Auth | Y | — |
| **Snov.io** | Email finding, verification, drip campaigns | OAuth2 client credentials | Y | — |
| **Dub.co** | Link management and attribution | API Key | — | — |

### G. Billing & Payments (3 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Stripe** | Payment processing, subscriptions, billing | API Key (sk_live/sk_test) | Y | Y |
| **Paddle** | SaaS billing, merchant of record + tax compliance | Bearer Token | Y | — |
| **Shopify** | E-commerce platform | Access Token | Y | — |

### H. Referral & Affiliate (4 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Rewardful** | Affiliate/referral tracking for Stripe-based SaaS | API Secret | — | — |
| **Tolt** | Affiliate program management (Stripe/Paddle) | API Key | — | — |
| **PartnerStack** | Partner/affiliate program management for SaaS | Basic Auth (public:secret) | Y | — |
| **Mention Me** | Enterprise referral marketing | Bearer Token | — | — |

### I. Scheduling & Events (4 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Calendly** | Scheduling and booking | Bearer Token / OAuth 2.0 | Y | — |
| **SavvyCal** | Scheduling links and availability | Bearer Token | Y | — |
| **Demio** | Webinar platform (live, automated, on-demand) | API Key + Secret | Y | — |
| **Livestorm** | Video engagement (webinars, virtual events) | API Token (JSON:API) | Y | — |

### J. A/B Testing & Experimentation (1 integration)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Optimizely** | A/B testing and experimentation platform | Bearer Token | Y | — |

### K. Social Media Management (1 integration)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Buffer** | Social media scheduling, publishing, analytics | OAuth 2.0 Bearer Token | Y | — |

### L. Website & CMS (2 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Webflow** | Visual web design and CMS | API Token | Y | — |
| **WordPress** | Content management system | Basic Auth (App Password) | Y | — |

### M. Forms, Surveys & Reviews (2 integrations)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Typeform** | Forms and surveys | Bearer Token | Y | — |
| **Trustpilot** | Business review management | API Key + OAuth 2.0 | Y | — |

### N. Video & Media (1 integration)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Wistia** | Video hosting, management, analytics | Bearer Token | Y | — |

### O. Automation (1 integration)

| Tool | Purpose | Auth | CLI | MCP |
|------|---------|------|:---:|:---:|
| **Zapier** | Workflow automation connecting apps | API Key | — | Y |

---

## Skill-to-Integration Mapping

Which integrations power which skills — the core relationship table.

| Skill | Primary Integrations | Secondary / Optional |
|-------|---------------------|----------------------|
| **copywriting** | — (LLM only) | — |
| **copy-editing** | — (LLM only) | — |
| **social-content** | Buffer | — |
| **cold-email** | Hunter, Instantly, Lemlist, Snov, Apollo | Clearbit (enrichment) |
| **email-sequence** | ActiveCampaign, Brevo, Customer.io, Kit, Klaviyo, Mailchimp, Resend, SendGrid | Beehiiv (newsletters), Intercom (in-app) |
| **content-strategy** | — (LLM only) | Ahrefs, SEMrush (keyword data) |
| **launch-strategy** | Calendly, SavvyCal (scheduling), Demio, Livestorm (webinars) | Buffer (social), Beehiiv (newsletter) |
| **pricing-strategy** | Stripe, Paddle | — |
| **referral-program** | Rewardful, Tolt, PartnerStack, Mention Me | Stripe, Paddle (billing hooks) |
| **marketing-ideas** | — (LLM only) | — |
| **marketing-psychology** | — (LLM only) | — |
| **page-cro** | Hotjar (heatmaps), Webflow/WordPress (CMS) | Optimizely (testing) |
| **signup-flow-cro** | Hotjar, Typeform | Optimizely |
| **onboarding-cro** | Intercom (in-app guides), OneSignal (push) | Amplitude, Mixpanel (activation analytics) |
| **form-cro** | Typeform, Hotjar | — |
| **popup-cro** | Optimizely (testing) | — |
| **paywall-upgrade-cro** | Stripe, Paddle (billing) | Amplitude (usage tracking) |
| **churn-prevention** | Stripe, Paddle (dunning), ActiveCampaign/Mailchimp (win-back) | Intercom (in-app retention) |
| **free-tool-strategy** | — (LLM only) | Webflow/WordPress (hosting) |
| **seo-audit** | Ahrefs, SEMrush, DataForSEO, Google Search Console | — |
| **ai-seo** | Ahrefs, SEMrush (tracking) | — |
| **programmatic-seo** | DataForSEO, Keywords Everywhere | Webflow/WordPress (CMS) |
| **schema-markup** | Google Search Console (validation) | — |
| **competitor-alternatives** | Ahrefs, SEMrush (competitor data), G2 (reviews) | — |
| **paid-ads** | Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads | — |
| **ad-creative** | Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads | — |
| **ab-test-setup** | Optimizely, GA4 | PostHog (feature flags) |
| **analytics-tracking** | GA4, Adobe Analytics, Amplitude, Mixpanel, PostHog, Plausible, Segment | Hotjar (qualitative) |
| **product-marketing-context** | — (local file only) | — |

---

## Summary Matrix

Integration capability at a glance — 6 have MCP support, 31 have CLI access.

```
                              MCP    CLI    Skills that use it
                              ───    ───    ──────────────────
EMAIL & MESSAGING
  ActiveCampaign               -      Y     email-sequence, churn-prevention
  Brevo                        -      Y     email-sequence
  Customer.io                  -      -     email-sequence
  Kit (ConvertKit)             -      -     email-sequence
  Klaviyo                      -      Y     email-sequence
  Mailchimp                    Y      -     email-sequence, churn-prevention
  OneSignal                    -      Y     onboarding-cro
  Postmark                     -      Y     email-sequence
  Resend                       Y      -     email-sequence
  SendGrid                     -      -     email-sequence
  Beehiiv                      -      Y     email-sequence, launch-strategy
  Intercom                     -      Y     onboarding-cro, churn-prevention

ANALYTICS & DATA
  Google Analytics 4           Y      -     analytics-tracking, ab-test-setup
  Adobe Analytics              -      -     analytics-tracking
  Amplitude                    -      -     analytics-tracking, onboarding-cro
  Mixpanel                     -      -     analytics-tracking
  PostHog                      -      Y     analytics-tracking, ab-test-setup
  Hotjar                       -      Y     page-cro, signup-flow-cro, form-cro
  Plausible                    -      Y     analytics-tracking
  Segment                      -      -     analytics-tracking
  Google Search Console        -      -     seo-audit, schema-markup
  Clearbit                     -      Y     cold-email

SEO TOOLS
  Ahrefs                       -      -     seo-audit, ai-seo, competitor-alts
  SEMrush                      -      -     seo-audit, ai-seo, competitor-alts
  DataForSEO                   -      Y     seo-audit, programmatic-seo
  Keywords Everywhere          -      Y     programmatic-seo

ADVERTISING
  Google Ads                   Y      -     paid-ads, ad-creative
  Meta Ads                     -      -     paid-ads, ad-creative
  LinkedIn Ads                 -      -     paid-ads, ad-creative
  TikTok Ads                   -      -     paid-ads, ad-creative

CRM & SALES
  HubSpot                      -      Y     (CRM workflows)
  Salesforce                   -      Y     (CRM workflows)
  Apollo.io                    -      Y     cold-email
  G2                           -      Y     competitor-alternatives

OUTREACH
  Hunter.io                    -      Y     cold-email
  Instantly.ai                 -      Y     cold-email
  Lemlist                      -      Y     cold-email
  Snov.io                      -      Y     cold-email
  Dub.co                       -      -     (link tracking)

BILLING
  Stripe                       Y      Y     pricing, paywall, churn, referral
  Paddle                       -      Y     pricing, paywall, churn, referral
  Shopify                      -      Y     (e-commerce)

REFERRAL
  Rewardful                    -      -     referral-program
  Tolt                         -      -     referral-program
  PartnerStack                 -      Y     referral-program
  Mention Me                   -      -     referral-program

SCHEDULING & EVENTS
  Calendly                     -      Y     launch-strategy
  SavvyCal                     -      Y     launch-strategy
  Demio                        -      Y     launch-strategy
  Livestorm                    -      Y     launch-strategy

A/B TESTING
  Optimizely                   -      Y     ab-test-setup, page-cro, popup-cro

SOCIAL
  Buffer                       -      Y     social-content

CMS
  Webflow                      -      Y     page-cro, programmatic-seo
  WordPress                    -      Y     page-cro, programmatic-seo

FORMS & REVIEWS
  Typeform                     -      Y     signup-flow-cro, form-cro
  Trustpilot                   -      Y     (reviews/social proof)

VIDEO
  Wistia                       -      Y     (video marketing)

AUTOMATION
  Zapier                       Y      -     (workflow glue)
```

### Key Patterns

1. **Context-first design** — Every skill checks for `product-marketing-context` first. That skill is the foundational entry point.

2. **Full-funnel coverage** — Awareness (content-strategy, social, SEO, paid-ads) → Consideration (competitor pages, pricing) → Conversion (CRO skills, signup, onboarding) → Retention (churn-prevention, email-sequence).

3. **CRO is deeply specialised** — Split into 7 distinct skills (page, signup, onboarding, form, popup, paywall, churn) with clear "use this when" boundaries and cross-references.

4. **Integrations as API reference cards** — Each integration file provides exact curl/API examples ready for agent use, not code libraries.

5. **MCP-enabled integrations** (6 total): GA4, Google Ads, Mailchimp, Resend, Stripe, Zapier — these can be used as Claude MCP tool servers.

6. **CLI-enabled integrations** (31 total): The majority support CLI access, making them scriptable from agent workflows.

7. **LLM-only skills** — copywriting, copy-editing, content-strategy, marketing-ideas, marketing-psychology, product-marketing-context, and free-tool-strategy need no external integrations — they run purely on LLM reasoning with context.
