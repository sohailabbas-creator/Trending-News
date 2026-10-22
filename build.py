#!/usr/bin/env python3
"""
sohailabbas.site — static site generator for 20 browser-based tools.

Output structure (clean, extensionless URLs):
  site/index.html
  site/tools/<slug>/index.html
  site/category/<slug>/index.html
  site/about/index.html  site/contact/  site/privacy-policy/  site/terms/
  site/all-tools/index.html
  site/sitemap.xml  robots.txt  llms.txt  manifest.webmanifest  404.html

Run:  python3 build.py           build
      python3 build.py --check   build + validate SEO constraints
"""
import html
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "site")

SITE_NAME = "SohailAbbas Tools"
SITE_URL = "https://sohailabbas.site"
BRAND_SHORT = "sohailabbas.site"
CONTACT_EMAIL = "hello@sohailabbas.site"
TAGLINE = "20 free browser-based calculators and converters"
TODAY = date.today().isoformat()
YEAR = date.today().year

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' rx='14' fill='%231d4ed8'/%3E"
           "%3Ctext x='32' y='44' font-family='Arial,Helvetica,sans-serif' font-size='34'"
           " font-weight='700' fill='%23ffffff' text-anchor='middle'%3Es%3C/text%3E%3C/svg%3E")


# ----------------------------------------------------------------- data
def load_json(name):
    with open(os.path.join(SRC, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def load_tools():
    tools = []
    for f in ("tools-1.json", "tools-2.json"):
        tools.extend(load_json(f))
    tools.sort(key=lambda t: t["rank"])
    ranks = [t["rank"] for t in tools]
    assert ranks == list(range(1, len(tools) + 1)), f"ranks broken: {ranks}"
    assert len(tools) == 20, f"expected 20 tools, got {len(tools)}"
    slugs = [t["slug"] for t in tools]
    assert len(set(slugs)) == len(slugs), "duplicate slug"
    cats = {c["slug"] for c in load_json("categories.json")}
    for t in tools:
        assert t["category"] in cats, f"{t['slug']}: unknown category {t['category']}"
    return tools


def fragment(path):
    with open(os.path.join(SRC, path), encoding="utf-8") as fh:
        return fh.read().strip()


# ----------------------------------------------------------------- helpers
def esc(v):
    return html.escape(str(v), quote=True)


def relpath(from_url, to_url):
    """Relative link from the page at from_url to to_url.

    from_url is the *directory* URL of the current page (e.g. "tools/vat-calculator/"),
    so the whole path is the base - not its dirname.
    """
    a = from_url.strip("/") or "."
    b = to_url.strip("/")
    if not b:
        return os.path.relpath(".", a) + "/"
    r = os.path.relpath(b, a)
    return r + "/" if not r.endswith("/") else r


def up(url):
    """Prefix that returns to site root from a page URL like tools/x/."""
    depth = len([p for p in url.strip("/").split("/") if p])
    return "../" * depth


def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>")


def icon(d, label=None, size=22):
    attrs = f'role="img" aria-label="{esc(label)}"' if label else 'aria-hidden="true"'
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" {attrs}><title>{esc(label or "")}</title>'
            f'<path d="{esc(d)}"/></svg>')


def head(title, desc, canonical, prefix, extra_meta=None, noindex=False,
         og_type="website", keywords=None):
    robots = "noindex, follow" if noindex else "index, follow, max-snippet:-1, max-image-preview:large"
    kw = (f'<meta name="keywords" content="{esc(", ".join(keywords))}">\n' if keywords else "")
    extra = "\n".join(extra_meta) if extra_meta else ""
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1d4ed8">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{kw}<meta name="robots" content="{robots}">
<link rel="canonical" href="{esc(canonical)}">
<link rel="icon" href="{FAVICON}">
<link rel="apple-touch-icon" href="{FAVICON}">
<link rel="manifest" href="{prefix}manifest.webmanifest">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(SITE_NAME)} — 20 free online calculators and converters">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE_URL}/assets/og.png">
<link rel="stylesheet" href="{prefix}assets/style.css">
{extra}"""


NAV = [
    ("", "Home"),
    ("all-tools/", "All tools"),
    ("category/", "Categories"),
    ("about/", "About"),
    ("contact/", "Contact"),
]


def header(cur_url):
    items = []
    for href, label in NAV:
        target = relpath(cur_url, href) if href else relpath(cur_url, "")
        active = ' aria-current="page"' if href and cur_url.startswith(href) else ""
        items.append(f'<li><a href="{target}"{active}>{esc(label)}</a></li>')
    return f"""<a class="skip" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{relpath(cur_url, '')}">
      <span class="brand-mark" aria-hidden="true">s</span>
      <span class="brand-text">{esc(SITE_NAME)}</span>
    </a>
    <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="site-nav">
      <span class="sr-only">Toggle navigation</span><span aria-hidden="true">☰</span>
    </button>
    <nav id="site-nav" class="site-nav" aria-label="Main">
      <ul>{''.join(items)}</ul>
    </nav>
  </div>
