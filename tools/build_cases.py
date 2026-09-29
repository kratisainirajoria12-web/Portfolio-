"""Generate the three case-study pages in /work from one shared template.

Edit the content in PROJECTS below, then run:  python3 tools/build_cases.py
The cover artwork for each project is pulled from the matching stage in index.html
so the home page and the case study always share the same visual identity.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = (ROOT / "index.html").read_text()


def stage(cls):
    """Return the <div class="stage-scene"> markup of a project on the home page."""
    art = HOME.split(f'class="project {cls}')[1]
    start = art.index('<div class="stage-scene">')
    depth, i = 0, start
    for m in re.finditer(r"<(/?)div\b", art[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            i = start + m.end()
            break
    end = art.index(">", i) + 1
    return art[start:end]


# ---------------------------------------------------------------- mock screens

DD_BEFORE = """
<div class="m-h">New discount</div>
<div class="m-col">
  <div class="m-field"><b>Discount code</b>SUMMER-SALE-24</div>
  <div class="m-row"><div class="m-field" style="flex:1"><b>Type</b>Select… ▾</div><div class="m-field" style="flex:1"><b>Value</b>—</div></div>
  <div class="m-field"><b>Applies to</b>Collections / Products / All ▾</div>
  <div class="m-row"><div class="m-field" style="flex:1"><b>Min. requirement</b>None ▾</div><div class="m-field" style="flex:1"><b>Eligibility</b>Everyone ▾</div></div>
  <div class="m-row"><div class="m-field" style="flex:1"><b>Usage limits</b>—</div><div class="m-field" style="flex:1"><b>Combinations</b>—</div></div>
  <div class="m-row"><div class="m-field" style="flex:1"><b>Start</b>dd/mm/yyyy</div><div class="m-field" style="flex:1"><b>End</b>dd/mm/yyyy</div></div>
  <div><span class="m-btn m-btn--muted">Save</span></div>
</div>
<span class="m-note" style="right:4cqw;top:14cqw">Every option on one screen — merchants didn’t know where to start</span>
"""

DD_AFTER = """
<div class="m-small">Step 1 of 3</div>
<div class="m-h">What do you want to offer?</div>
<div class="m-col">
  <div class="m-choice on"><b>% off</b> &nbsp;<span class="m-small">e.g. 20% off everything</span></div>
  <div class="m-choice"><b>Buy X, get Y</b> &nbsp;<span class="m-small">e.g. buy 2, get 1 free</span></div>
  <div class="m-choice"><b>Free shipping</b> &nbsp;<span class="m-small">over a minimum spend</span></div>
  <div class="m-card m-row" style="justify-content:space-between"><span class="m-small">Customers will see</span><b>20% off · ends Sun</b></div>
  <div class="m-row" style="justify-content:flex-end"><span class="m-btn">Continue</span></div>
</div>
<span class="m-note m-note--good" style="left:5cqw;bottom:5cqw">Start from the goal, not the settings</span>
"""

BIE_BEFORE = """
<div class="m-row" style="align-items:flex-start">
  <div class="m-img" style="width:46%;aspect-ratio:1"></div>
  <div class="m-col" style="flex:1">
    <div class="m-h" style="font-size:3.6cqw">Velvet Lip Tint</div>
    <div class="m-line" style="width:40%"></div>
    <div class="m-line"></div><div class="m-line"></div><div class="m-line" style="width:70%"></div>
    <div class="m-line"></div><div class="m-line" style="width:60%"></div>
    <div class="m-field">Shade ▾</div>
  </div>
</div>
<div class="m-col" style="margin-top:3cqw">
  <div class="m-line"></div><div class="m-line" style="width:80%"></div>
  <div><span class="m-btn">Add to cart</span></div>
