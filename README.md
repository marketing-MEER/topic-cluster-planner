<div align="center">

# 🕸️ topic-cluster-planner

### Turn a flat keyword list into pillar and spoke pages, with an internal link plan and anchor texts.

[![tests](https://github.com/marketing-MEER/topic-cluster-planner/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/topic-cluster-planner/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![Part of SEO Toolbox](https://img.shields.io/badge/part%20of-SEO%20Toolbox-orange)](https://github.com/marketing-MEER/seo-toolbox)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#quick-start) · [⚙️ How it works](#how-it-works) · [📄 Report](#report) · [❓ FAQ](#faq) · [👤 Author](#author)

</div>

---

## 💡 What it does

A flat keyword list doesn't tell you which pages to build or how they should link. Turning it into topic clusters by hand means sorting hundreds of rows into groups and then drawing the links.

`topic-cluster-planner` reads a keyword CSV and gives you the plan: pillar pages for core topics, spoke pages for their sub-topics, sections that belong on an existing page, standalone pages for small topics, and an internal link plan with anchor texts.

- ✅ Pillar, spoke, section and standalone roles with a suggested URL for every keyword
- ✅ An internal link plan: pillar to spokes, spokes to pillar, spokes to their biggest siblings
- ✅ Each cluster's volume and the share in keywords of 3+ words
- ✅ Free, MIT licensed, no API keys. Works with the exports you already have.

## 📊 Why this matters

> **Topic-Focused SEO Performs Better in Tough Markets** · NP Digital, October 2025 (50 sites over 4 years)
> - 2023: Topic +18.7%, Keyword +2.5%.
> - 2024: Topic -3.3%, Keyword -18.1%.
> - 2025: Topic -12.7%, Keyword -21.6%.
> - Topic-focused content outperformed in all four years.
>
> **SEO Traffic Distribution by Keyword Length** · NP Digital, January 2024 (579,240 leads)
> - Keywords with 3 to 6 words drive 57.31% of SEO traffic.
> - Short keywords with 1 to 2 words generate only 18.43% of traffic.
>
> Data: [topic vs keyword SEO](https://neilpatel.com/marketing-stats/keyword-vs-topic-seo-performance/) · [traffic by keyword length](https://neilpatel.com/marketing-stats/seo-traffic-by-keyword-length/)

**How topic-cluster-planner uses this:** the insights are *"switch from keyword-first to topic-first content planning"*, *"cluster related content around core themes"* and *"use internal linking to reinforce topic authority"*. Those are the three outputs: clusters, a page plan and a link plan. The length data is why the cluster table shows the share of 3+ word keywords: they are usually the spokes, and they carry most of the traffic.

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/topic-cluster-planner.git
cd topic-cluster-planner
pip install -e .
topic-cluster-planner examples/coffee_keywords.csv
```

This writes **`topic_clusters.html`** (a formatted report you can open, share or print to PDF) and **`topic_clusters.xlsx`** (clusters, page plan and link plan).

> [!TIP]
> If the `topic-cluster-planner` command isn't found, use `python -m topic_cluster_planner`.

## 📥 Input

Any keyword CSV. The keyword column is found by name (`Keyword`, `Query`, `Top queries`, `Search term`), else the first column is used. Volume comes from `Volume`, `Search Volume`, `Avg. monthly searches` or `Impressions`. Works with Ahrefs, Semrush, Keyword Planner and Search Console exports.

<a id="how-it-works"></a>

## ⚙️ How it works

1. **Words**: each keyword is cut into words; small words (how, to, the, best, vs, make...) are dropped and plurals made singular. "How to make cold brews" becomes {cold, brew}.
2. **Parent**: keywords are read shortest first. A keyword's parent is the earlier keyword whose words it contains completely; when several fit, the most specific one (most words, then highest volume). "cold brew concentrate ratio" → parent "cold brew ratio" → parent "cold brew".
3. **Roles**:

| Role | Rule | What to build |
|---|---|---|
| pillar | Top keyword of a topic with at least `--min-spokes` children (default 2) | Hub page that covers the topic broadly and links to every spoke |
| spoke | Direct child of a pillar | Its own page, linked to and from the pillar |
| section | Child of a spoke (or of a small topic) | An H2 or FAQ on the page in the `page` column |
| standalone | Topic with fewer than `--min-spokes` children | One page; its children are sections on it |

4. **Link plan**: pillar → every spoke (anchor = spoke keyword), every spoke → pillar (anchor = pillar keyword), and each spoke → its two biggest siblings.

### Options

| Option | Default | What it does |
|---|---|---|
| `--min-spokes` | `2` | Spokes a topic needs to become a pillar |
| `-o`, `--output` | `topic_clusters` | File name for the report (`.html` + `.xlsx`) |

<a id="report"></a>

## 📄 The report

| Section / Excel sheet | Shows |
|---|---|
| Summary cards | Keywords, pillar pages, spoke pages, sections, standalone pages, internal links |
| Benchmark panels | The two NP Digital studies behind the plan |
| **Clusters** | Each topic with its pillar URL, keywords, spokes, sections, volume and share of 3+ word volume |
| **Page plan** | Every keyword with its cluster, role, parent and the page it lives on |
| **Link plan** | From page, to page, anchor text and the reason for each link |

<details>
<summary>📄 Example: real output from <code>examples/</code> (fictional coffee keywords)</summary>

**Clusters**

| cluster | pillar page | keywords | spokes | sections | volume | share 3 plus words pct | type |
|---|---|---|---|---|---|---|---|
| cold brew | /cold-brew/ | 6 | 4 | 1 | 137,700 | 34.3 | pillar + spokes |
| espresso machine | /espresso-machine/ | 7 | 5 | 1 | 102,280 | 27.6 | pillar + spokes |
| french press | /french-press/ | 3 | 2 | 0 | 54,700 | 9.5 | pillar + spokes |
| coffee grinder | /coffee-grinder/ | 3 | 2 | 0 | 50,500 | 19.8 | pillar + spokes |
| moka pot | /moka-pot/ | 1 | 0 | 0 | 33,100 | 0 | standalone page |
| pour over coffee | /pour-over-coffee/ | 3 | 2 | 0 | 24,900 | 100 | pillar + spokes |

**Page plan (cold brew)**

| keyword | volume | role | page |
|---|---|---|---|
| cold brew | 90,500 | pillar | /cold-brew/ |
| how to make cold brew | 22,200 | spoke | /how-to-make-cold-brew/ |
| cold brew maker | 9,900 | spoke | /cold-brew-maker/ |
| cold brew ratio | 8,100 | spoke | /cold-brew-ratio/ |
| cold brew vs iced coffee | 5,400 | spoke | /cold-brew-vs-iced-coffee/ |
| cold brew concentrate ratio | 1,600 | section | /cold-brew-ratio/ |

**Link plan (first rows, 54 links in total)**

| from page | to page | anchor | why |
|---|---|---|---|
| /cold-brew/ | /how-to-make-cold-brew/ | how to make cold brew | Pillar links down to every spoke |
| /how-to-make-cold-brew/ | /cold-brew/ | cold brew | Every spoke links up to the pillar |
| /how-to-make-cold-brew/ | /cold-brew-maker/ | cold brew maker | Sibling link to a big spoke in the same cluster |

</details>

## 🧰 More free SEO tools

This repo is one tool in the **[SEO Toolbox](https://github.com/marketing-MEER/seo-toolbox)**, a family of free, single-purpose SEO tools. Related:
- [keyword-mapper](https://github.com/marketing-MEER/keyword-mapper): match the plan against the pages you already have
- [question-keyword-miner](https://github.com/marketing-MEER/question-keyword-miner): find the questions to answer in each cluster
- [keyword-cannibalization-detector](https://github.com/marketing-MEER/keyword-cannibalization-detector): check that cluster pages don't compete
- [seo-workhorse](https://github.com/marketing-MEER/seo-workhorse): audit, clustering, redirects and GSC quick wins in one CLI

<a id="faq"></a>

## ❓ FAQ

<details><summary><b>Why word matching and not SERP or AI clustering?</b></summary>

It is free, instant, works offline and every grouping can be explained: a keyword sits under its parent because it contains all of the parent's words. SERP clustering is more accurate for synonyms ("cheap" vs "budget"), so check the standalone pages by hand: some of them may belong in a cluster.
</details>

<details><summary><b>Should every spoke really be its own page?</b></summary>

Not always. If two spokes would answer the same question, keep them on one page. The plan is a starting point; run [keyword-mapper](https://github.com/marketing-MEER/keyword-mapper) with your existing pages to see what is already covered.
</details>

<details><summary><b>Is my data sent anywhere?</b></summary>

No. It reads your CSV and writes the report on your computer. It makes no network requests.
</details>

## 🧪 Tests

```bash
python -m unittest discover -s tests -t . -v
```

## 📄 License

[MIT](LICENSE). Free for personal and commercial use. Benchmark figures © their original publishers and quoted with a link to the source.

<a id="author"></a>

## 👤 Author

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪
10+ years in SEO, AEO and GEO. I build small tools that take the spreadsheet work out of SEO.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

<div align="center">

**If this saved you time, a ⭐ helps other SEOs find it.**

</div>