</header>"""


def footer(cur_url, tools, cats):
    tool_links = "".join(
        f'<li><a href="{relpath(cur_url, f"tools/{t["slug"]}/")}">{esc(t["name"])}</a></li>'
        for t in tools[:10])
    tool_links2 = "".join(
        f'<li><a href="{relpath(cur_url, f"tools/{t["slug"]}/")}">{esc(t["name"])}</a></li>'
        for t in tools[10:])
    cat_links = "".join(
        f'<li><a href="{relpath(cur_url, f"category/{c["slug"]}/")}">{esc(c["name"])}</a></li>'
        for c in cats)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="{relpath(cur_url, '')}">
          <span class="brand-mark" aria-hidden="true">s</span>
          <span class="brand-text">{esc(SITE_NAME)}</span>
        </a>
        <p class="muted small">{esc(TAGLINE)}. Every tool runs in your browser — files are
          never uploaded to a server. Free, no account, no ads on this page.</p>
        <p class="muted small">Last reviewed: {TODAY}</p>
      </div>
      <nav aria-label="Tools 1-10"><h2 class="foot-h">Tools</h2><ul class="foot-list">{tool_links}</ul></nav>
      <nav aria-label="Tools 11-20"><h2 class="foot-h">More tools</h2><ul class="foot-list">{tool_links2}</ul></nav>
      <nav aria-label="Site"><h2 class="foot-h">Site</h2>
        <ul class="foot-list">{cat_links}
          <li><a href="{relpath(cur_url, 'about/')}">About</a></li>
          <li><a href="{relpath(cur_url, 'contact/')}">Contact</a></li>
          <li><a href="{relpath(cur_url, 'privacy-policy/')}">Privacy policy</a></li>
          <li><a href="{relpath(cur_url, 'terms/')}">Terms of use</a></li>
        </ul>
      </nav>
    </div>
    <div class="footer-bottom">
      <span>© {YEAR} {esc(SITE_NAME)}. Calculations are provided for information only — not financial,
        tax or medical advice.</span>
      <span><a href="{relpath(cur_url, 'sitemap.xml')}">Sitemap</a> · <a href="{relpath(cur_url, 'llms.txt')}">llms.txt</a></span>
    </div>
  </div>
</footer>
<script>
(function(){{
  var b=document.getElementById('nav-toggle'),n=document.getElementById('site-nav');
  if(!b||!n)return;
  b.addEventListener('click',function(){{
    var open=n.classList.toggle('open');
    b.setAttribute('aria-expanded',open?'true':'false');
  }});
}})();
</script>"""


def breadcrumbs(cur_url, trail):
    """trail: list of (label, url or None)"""
    parts = []
    for i, (label, url) in enumerate(trail):
        if url:
            parts.append(f'<li><a href="{relpath(cur_url, url)}">{esc(label)}</a></li>')
        else:
            parts.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(parts) + "</ol></nav>"


def crumb_ld(trail):
    out = []
    for i, (label, url) in enumerate(trail, start=1):
        item = {"@type": "ListItem", "position": i, "name": label}
        item["item"] = SITE_URL + "/" + (url if url else "")
        out.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": out}


def example_table(ex):
    if not ex:
        return ""
    head_cells = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in ex["head"])
    rows = "".join(
        "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in ex["rows"])
    return (f'<div class="table-wrap"><table class="data">{ex.get("caption", "")}'
            f'<thead><tr>{head_cells}</tr></thead><tbody>{rows}</tbody></table></div>')


# ----------------------------------------------------------------- pages
def page(cur_url, head_html, body):
    prefix = up(cur_url)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_html}