</div>
<span class="m-note" style="left:4cqw;top:36cqw">Shade hidden in a dropdown</span>
<span class="m-note" style="right:4cqw;bottom:14cqw">Price, reviews &amp; delivery below the fold</span>
"""

BIE_AFTER = """
<div class="m-row" style="align-items:flex-start">
  <div class="m-img" style="width:46%;aspect-ratio:1"></div>
  <div class="m-col" style="flex:1">
    <div class="m-h" style="font-size:3.6cqw;margin:0">Velvet Lip Tint</div>
    <div class="m-row"><b>₹549</b><span class="m-small">★ 4.7 · 312 reviews</span></div>
    <div class="m-small">Shade: <b style="color:var(--ink)">Rosewood</b></div>
    <div class="m-row" style="gap:1.6cqw">
      <span style="width:5cqw;height:5cqw;border-radius:50%;background:#c47b73"></span>
      <span style="width:5cqw;height:5cqw;border-radius:50%;background:#a3504d;box-shadow:0 0 0 .6cqw #fff,0 0 0 1cqw var(--accent-p)"></span>
      <span style="width:5cqw;height:5cqw;border-radius:50%;background:#d9a08f"></span>
      <span style="width:5cqw;height:5cqw;border-radius:50%;background:#8e5b4b"></span>
    </div>
    <span class="m-btn">Add to bag</span>
    <div class="m-small">🚚 Free delivery by Thu · Easy returns</div>
  </div>
</div>
<div class="m-card m-row" style="margin-top:3cqw;justify-content:space-between"><span class="m-small">“Doesn’t dry out my lips”</span><b class="m-small">Read reviews →</b></div>
<span class="m-note m-note--good" style="right:4cqw;bottom:4cqw">Everything needed to decide, above the fold</span>
"""

HF_BEFORE = """
<div class="m-row" style="justify-content:space-between;margin-bottom:3cqw">
  <b style="font-family:Arial,sans-serif;color:#2e8b3d;font-size:4cqw;letter-spacing:.02em">HEALTH FAB</b>
  <div class="m-row m-small">Home · Shop · Offers · Blog · Contact</div>
</div>
<div style="background:#2e8b3d;color:#fff;border-radius:1.4cqw;padding:4cqw;font-family:Arial,sans-serif">
  <div style="font-size:5cqw;font-weight:700">MEGA SALE!!! UPTO 50% OFF</div>
  <div style="font-size:2.4cqw;margin-top:1cqw">On all products. Hurry, limited stock.</div>
</div>
<div class="m-row" style="margin-top:3cqw">
  <div class="m-img" style="flex:1;aspect-ratio:1;background:#d6e8d0"></div>
  <div class="m-img" style="flex:1;aspect-ratio:1;background:#f3d3a8"></div>
  <div class="m-img" style="flex:1;aspect-ratio:1;background:#cfe0f0"></div>
</div>
<span class="m-note" style="right:4cqw;bottom:5cqw">Discount-led, generic — nothing felt ownable</span>
"""

HF_AFTER = """
<div class="m-row" style="justify-content:space-between;margin-bottom:3cqw">
  <b style="font-family:var(--serif);font-weight:400;font-size:4.4cqw;color:#3f4a22">health<i>fab</i></b>
  <div class="m-row m-small">Shop · Rituals · Our story</div>
</div>
<div class="m-row" style="background:#ece2c8;border-radius:2cqw;padding:4cqw;align-items:center">
  <div class="m-col" style="flex:1.2">
    <div style="font:400 5cqw/1.05 var(--serif);color:#3f4a22">Everyday health,<br><i>made gentle.</i></div>
    <div><span class="m-btn">Find your ritual</span></div>
  </div>
  <div style="flex:1;display:flex;justify-content:center">
    <div style="width:14cqw;height:20cqw;border-radius:2.4cqw;background:#f3ece0;box-shadow:inset -1cqw -1cqw 2cqw rgba(0,0,0,.08);position:relative">
      <div style="position:absolute;left:0;right:0;top:6cqw;height:6cqw;background:#e9a978"></div>
    </div>
  </div>
