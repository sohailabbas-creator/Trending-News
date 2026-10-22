# 90-Day SEO Plan — sohailabbas.site

This plan assumes the site is deployed, `SITE_URL` is set to `https://sohailabbas.site`, and Google
Search Console is verified. It is written as a schedule of work, not a promise. **No ranking,
traffic, revenue or advertising-approval outcome is guaranteed anywhere in this document.**

Two ground rules that shape everything below:

1. **Nothing is published to chase a keyword.** Every tool page already exists because the tool
   does something useful. New content must add something a user cannot get from the current page.
2. **Metrics are what the data says.** Where this plan says "expect", it means "a plausible range
   if the work is done", not a forecast. Your Search Console and analytics are the only truth.

---

## Week 0 (before day 1) — foundations

| Task | Why | Done when |
|---|---|---|
| Set `SITE_URL` in `build.py`, rebuild, deploy | Canonicals, sitemap, OG URLs all derive from it | `https://sohailabbas.site/sitemap.xml` loads |
| Serve over HTTPS with a single canonical host (no `www` / non-`www` duplication) | Two hosts = split signals | One 301 direction, verified with `curl -I` |
| Map `404.html` as the error page; make sure unknown URLs return 404 (not 200) | Soft-404s waste crawl budget | `/nonsense/` returns HTTP 404 |
| Verify Google Search Console (DNS or HTML file) and Bing Webmaster Tools | Indexing, queries, errors | Both verified |
| Submit `sitemap.xml` in both | Faster discovery | Sitemap status "Success", 32 URLs |
| Run 3 tool pages through the Rich Results Test | Catch structured-data mistakes before indexing | WebApplication / FAQ / HowTo valid |
| Add analytics (Plausible or GA4) **with consent** if you target the EU/UK | You cannot manage what you do not measure | Events: tool_used, file_converted |
| Check Core Web Vitals on mobile (PageSpeed Insights) | Baseline before content grows | LCP < 2.5 s, CLS < 0.1 |
| Confirm the privacy policy matches reality (no cookies, no uploads) | Trust + legal accuracy | Statement is true in network tools |

---

## Days 1–30 — get indexed, fix what the data shows

**Goal: every page crawled, zero technical errors, first long-tail impressions.**

### Week 1 — indexing
- Request indexing for the homepage, `/all-tools/`, and the 6 highest-intent tool pages
  (VAT, percentage, salary, loan EMI, PDF merge, image compressor).
- Let the rest be discovered from internal links; check *Pages → Discovered/ Crawled* in GSC.
- Check for duplicate-canonical surprises: `site:sohailabbas.site` should return tool pages, not
  `/tools/x/index.html` variants.

### Week 2 — internal linking pass
- From each tool page, verify 3–4 outbound internal links exist to genuinely related tools
  (the build already emits them from the `related` field).
- Add contextual links **inside paragraphs** where it helps a reader: e.g. the VAT page's
  "removing a percentage" sentence should link to the percentage calculator; salary → overtime;
  image compressor → image to PDF → PDF merger.
- Do not add footer-wide links to everything; keep the link value in the body copy.

### Week 3 — query mining (first real data)
- GSC → Performance → Queries. Filter position 8–30. These are the pages Google is testing.
- For each promising query: does the page answer it in the first screen? If not, adjust the H2 or
  the first paragraph, not the whole page.
- Build a list of queries the site appears for but has no page for. Those are candidates — evaluate
  them against the same filter as the spreadsheet: intent match, KD, and whether a *tool* (not an
  article) is what ranks.

### Week 4 — content depth on the two best pages
- Pick the two pages with the best impressions-to-position ratio.
- Add what is genuinely missing: worked examples with different units, an edge case (zero,
  negative, 29 February, zero-rate VAT), or a reference table readers keep returning to.
- Update the "editorially reviewed" date only if the content actually changed.

**Day-30 checkpoint:** pages indexed ≥ 30/32 · zero coverage errors · impressions on long-tails ·
at least 3 pages ranking 11–30 for a real query.

---

## Days 31–60 — earn relevance, not links first

**Goal: move the long-tails into the top 10 and build the links that a tool genuinely deserves.**

### Content improvements (weeks 5–6)
- For each tool page ranking 11–20 for a long-tail, add a dedicated section that answers *that*
  query explicitly — a short answer in the first sentence, then the detail. This is how you win
  featured snippets without adding thin pages.
- Add one genuinely useful asset per top-5 tool: for example a VAT rate table by country (done),
  a salary-to-hourly reference table (done), an overtime multiplier chart (done). Keep them
  accurate and date-stamped.
- **Do not** create per-city or per-country duplicate pages yet. If the VAT page ranks, consider a
  separate page only for a market where the intent differs enough to justify it (e.g. a
  German-language MwSt page), and only if a native speaker can review the translation.