</head>
<body>
{header(cur_url)}
<main id="main">
{body}
</main>
{footer(cur_url, TOOLS, CATS)}
</body>
</html>
"""


def build_home():
    cur = ""
    chips = ['<button class="chip is-on" data-cat="all" aria-pressed="true">All 20</button>']
    for c in CATS:
        n = sum(1 for t in TOOLS if t["category"] == c["slug"])
        chips.append(f'<button class="chip" data-cat="{esc(c["slug"])}" aria-pressed="false">'
                     f'{esc(c["short"])} ({n})</button>')

    cards = []
    for t in TOOLS:
        search = esc((t["name"] + " " + t["tagline"] + " " + t["primary_keyword"] + " "
                      + " ".join(t["longtails"])).lower())
        cards.append(f"""      <li class="tool-card" data-cat="{esc(t['category'])}" data-search="{search}">
        <a class="card-link" href="{relpath(cur, f"tools/{t['slug']}/")}">
          <span class="card-top">{icon(t['icon'], t['name'] + ' icon')}<span class="card-rank">#{t['rank']}</span></span>
          <h3>{esc(t['name'])}</h3>
          <p>{esc(t['tagline'])}</p>
          <span class="card-cta">Open tool →</span>
        </a>
      </li>""")

    cat_cards = "".join(
        f'<a class="cat-card" href="{relpath(cur, f"category/{c["slug"]}/")}">'
        f'<b>{esc(c["name"])}</b><span>{esc(c["blurb"])}</span>'
        f'<em>{sum(1 for t in TOOLS if t["category"] == c["slug"])} tools</em></a>'
        for c in CATS)

    faq_home = [
        ("Are these tools really free?",
         "Yes. Every tool on sohailabbas.site is free to use with no account, no trial and no "
         "watermark. There is no paywall on any result or download."),
        ("Do you upload my files or numbers?",
         "No. All calculations, PDF merges and image conversions happen inside your browser using "
         "JavaScript. Your files are never sent to a server, which is why the tools keep working "
         "when your connection drops."),
        ("Can I use the results commercially?",
         "Yes. Numbers you calculate and files you convert are yours to use. The site and its written "
         "content remain our copyright — see the terms of use."),
        ("Why do different calculators show different results?",
         "Usually because of assumptions: how many weeks are in a working year, whether VAT is added "
         "or extracted, or whether interest is calculated monthly or annually. Each tool states its "
         "formula so you can check the difference."),
        ("Are the finance and health calculators official?",
         "No. They are estimate tools that use published formulas. Your bank, employer, tax authority "
         "or doctor is the authority for your specific situation."),
    ]
    faqs_html = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
        for i, (q, a) in enumerate(faq_home))

    body = f"""
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Free · No sign-up · Works offline</p>
    <h1>20 fast online tools for money, dates, text and files</h1>
    <p class="lede">Calculators, converters and file tools that run entirely in your browser.
      No uploads, no accounts, no waiting — and every page shows the formula it uses.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{relpath(cur, 'all-tools/')}">Browse all 20 tools</a>
      <a class="btn" href="{relpath(cur, 'tools/vat-calculator/')}">Open the VAT calculator</a>
    </div>
    <ul class="hero-facts">
      <li><b>20</b><span>tools</span></li>
      <li><b>7</b><span>categories</span></li>
      <li><b>0 KB</b><span>of your files uploaded</span></li>
      <li><b>100%</b><span>free, no account</span></li>
    </ul>
  </div>
</section>

<section class="wrap" aria-labelledby="finder">
  <h2 id="finder" class="section-title">Find a tool</h2>
  <div class="toolbar">
    <div class="search">
      <label class="sr-only" for="q">Search tools</label>
      <input id="q" type="search" placeholder="Search: VAT, PDF, BMI, overtime, diff…"
             autocomplete="off" spellcheck="false">
    </div>
    <div class="chips" id="chips">{''.join(chips)}</div>
  </div>
  <p class="result-count" id="count" role="status" aria-live="polite">Showing all 20 tools.</p>
  <ul class="tool-grid" id="grid">
{chr(10).join(cards)}
  </ul>
  <p class="empty" id="empty" hidden>No tool matches that search.
    <button class="link-btn" id="reset">Clear filters</button></p>
</section>

<section class="wrap" aria-labelledby="cats">
  <h2 id="cats" class="section-title">Browse by category</h2>
  <div class="cat-grid">{cat_cards}</div>
</section>

<section class="wrap prose-band">
  <h2>Built for people who need an answer, not a sign-up</h2>
  <p>Most calculator sites ask you to accept cookies, create an account or watch an ad before you
    see a result. These 20 tools do the opposite: the whole page is the tool, the formula is
    printed next to the answer, and nothing leaves your device. That matters most for the file
    tools — merging PDFs or compressing images usually means uploading sensitive documents to
    someone else's server.</p>
  <h3>What each page gives you</h3>
  <ul class="checklist">
    <li>A working tool above the fold, usable on a phone with one hand.</li>
    <li>The exact formula or rule behind the answer, so you can verify it.</li>
    <li>Worked examples with real numbers, plus a reference table where it helps.</li>
    <li>Honest limits: what the tool does not account for, and who the authority is.</li>
  </ul>
  <p class="muted small">No rankings, earnings or approval outcomes are promised anywhere on this
    site. Ranges you see in examples are illustrative arithmetic, not forecasts.</p>