</div>
<div class="m-row" style="margin-top:3cqw;gap:2cqw">
  <span style="flex:1;height:6cqw;border-radius:1.4cqw;background:#74824f"></span>
  <span style="flex:1;height:6cqw;border-radius:1.4cqw;background:#e9a978"></span>
  <span style="flex:1;height:6cqw;border-radius:1.4cqw;background:#f3ece0;box-shadow:inset 0 0 0 1px #e3d9c6"></span>
  <span style="flex:1;height:6cqw;border-radius:1.4cqw;background:#3f4a22"></span>
</div>
<span class="m-note m-note--good" style="right:4cqw;top:5cqw">Leads with care, not coupons</span>
"""

# ---------------------------------------------------------------- content
# NOTE: Copy below is a considered first draft. Replace any detail that
# doesn't match what actually happened, and add your real metrics where
# marked in OUTCOMES.

PROJECTS = [
    dict(
        slug="discount-discovery",
        cls="project--ddapp",
        case="case--ddapp",
        num="01 — Shopify app",
        title="Discount Discovery App",
        lede="Making discount creation simple enough for merchants who run their store alone — and don’t have time to become promotions experts.",
        meta=[("Role", "Product designer"), ("Scope", "Research, UX, UI, design system"), ("Team", "PM, 2 engineers, me"), ("Platform", "Shopify admin app")],
        tldr=[
            ("Problem", "Merchants wanted to run promotions, but the discount setup forced them to understand every setting before they could launch anything."),
            ("What I did", "Reframed setup around the merchant’s goal, split it into a guided three-step flow, and added a live preview of what shoppers see."),
            ("Outcome", "A calmer, faster setup that merchants could finish without help — and a component set the team reused across the app."),
        ],
        problem="""<p>The app helped Shopify merchants create and surface discounts, but most of the value was hidden behind a <strong>single, dense configuration form</strong>. Code, type, value, eligibility, limits, combinations and dates all lived on one screen.</p>