### Localisation decision (week 6)
- Pick **one** market from the Country plan sheet where competition is lowest (Netherlands or
  Poland are the least contested in the research). Translate 3–5 high-fit tools properly, with
  `hreflang` pairs and localised titles. Machine translation without review is worse than no
  translation — it reads as low quality and can be flagged.

### Backlinks (weeks 5–8) — realistic, small, relevant
The only link tactics that work for a new tool site:
1. **Answer real questions where the tool is the answer.** Reddit, Stack Exchange (Super User for
   JSON/PDF, Personal Finance for loans, Expatriates for VAT), Quora. Link only when the tool solves
   the actual question, and disclose nothing false. One good answer can out-earn 50 directory links.
2. **Get listed where tools are listed.** Relevant free tool directories, "alternatives to
   iLovePDF / Smallpdf / Tinypng" listicles that accept submissions, and privacy-tool lists
   (our no-upload angle fits those specifically).
3. **Pitch the differentiator, not the tool.** "This converter never uploads your file" is a story
   privacy blogs and EU-data-protection writers may cover. "Free PDF merger" is not a story.
4. **Fix unlinked mentions.** Search for the domain name; where it is mentioned without a link, ask.
5. **No paid link packages, no PBNs, no comment spam.** For a site whose entire promise is honesty,
   the downside is not worth the risk.

### Technical (weeks 7–8)
- Check GSC *Core Web Vitals* — the file tools load two vendored libraries only on the pages that
  need them; confirm they are not blocking LCP elsewhere.
- Audit internal 404s (links to removed slugs) and fix redirects.
- Re-test structured data after any template change.

**Day-60 checkpoint:** at least 2 pages ranking top 10 for a long-tail · referring domains > 3 and
all topically relevant · GSC clicks trending up week over week (small numbers are normal).

---

## Days 61–90 — consolidate and decide what is worth more work

**Goal: stop adding surface area. Make the winners win.**

### Weeks 9–10 — prune and consolidate
- Anything with zero impressions after 60 days: is it because the SERP is owned by a giant
  (BMI → NHS/CDC, percentage → calculator.net)? Then keep it as an internal-link and trust asset and
  stop optimising it. Do not delete a working tool to chase a metric.
- Anything ranking 5–15: give it the next round of work. These respond fastest.
- Merge any page that duplicates intent (as we already did with character counter → word counter).

### Weeks 11–12 — topical authority on the strongest cluster
- Pick the cluster with the best traction, most likely **money & tax** (VAT, percentage, salary,
  loan, discount, overtime, tip) or **files** (PDF/image).
- Strengthen the cluster hub page (`/category/money-tax/`) with a short, genuinely useful
  introduction and clear internal links; make it the page you link to when you mention the cluster.
- Add 1–2 *supporting* content pieces **only if** they answer a distinct query better than the tool
  page can, e.g. "how to remove VAT correctly (and why subtracting 20% is wrong)" — a real
  explanation with worked numbers, linked from the tool page.

### Month 3 measurement review
Produce one page of notes answering:
1. Which 5 queries bring the most impressions? Do the pages ranking for them answer the query in
   the first 100 words?
2. Which of the 20 tools has the best click-through rate? Why? (Usually the title/description.)
3. Which has zero impressions after 90 days, and what is the *reason*? (SERP owned by an authority,
   no demand, wrong intent, technical issue.)
4. What is the single biggest content gap the data reveals?

Then rewrite the next 90 days from that evidence, not from a template.

---

## Ongoing monthly rhythm (from day 91)

| Cadence | Task |
|---|---|
| Weekly | Check GSC coverage errors, 404s, and the queries report for position 8–30 movements |
| Monthly | Review VAT rates and tax-related tables against national authority pages; update the "last reviewed" date only when checked |
| Monthly | Browser-test every file tool on desktop and a real phone (uploads, downloads, large files) |
| Quarterly | Rewrite one underperforming page from scratch rather than adding a new one |
| Quarterly | Re-run the keyword export and re-rank tools if the evidence has changed |
| Never | Publish a page with no tool, no unique value, or a claim the tool cannot support |

---

## What this plan will not do

- It will not rank a brand-new domain for "bmi calculator" or "percentage calculator" in 90 days —
  those SERPs are held by NHS, CDC, calculator.net and rapidtables.
- It will not produce AdSense approval. That is an editorial and policy decision made by Google, and
  nothing here influences it. If you apply, do it after the site has real traffic and every page
  has been read end-to-end by a human.
- It will not make paid-link or spam tactics safe. They are not.
- It will not replace checking your own numbers. Every metric in your reports is the only metric
  that matters.