</section>

<section class="wrap faq" aria-labelledby="faq-h">
  <h2 id="faq-h" class="section-title">Common questions</h2>
  {faqs_html}
</section>
"""
    home_ld = [{
        "@context": "https://schema.org", "@type": "WebSite",
        "name": SITE_NAME, "url": SITE_URL, "inLanguage": "en",
        "description": TAGLINE,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": SITE_URL + "/all-tools/?q={search_term_string}"},
            "query-input": "required name=search_term_string"},
    }, {
        "@context": "https://schema.org", "@type": "Organization",
        "name": SITE_NAME, "url": SITE_URL, "email": CONTACT_EMAIL,
        "description": TAGLINE,
    }, {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": "All tools on sohailabbas.site",
        "numberOfItems": len(TOOLS),
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "itemListElement": [
            {"@type": "ListItem", "position": t["rank"], "name": t["name"],
             "url": f"{SITE_URL}/tools/{t['slug']}/"} for t in TOOLS],
    }, {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_home],
    }]

    title = "20 Free Online Calculators & Converters | SohailAbbas Tools"
    desc = ("Free browser-based tools: VAT, salary, EMI and percentage calculators, PDF merger, "
            "image compressor, time zone and text diff. No uploads, no sign-up.")
    head_html = head(title, desc, SITE_URL + "/", "", [jsonld(x) for x in home_ld],
                     keywords=["free online tools", "calculator", "converter", "pdf tools",
                               "browser tools", "no sign up tools"])
    html_out = page(cur, head_html, body)

    search_js = """
(function(){
  var q=document.getElementById('q'),chips=[].slice.call(document.querySelectorAll('.chip')),
      cards=[].slice.call(document.querySelectorAll('.tool-card')),count=document.getElementById('count'),
      empty=document.getElementById('empty'),state={q:'',cat:'all'};
  function apply(){
    var term=state.q.trim().toLowerCase(),n=0;
    cards.forEach(function(c){
      var ok=(state.cat==='all'||c.dataset.cat===state.cat)&&(!term||c.dataset.search.indexOf(term)>-1);
      c.hidden=!ok; if(ok)n++;
    });
    count.textContent=n===cards.length?'Showing all '+cards.length+' tools.':'Showing '+n+' of '+cards.length+' tools.';
    empty.hidden=n>0;
  }
  q.addEventListener('input',function(){state.q=q.value;apply();});
  chips.forEach(function(ch){ch.addEventListener('click',function(){
    state.cat=ch.dataset.cat;
    chips.forEach(function(c){c.classList.toggle('is-on',c===ch);c.setAttribute('aria-pressed',String(c===ch));});
    apply();});});
  document.getElementById('reset').addEventListener('click',function(){
    state={q:'',cat:'all'};q.value='';chips.forEach(function(c){
      c.classList.toggle('is-on',c.dataset.cat==='all');c.setAttribute('aria-pressed',String(c.dataset.cat==='all'));});
    apply();});
  var p=new URLSearchParams(location.search).get('q');
  if(p){q.value=p;state.q=p;apply();}
})();
"""
    return html_out.replace("</body>", f"<script>{search_js}</script>\n</body>")


def build_all_tools():
    cur = "all-tools/"
    groups = []
    for c in CATS:
        items = [t for t in TOOLS if t["category"] == c["slug"]]
        rows = "".join(
            f'<li><a href="{relpath(cur, f"tools/{t["slug"]}/")}"><b>{esc(t["name"])}</b>'
            f'<span>{esc(t["tagline"])}</span></a></li>' for t in items)
        groups.append(f'<section class="list-group"><h2>{esc(c["name"])}'
                      f'<span class="muted small"> · {len(items)} tools</span></h2>'
                      f'<ul class="tool-list">{rows}</ul></section>')

    body = f"""
<div class="wrap">
{breadcrumbs(cur, [("Home", ""), ("All tools", None)])}
<header class="page-head">
  <h1>All 20 tools</h1>
  <p class="lede">Every tool on the site, grouped by category. Each one works on mobile,
    needs no account and processes your data locally.</p>
</header>
<div class="toolbar">
  <div class="search">
    <label class="sr-only" for="q">Filter tools</label>
    <input id="q" type="search" placeholder="Filter by name, e.g. VAT, PDF, BMI…" autocomplete="off">
  </div>