<p>For experienced marketers that was fine. For the small-store owners who made up most installs, it was a wall. They abandoned setup halfway, created discounts that didn’t apply the way they expected, or wrote to support asking which option to pick.</p>
<p><strong>The question:</strong> how might we help a merchant go from “I want to run a sale” to a live, correct discount — without needing to understand every setting first?</p>""",
        role="""<p>I was the sole designer, working with a product manager and two engineers. I owned the work end to end: research planning, synthesis, flows, UI, prototype testing and design QA during build.</p>""",
        role_pills=["User interviews", "Support-ticket analysis", "Flows & IA", "Prototyping", "Usability testing", "Design QA"],
        methods=[
            ("Merchant interviews", "Conversations with small-store owners about how they plan and launch promotions."),
            ("Support tickets", "Tagged recent tickets to find which settings caused the most confusion."),
            ("Competitive review", "Walked through discount setup in comparable Shopify apps and native admin."),
            ("Funnel review", "Looked at where in setup merchants dropped off or saved without publishing."),
        ],
        insights=[
            ("Merchants think in goals, not settings", "They described promotions as outcomes — “clear old stock”, “thank loyal customers” — never as a discount type plus conditions.", "I just want 20% off for the weekend. Why do I need to decide all this?"),
            ("Uncertainty, not effort, caused drop-off", "People could fill the form. What stopped them was not knowing what the shopper would actually see once it went live.", None),
            ("Advanced options were needed — occasionally", "Usage limits and combinations mattered, but only for a minority of discounts. They shouldn’t block the common case.", None),
        ],
        decisions=[
            ("Start with the goal", "The first screen now asks one question — what do you want to offer? — with plain-language examples under each option.", "Choosing an outcome first narrows every later decision, so merchants see only the settings that apply."),
            ("Three steps, with smart defaults", "Offer → who and what it applies to → when it runs. Sensible defaults are pre-filled, and advanced settings sit behind a single “More options” disclosure.", "Keeps the common path short without removing control for power users."),
            ("A live shopper preview", "A persistent card shows exactly how the discount will appear to customers, updating as the merchant edits.", "Directly addresses the biggest source of anxiety: “what will this actually look like?”"),
        ],
        before=("Before", "One long form. Every setting, visible at once, with no guidance on where to begin.", DD_BEFORE),
        after=("After", "A guided first step that starts from the merchant’s goal, with a live preview of the result.", DD_AFTER),
        outcomes=[
            ("7 → 3", "decisions needed before a basic discount can go live"),
            ("1 flow", "for every discount type, replacing separate forms"),
            ("Reusable", "choice cards, preview and stepper became shared components"),
        ],
        reflection="""<p>If I did this again I’d instrument the old flow earlier, so we had a cleaner baseline to compare against. I’d also like to explore templates — “weekend sale”, “first-order discount” — as an even faster starting point for new merchants.</p>""",
        next_slug="beauty-by-bie",
        next_title="Beauty by Bie",
        next_bg="#ecd4cb",
    ),
    dict(
        slug="beauty-by-bie",
        cls="project--bie",
        case="case--bie",
        num="02 — CRO case study",
        title="Beauty by Bie",
        lede="Finding where shoppers hesitated on a beauty storefront — and redesigning the product and checkout journey to remove that friction.",
        meta=[("Role", "UX & CRO designer"), ("Scope", "Audit, research, redesign, test plan"), ("Team", "Founder, developer, me"), ("Platform", "Shopify storefront")],
        tldr=[
            ("Problem", "Healthy traffic, but too few visitors were adding to bag, and too many carts were being abandoned before payment."),
            ("What I did", "Ran a CRO audit combining analytics, heatmaps, recordings and a quick survey, then prioritised and redesigned the key pages."),
            ("Outcome", "A clear, evidence-backed roadmap and a redesigned product page and cart built to answer shoppers’ questions up front."),
        ],
        problem="""<p>Beauty by Bie had a loyal audience on social media and plenty of visits to its store — but <strong>that attention wasn’t turning into orders</strong>. Visitors browsed, opened product pages and then left.</p>