</div>
<p class="result-count" id="count" role="status" aria-live="polite"></p>
{''.join(groups)}
<p class="empty" id="empty" hidden>Nothing matches that filter.</p>
</div>
"""
    tools_ld = [{
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": "All tools", "url": SITE_URL + "/all-tools/",
        "description": "Directory of all 20 free browser-based tools.",
        "hasPart": [{"@type": "WebApplication", "name": t["name"],
                     "url": f"{SITE_URL}/tools/{t['slug']}/"} for t in TOOLS],
    }]
    title = "All 20 Tools — Complete Directory | SohailAbbas Tools"
    desc = ("The full directory of our 20 free tools: finance and tax calculators, date tools, "
            "text utilities, PDF and image converters. Search or browse by category.")
    head_html = head(title, desc, SITE_URL + "/all-tools/", up(cur),
                     [jsonld(x) for x in tools_ld] + [jsonld(crumb_ld([("Home", ""), ("All tools", "all-tools/")]))])
    out = page(cur, head_html, body)
    filt = """
(function(){
  var q=document.getElementById('q'),items=[].slice.call(document.querySelectorAll('.tool-list li')),
      groups=[].slice.call(document.querySelectorAll('.list-group')),count=document.getElementById('count'),
      empty=document.getElementById('empty');
  function apply(){
    var t=q.value.trim().toLowerCase(),n=0;
    items.forEach(function(li){var ok=!t||li.textContent.toLowerCase().indexOf(t)>-1;li.hidden=!ok;if(ok)n++;});
    groups.forEach(function(g){g.hidden=![].some.call(g.querySelectorAll('li'),function(li){return !li.hidden;});});
    count.textContent=n+' of '+items.length+' tools shown.';
    empty.hidden=n>0;
  }
  q.addEventListener('input',apply);apply();
  var p=new URLSearchParams(location.search).get('q'); if(p){q.value=p;apply();}
})();
"""
    return out.replace("</body>", f"<script>{filt}</script>\n</body>")


def build_category(c):
    cur = f"category/{c['slug']}/"
    items = [t for t in TOOLS if t["category"] == c["slug"]]
    cards = "".join(
        f'<li class="tool-card"><a class="card-link" href="{relpath(cur, f"tools/{t["slug"]}/")}">'
        f'<span class="card-top">{icon(t["icon"], t["name"] + " icon")}</span>'
        f'<h3>{esc(t["name"])}</h3><p>{esc(t["tagline"])}</p>'
        f'<span class="card-cta">Open tool →</span></a></li>' for t in items)
    others = "".join(
        f'<li><a href="{relpath(cur, f"category/{o["slug"]}/")}">{esc(o["name"])}</a></li>'
        for o in CATS if o["slug"] != c["slug"])
    body = f"""
<div class="wrap">
{breadcrumbs(cur, [("Home", ""), ("Categories", "category/"), (c["name"], None)])}
<header class="page-head">
  <h1>{esc(c["h1"])}</h1>
  <p class="lede">{esc(c["intro"])}</p>
</header>
<ul class="tool-grid">{cards}</ul>
<div class="prose">
  {c["body"]}
</div>
<div class="also">
  <h2>Other categories</h2>
  <ul class="pill-list">{others}</ul>
</div>
</div>
"""
    ld = [
        {"@context": "https://schema.org", "@type": "CollectionPage",
         "name": c["h1"], "url": f"{SITE_URL}/category/{c['slug']}/",
         "description": c["meta_description"],
         "isPartOf": {"@type": "WebSite", "url": SITE_URL},
         "hasPart": [{"@type": "WebApplication", "name": t["name"],
                      "url": f"{SITE_URL}/tools/{t['slug']}/"} for t in items]},
        crumb_ld([("Home", ""), ("Categories", "category/"), (c["name"], f"category/{c['slug']}/")]),
    ]
    head_html = head(c["meta_title"], c["meta_description"],
                     f"{SITE_URL}/category/{c['slug']}/", up(cur), [jsonld(x) for x in ld],
                     keywords=c.get("keywords"))
    return page(cur, head_html, body)


def build_categories_hub():
    cur = "category/"
    cards = "".join(
        f'<a class="cat-card" href="{relpath(cur, f"category/{c["slug"]}/")}">'
        f'<b>{esc(c["name"])}</b><span>{esc(c["blurb"])}</span>'
        f'<em>{sum(1 for t in TOOLS if t["category"] == c["slug"])} tools</em></a>' for c in CATS)
    body = f"""
<div class="wrap">
{breadcrumbs(cur, [("Home", ""), ("Categories", None)])}
<header class="page-head">
  <h1>Browse tools by category</h1>
  <p class="lede">Twenty tools, seven categories. Pick the area you are working in — money,
    dates, text, code, files, time or health.</p>
</header>
<div class="cat-grid">{cards}</div>
</div>
"""
    title = "All Categories — 20 Free Tools | SohailAbbas Tools"
    desc = ("Browse every tool by category: finance and tax calculators, date and time tools, "
            "text utilities, developer tools, PDF and image converters, and health calculators.")
    head_html = head(title, desc, SITE_URL + "/category/", up(cur),
                     [jsonld(crumb_ld([("Home", ""), ("Categories", "category/")]))])
    return page(cur, head_html, body)


def build_tool(t):
    by_slug = {x["slug"]: x for x in TOOLS}
    cur = f"tools/{t['slug']}/"
    cat = next(c for c in CATS if c["slug"] == t["category"])
    related = [by_slug[s] for s in t["related"] if s in by_slug and s != t["slug"]][:4]
    if len(related) < 3:
        for cand in TOOLS:
            if len(related) >= 3:
                break
            if cand["slug"] != t["slug"] and cand not in related:
                related.append(cand)

    canonical = f"{SITE_URL}/tools/{t['slug']}/"
    trail = [("Home", ""), (cat["name"], f"category/{cat['slug']}/"), (t["name"], None)]

    steps = "".join(f"<li>{esc(s)}</li>" for s in t["how_to"])
    feats = "".join(f"<li>{esc(f)}</li>" for f in t["features"])
    longtails = "".join(f"<li>{esc(k)}</li>" for k in t["longtails"])
    relterms = "".join(f"<li>{esc(k)}</li>" for k in t["related_terms"])
    faqs = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>'
        for i, f in enumerate(t["faqs"]))
    examples = "".join(
        f'<h3>{esc(e["title"])}</h3><p>{esc(e["body"])}</p>' for e in t.get("examples", []))
    related_cards = "".join(
        f'<a class="rel-card" href="{relpath(cur, f"tools/{o["slug"]}/")}">'
        f'<b>{esc(o["name"])}</b><span>{esc(o["tagline"])}</span></a>' for o in related)

    intro_html = "".join(f"<p>{esc(p)}</p>" for p in t["intro"])

    body = f"""
<div class="wrap">
{breadcrumbs(cur, trail)}
<div class="tool-hero">
  <div class="tool-hero-main">
    <h1>{esc(t['h1'])}</h1>
    <p class="lede">{esc(t['tagline'])}</p>
    <ul class="badges">
      <li>{esc(cat['name'])}</li><li>Free</li><li>No sign-up</li><li>Runs locally</li>
    </ul>
  </div>
  <aside class="tool-hero-aside" aria-label="Quick facts">
    <dl>
      <dt>Primary search intent</dt><dd>{esc(t['intent_label'])}</dd>
      <dt>Works on</dt><dd>Phone, tablet, desktop</dd>
      <dt>Data leaves device?</dt><dd>No</dd>
    </dl>
  </aside>
</div>

<section class="tool-shell" aria-label="{esc(t['name'])}">
{fragment('tools/' + t['slug'] + '.html').replace('{{P}}', up(cur))}
</section>

<div class="content-grid">
  <article class="prose">
    <h2 id="about">What the {esc(t['name'])} does</h2>
    {intro_html}

    <h2 id="how-to">How to use it</h2>
    <ol class="steps">{steps}</ol>

    <h2 id="features">Features</h2>
    <ul class="checklist">{feats}</ul>

    {f'<h2 id="examples">Worked examples</h2>{examples}' if examples else ''}
    {example_table(t.get('example_table'))}

    <h2 id="faq">Frequently asked questions</h2>
    <div class="faq">{faqs}</div>

    <h2 id="related">Related tools</h2>
    <div class="related">{related_cards}</div>

    <h2 id="keywords">What people search for</h2>
    <p class="small muted">This page is written to answer these real questions about
      {esc(t['primary_keyword'])}. They are listed for transparency, not as keyword stuffing.</p>
    <div class="kw-grid">
      <div><h3>Long-tail questions</h3><ul class="plain">{longtails}</ul></div>
      <div><h3>Related terms</h3><ul class="plain">{relterms}</ul></div>
    </div>
    <p class="small muted">Editorially reviewed {TODAY}. Formula and limits stated on this page.
      {esc(t['disclaimer'])}</p>
  </article>

  <aside class="sidebar" aria-label="On this page">
    <nav class="side-card">
      <h2>On this page</h2>
      <ul class="toc">
        <li><a href="#about">About</a></li>
        <li><a href="#how-to">How to use</a></li>
        <li><a href="#features">Features</a></li>
        <li><a href="#faq">FAQ</a></li>
        <li><a href="#related">Related tools</a></li>
        <li><a href="#keywords">Search terms</a></li>
      </ul>
    </nav>
    <div class="side-card">
      <h2>In {esc(cat['name'])}</h2>
      <ul class="plain">
        {''.join(f'<li><a href="{relpath(cur, f"tools/{o["slug"]}/")}">{esc(o["name"])}</a></li>' for o in TOOLS if o["category"] == cat["slug"] and o["slug"] != t["slug"])}
        <li><a href="{relpath(cur, f"category/{cat["slug"]}/")}">All {esc(cat['name'].lower())} →</a></li>
      </ul>
    </div>
    <div class="side-card note">
      <h2>Editorial note</h2>
      <p class="small">{esc(t['editorial_note'])}</p>
    </div>
  </aside>