<p>The brief was open: “find out why, and fix it.” Rather than jumping to a redesign, I started by finding exactly where in the journey people hesitated, and why.</p>""",
        role="""<p>I led the audit and redesign: setting up the research, analysing data, synthesising findings, prioritising opportunities with the founder, designing the new pages and writing the test plan for the developer.</p>""",
        role_pills=["Heuristic audit", "Analytics", "Heatmaps & recordings", "On-site survey", "Prioritisation (ICE)", "UI design", "A/B test plan"],
        methods=[
            ("Funnel analytics", "Mapped drop-off from landing to product page, bag, checkout and purchase."),
            ("Heatmaps & recordings", "Watched how people actually scrolled, tapped and hesitated on mobile."),
            ("Exit survey", "Asked leaving visitors one question: what stopped you today?"),
            ("Heuristic review", "Audited every step against e-commerce UX best practice."),
        ],
        insights=[
            ("Shade was the real decision", "Shoppers tapped repeatedly on product images trying to see shades. The shade picker was a small dropdown that many never opened.", "I can’t tell what colour this is going to be on me."),
            ("Key answers lived below the fold", "Price context, reviews and delivery information sat far down the page — most mobile visitors never scrolled that far.", None),
            ("Surprise costs at checkout", "Shipping costs appeared only at the last step, which lined up with a sharp spike in abandonment.", "Delivery was more than I expected."),
        ],
        decisions=[
            ("Make shade the hero", "Visual swatches replace the dropdown, with the selected shade named and reflected in the product imagery.", "Turns the most important decision into the most visible one."),
            ("Answer questions above the fold", "Price, rating, shade, add-to-bag and delivery promise now sit in the first screen on mobile, with a sticky add-to-bag as you scroll.", "Reduces the scrolling and guessing needed before committing."),
            ("No surprises in the bag", "A free-delivery progress bar and shipping estimate appear in the bag, long before payment.", "Removes the shock that was driving late-stage abandonment."),
        ],
        before=("Before", "Shade hidden in a dropdown; price, reviews and delivery info far below the fold.", BIE_BEFORE),
        after=("After", "Everything a shopper needs to decide is visible immediately, with shade as the hero.", BIE_AFTER),
        outcomes=[
            ("Ranked", "roadmap of opportunities, scored by impact and effort"),
            ("3", "redesigned templates: product page, bag and checkout entry"),
            ("A/B", "test plan handed over, starting with the product page"),
        ],
        reflection="""<p>The biggest lesson: most of the friction wasn’t visual at all — it was missing information. Next, I’d run the planned A/B tests one change at a time so we can attribute results clearly, and extend the shade work into a quick “find my shade” quiz.</p>""",
        next_slug="healthfab",
        next_title="Healthfab",
        next_bg="#e5d6b1",
    ),
    dict(
        slug="healthfab",
        cls="project--hf",
        case="case--hf",
        num="03 — Brand & digital",
        title="Healthfab",
        lede="A rebrand carried through packaging and a new e-commerce experience — one warmer, clearer identity from shelf to screen.",
        meta=[("Role", "Brand & UI designer"), ("Scope", "Identity, packaging, website"), ("Team", "Founders, printer, developer, me"), ("Deliverables", "Logo, system, packs, store")],
        tldr=[
            ("Problem", "The brand looked like every other discount wellness store, which made it hard to build trust or charge a fair price."),
            ("What I did", "Defined a new positioning with the founders, then designed the identity, packaging system and e-commerce site around it."),
            ("Outcome", "A cohesive, ownable brand that works on a shelf, in a feed and on a product page — and a system the team can extend."),
        ],
        problem="""<p>Healthfab made genuinely good everyday wellness products, but the brand <strong>didn’t say so</strong>. A generic logo, bright stock greens and constant sale banners made it look like a discount reseller.</p>