</div>
</div>
"""

    ld = [
        {"@context": "https://schema.org", "@type": "WebApplication",
         "name": t["name"], "url": canonical, "description": t["meta_description"],
         "applicationCategory": "UtilitiesApplication",
         "operatingSystem": "Any modern browser",
         "browserRequirements": "Requires JavaScript",
         "inLanguage": "en", "isAccessibleForFree": True,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "featureList": t["features"],
         "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
         "dateModified": TODAY},
        crumb_ld(trail),
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": f["q"],
                         "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in t["faqs"]]},
        {"@context": "https://schema.org", "@type": "HowTo",
         "name": f"How to use the {t['name']}", "description": t["tagline"],
         "totalTime": "PT1M",
         "step": [{"@type": "HowToStep", "position": i + 1, "text": s}
                  for i, s in enumerate(t["how_to"])]},
    ]
    head_html = head(t["meta_title"], t["meta_description"], canonical, up(cur),
                     [jsonld(x) for x in ld], keywords=t["keywords"])
    return page(cur, head_html, body)


def build_static(slug, meta_title, meta_desc, title_h1, frag_path, extra_ld=None, keywords=None):
    cur = f"{slug}/"
    body_frag = fragment(frag_path).replace("{{P}}", up(cur)) \
        .replace("{{EMAIL}}", CONTACT_EMAIL).replace("{{YEAR}}", str(YEAR))
    body = f"""
<div class="wrap narrow">
{breadcrumbs(cur, [("Home", ""), (title_h1, None)])}
<header class="page-head"><h1>{esc(title_h1)}</h1></header>
<article class="prose">{body_frag}</article>
</div>
"""
    ld = [crumb_ld([("Home", ""), (title_h1, f"{slug}/")])] + (extra_ld or [])
    head_html = head(meta_title, meta_desc, f"{SITE_URL}/{slug}/", up(cur),
                     [jsonld(x) for x in ld], keywords=keywords)
    return page(cur, head_html, body)


def build_404():
    body = """
<div class="wrap narrow center">
  <h1>Page not found</h1>
  <p class="lede">That address does not exist. It may have moved, or the link may be mistyped.</p>
  <p><a class="btn btn-primary" href="/all-tools/">Browse all 20 tools</a></p>
</div>
"""
    return page("404.html", head("Page not found (404) | SohailAbbas Tools",
                                 "The page you asked for does not exist. Browse the 20 free tools instead.",
                                 SITE_URL + "/404.html", "", noindex=True), body)


def build_sitemap():
    urls = [(SITE_URL + "/", "1.0", "weekly")]
    urls.append((SITE_URL + "/all-tools/", "0.9", "weekly"))
    urls.append((SITE_URL + "/category/", "0.7", "monthly"))
    for c in CATS:
        urls.append((f"{SITE_URL}/category/{c['slug']}/", "0.7", "monthly"))
    for t in TOOLS:
        urls.append((f"{SITE_URL}/tools/{t['slug']}/", "0.9" if t["rank"] <= 8 else "0.8", "monthly"))
    for slug in ("about", "contact", "privacy-policy", "terms"):
        urls.append((f"{SITE_URL}/{slug}/", "0.3", "yearly"))
    body = "".join(f"\n  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod>"
                   f"<changefreq>{freq}</changefreq><priority>{p}</priority></url>"
                   for loc, p, freq in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{body}\n</urlset>\n"), len(urls)


def build_robots():
    return ("# https://sohailabbas.site\nUser-agent: *\nAllow: /\nDisallow: /404.html\n\n"
            f"Sitemap: {SITE_URL}/sitemap.xml\n")


def build_llms():
    lines = [f"# {SITE_NAME}", "", f"> {TAGLINE}. No uploads, no accounts, no ads.", "",
             "All tools run client-side. Calculations use published formulas shown on each page.",
             "For tax, finance and health questions the user's own authority is the source of truth.",
             "", "## Tools", ""]
    for t in TOOLS:
        lines.append(f"- [{t['name']}]({SITE_URL}/tools/{t['slug']}/) — {t['tagline']}")
    lines += ["", "## Categories", ""]
    for c in CATS:
        names = ", ".join(t["name"] for t in TOOLS if t["category"] == c["slug"])
        lines.append(f"- {c['name']}: {names}")
    lines += ["", "## Pages", "",
              f"- [About]({SITE_URL}/about/)", f"- [Contact]({SITE_URL}/contact/)",
              f"- [Privacy policy]({SITE_URL}/privacy-policy/)", f"- [Terms]({SITE_URL}/terms/)"]
    return "\n".join(lines) + "\n"


def build_manifest():
    return json.dumps({
        "name": f"{SITE_NAME} — 20 free browser tools",
        "short_name": "SA Tools",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1d4ed8",
        "description": TAGLINE,
        "icons": []
    }, indent=2)


# ----------------------------------------------------------------- write
def w(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


TOOLS = load_tools()
CATS = load_json("categories.json")


def main():
    check = "--check" in sys.argv
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    w("index.html", build_home())
    w("all-tools/index.html", build_all_tools())
    w("category/index.html", build_categories_hub())
    for c in CATS:
        w(f"category/{c['slug']}/index.html", build_category(c))
    for t in TOOLS:
        w(f"tools/{t['slug']}/index.html", build_tool(t))

    pages = load_json("pages.json")
    for p in pages:
        w(f"{p['slug']}/index.html", build_static(
            p["slug"], p["meta_title"], p["meta_description"], p["h1"], p["fragment"],
            extra_ld=p.get("ld"), keywords=p.get("keywords")))

    w("404.html", build_404())
    sm, n = build_sitemap()
    w("sitemap.xml", sm)
    w("robots.txt", build_robots())
    w("llms.txt", build_llms())
    w("manifest.webmanifest", build_manifest())

    os.makedirs(os.path.join(OUT, "assets", "vendor"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets", "style.css"), os.path.join(OUT, "assets", "style.css"))
    for v in ("pdf-lib.min.js", "fflate.js"):
        src = os.path.join(ROOT, "assets", "vendor", v)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, "assets", "vendor", v))
    og = os.path.join(ROOT, "assets", "og.png")
    if os.path.exists(og):
        shutil.copy(og, os.path.join(OUT, "assets", "og.png"))

    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
    print(f"Built {n} sitemap URLs, {len(TOOLS)} tool pages, {len(CATS)} category pages, "
          f"{len(pages)} static pages → {OUT} ({total/1024:.0f} KB)")
    if check:
        validate()


# ----------------------------------------------------------------- checks
def validate():
    problems = []
    titles, descs = {}, {}
    pages = [os.path.join(dp, f) for dp, _, fs in os.walk(OUT) for f in fs if f.endswith(".html")]
    for p in pages:
        s = open(p, encoding="utf-8").read()
        rel = os.path.relpath(p, OUT)
        t = re.search(r"<title>(.*?)</title>", s)
        d = re.search(r'<meta name="description" content="(.*?)">', s)
        if not t or not d:
            problems.append(f"{rel}: missing title/description")
            continue
        title, desc = html.unescape(t.group(1)), html.unescape(d.group(1))
        titles.setdefault(title, []).append(rel)
        descs.setdefault(desc, []).append(rel)
        if "noindex" not in s:
            if not (45 <= len(title) <= 62):
                problems.append(f"{rel}: title {len(title)} chars — {title!r}")
            if not (135 <= len(desc) <= 165):
                problems.append(f"{rel}: description {len(desc)} chars")
            if len(re.findall(r"<h1[\s>]", s)) != 1:
                problems.append(f"{rel}: {len(re.findall(r'<h1[ >]', s))} h1 tags")
            if 'rel="canonical"' not in s:
                problems.append(f"{rel}: no canonical")
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(m.group(1))
            except Exception as exc:
                problems.append(f"{rel}: invalid JSON-LD ({exc})")
        # unbalanced colons in alt/aria handled by browser; check img alt presence
        for img in re.findall(r"<img\b[^>]*>", s):
            if "alt=" not in img:
                problems.append(f"{rel}: <img> without alt")
    for title, where in titles.items():
        if len(where) > 1:
            problems.append(f"duplicate title on {where}")
    for desc, where in descs.items():
        if len(where) > 1:
            problems.append(f"duplicate description on {where}")
    if problems:
        print("\nCHECK FAILED:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"CHECK PASSED: {len(pages)} pages — unique titles/descriptions in range, "
          f"single h1, canonical present, JSON-LD valid, all images have alt text.")


if __name__ == "__main__":
    main()