<p>The founders wanted a brand that felt caring and credible — something people would trust enough to make part of a daily routine, without it feeling clinical.</p>""",
        role="""<p>I led the rebrand from positioning workshop to launch: brand strategy with the founders, identity design, the packaging system, and the UI design of the new store, including design handover to the developer and print checks with the packaging supplier.</p>""",
        role_pills=["Brand workshop", "Positioning", "Logo & identity", "Packaging system", "Web UI", "Print & dev handover"],
        methods=[
            ("Founder workshop", "Defined who Healthfab is for, what it stands for and how it should feel."),
            ("Customer conversations", "Asked existing customers why they bought and what made them hesitate."),
            ("Shelf & category audit", "Mapped competitor brands to find where the category looked the same."),
            ("Moodboarding", "Explored three directions before committing to one."),
        ],
        insights=[
            ("The category shouts", "Competitors leaned on bright greens, bold claims and discounts. Calm and warm was an open space.", None),
            ("Customers bought for the routine", "People talked about habits and small rituals, not ingredients or price.", "It’s the one thing I do for myself every morning."),
            ("Trust came from clarity", "Hesitation came from unclear usage and ingredient information, not from price.", None),
        ],
        decisions=[
            ("A softer, warmer identity", "A rounded serif wordmark, an earthy olive-and-apricot palette and generous whitespace replace the generic green sans.", "Signals care and quality, and stands apart on a crowded shelf."),
            ("A modular packaging system", "One structure, with colour bands and a consistent information hierarchy for every product line.", "Easy to extend to new SKUs, and scannable at a glance."),
            ("A store built around rituals", "Shopping by routine (morning, recovery, sleep) sits alongside categories, with clear usage information on every product page.", "Mirrors how customers actually talk about the products."),
        ],
        before=("Before", "A discount-led homepage with a generic identity that could belong to any wellness store.", HF_BEFORE),
        after=("After", "A calmer, warmer store that leads with the brand’s care — and the product — instead of coupons.", HF_AFTER),
        outcomes=[
            ("1 system", "identity, packaging and web built from the same tokens"),
            ("Every SKU", "moved onto the modular packaging structure"),
            ("Launch", "new storefront shipped alongside the new packs"),
        ],
        reflection="""<p>Designing packaging and web together was the best decision in the project — each informed the other. With more time I’d have tested the packaging on shelf with real customers before the final print run.</p>""",
        next_slug="discount-discovery",
        next_title="Discount Discovery App",
        next_bg="#cfd9c8",
    ),
]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <script>document.documentElement.classList.add("js")</script>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Krati, UI/UX Designer</title>
  <meta name="description" content="{lede_attr}">
  <meta name="theme-color" content="#f4efe8">
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..500,100;1,9..144,300..500,100&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/base.css">
  <link rel="stylesheet" href="../css/home.css">
  <link rel="stylesheet" href="../css/case.css">
</head>
<body class="case {case}">
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="nav" id="nav">
    <div class="wrap">
      <a class="brand" href="../index.html" aria-label="Krati, home">
        <span class="brand-mark"><img src="../assets/krati.webp" alt="" width="40" height="40"></span>
        Krati
      </a>
      <nav aria-label="Primary">
        <ul class="nav-links">
          <li><a href="../index.html#work">Work</a></li>
          <li><a href="../index.html#about">About</a></li>
          <li><a href="../index.html#approach">Approach</a></li>
          <li><a class="nav-cta" href="../index.html#contact">Say hello</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
    <section class="case-hero wrap" aria-labelledby="case-title">
      <a class="back-link" href="../index.html#work"><span aria-hidden="true">←</span> All work</a>
      <p class="project-num reveal">{num}</p>
      <h1 id="case-title" class="reveal" style="--d:.06s">{title}</h1>
      <p class="lede reveal" style="--d:.12s">{lede}</p>
      <dl class="case-meta reveal" style="--d:.18s">
{meta}
      </dl>
    </section>

    <div class="wrap">
      <div class="case-cover reveal" aria-hidden="true">
        <div class="project-stage">
          {stage}
        </div>
      </div>

      <section class="tldr reveal" aria-label="Summary">
{tldr}
      </section>

      <div class="case-body">
        <aside class="toc" aria-label="On this page">
          <p>On this page</p>
          <ol>
            <li><a href="#problem">Problem</a></li>
            <li><a href="#role">My role</a></li>
            <li><a href="#research">Research</a></li>
            <li><a href="#insights">Insights</a></li>
            <li><a href="#decisions">Design decisions</a></li>
            <li><a href="#before-after">Before &amp; after</a></li>
            <li><a href="#outcomes">Outcomes</a></li>
            <li><a href="#reflection">Reflection</a></li>
          </ol>
        </aside>

        <article>
          <section class="chapter" id="problem" aria-labelledby="h-problem">
            <p class="chapter-num">01</p>
            <h2 id="h-problem">The problem</h2>
            <div class="prose">{problem}</div>
          </section>

          <section class="chapter" id="role" aria-labelledby="h-role">
            <p class="chapter-num">02</p>
            <h2 id="h-role">My role</h2>
            <div class="prose">{role}</div>
            <ul class="pill-list" aria-label="Responsibilities">{role_pills}</ul>
          </section>

          <section class="chapter" id="research" aria-labelledby="h-research">
            <p class="chapter-num">03</p>
            <h2 id="h-research">Research</h2>
            <div class="methods">
{methods}
            </div>
          </section>

          <section class="chapter" id="insights" aria-labelledby="h-insights">
            <p class="chapter-num">04</p>
            <h2 id="h-insights">What we learned</h2>
            <div class="insights">
{insights}
            </div>
          </section>

          <section class="chapter" id="decisions" aria-labelledby="h-decisions">
            <p class="chapter-num">05</p>
            <h2 id="h-decisions">Design decisions</h2>
            <div class="decisions">
{decisions}
            </div>
          </section>

          <section class="chapter" id="before-after" aria-labelledby="h-ba">
            <p class="chapter-num">06</p>
            <h2 id="h-ba">Before &amp; after</h2>
            <div class="compare">
{compare}
            </div>
          </section>

          <section class="chapter" id="outcomes" aria-labelledby="h-outcomes">
            <p class="chapter-num">07</p>
            <h2 id="h-outcomes">Outcomes</h2>
            <!-- Add your measured results here (e.g. conversion rate, completion rate, time on task). -->
            <div class="outcomes">
{outcomes}
            </div>
          </section>

          <section class="chapter" id="reflection" aria-labelledby="h-reflection">
            <p class="chapter-num">08</p>
            <h2 id="h-reflection">Reflection</h2>
            <div class="prose">{reflection}</div>
          </section>
        </article>
      </div>

      <a class="next" href="{next_slug}.html" style="--next-bg:{next_bg}">
        <span><small>Next project</small><strong>{next_title}</strong></span>
        <span class="arrow-circle" aria-hidden="true">→</span>
      </a>
    </div>
  </main>

  <footer class="footer">
    <div class="wrap">
      <p>© <span data-year>2026</span> Krati. Designed with care, built by hand.</p>
      <ul>
        <li><a href="../index.html#contact">Contact</a></li>
        <li><a href="#">LinkedIn</a></li>
        <li><a href="#">Behance</a></li>
      </ul>
    </div>
  </footer>

  <script src="../js/main.js" defer></script>
</body>
</html>
"""


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def build(p):
    meta = "\n".join(f"        <div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in p["meta"])
    tldr = "\n".join(f"        <div><h2>{k}</h2><p>{v}</p></div>" for k, v in p["tldr"])
    pills = "".join(f"<li>{x}</li>" for x in p["role_pills"])
    methods = "\n".join(
        f'              <div class="method"><h3>{h}</h3><p>{t}</p></div>' for h, t in p["methods"]
    )
    insights = "\n".join(
        f'              <div class="insight"><span class="insight-n" aria-hidden="true">{i}</span><div><h3>{h}</h3><p>{t}</p>'
        + (f"<blockquote>“{q}”</blockquote>" if q else "")
        + "</div></div>"
        for i, (h, t, q) in enumerate(p["insights"], 1)
    )
    decisions = "\n".join(
        f'              <div class="decision"><h3>{h}</h3><p>{t}</p><p class="why"><b>Why:</b> {w}</p></div>'
        for h, t, w in p["decisions"]
    )

    def fig(kind, data):
        label, cap, body = data
        tag = "tag tag--after" if kind == "after" else "tag"
        return f"""              <figure>
                <span class="{tag}">{label}</span>
                <div class="screen" role="img" aria-label="{esc(label)}: {esc(cap)}">
                  <div class="screen-bar" aria-hidden="true"><i></i><i></i><i></i></div>
                  <div class="screen-body" aria-hidden="true">{body}</div>
                </div>
                <figcaption><b>{label}</b>{cap}</figcaption>
              </figure>"""

    compare = fig("before", p["before"]) + "\n" + fig("after", p["after"])
    outcomes = "\n".join(
        f'              <div class="outcome"><p class="big">{b}</p><p>{t}</p></div>' for b, t in p["outcomes"]
    )
    html = TEMPLATE.format(
        title=p["title"], lede=p["lede"], lede_attr=esc(p["lede"]), num=p["num"], case=p["case"],
        meta=meta, stage=stage(p["cls"]), tldr=tldr, problem=p["problem"], role=p["role"],
        role_pills=pills, methods=methods, insights=insights, decisions=decisions,
        compare=compare, outcomes=outcomes, reflection=p["reflection"],
        next_slug=p["next_slug"], next_title=p["next_title"], next_bg=p["next_bg"],
    )
    out = ROOT / "work" / f"{p['slug']}.html"
    out.write_text(html)
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    for p in PROJECTS:
        build(p)
