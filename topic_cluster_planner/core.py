"""Turn a keyword list into pillar + spoke pages with an internal link plan.

Keywords are cut into words (small words dropped, plurals made singular) and sorted shortest first.
Each keyword's parent is the earlier keyword whose words it contains completely, choosing the most
specific one. Keywords with no parent start a cluster (the pillar), their children are spokes, and
deeper keywords become sections on the spoke page they belong to.

Why topics: NP Digital found topic-focused sites beat keyword-focused sites in all four years
(2025: topic -12.7% vs keyword -21.6%), with the insight "cluster related content around core themes"
and "use internal linking to reinforce topic authority".
Source: https://neilpatel.com/marketing-stats/keyword-vs-topic-seo-performance/
"""
import re

import pandas as pd

from .report import find_column, to_number

STOPWORDS = {"a", "an", "and", "the", "for", "to", "of", "in", "on", "with", "by", "at", "or", "is", "are", "what",
             "how", "why", "when", "where", "which", "who", "your", "you", "my", "me", "i", "it", "do", "does", "can",
             "should", "from", "that", "this", "vs", "versus", "best", "top", "good", "make"}
MIN_SPOKES = 2          # a pillar needs at least this many spokes, else the keyword is a standalone page
SIBLING_LINKS = 2       # each spoke links to this many sibling spokes (the biggest ones)

PLAN_COLS = ["cluster", "keyword", "volume", "words", "role", "parent", "page", "length"]
LINK_COLS = ["cluster", "from_page", "to_page", "anchor", "why"]


def _stem(word: str) -> str:
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 4 and word.endswith(("shes", "ches", "sses", "xes")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def tokens(text) -> frozenset:
    return frozenset(_stem(w) for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in STOPWORDS)


def length_bucket(words: int) -> str:
    # Buckets from NP Digital's traffic-by-length data (1-2, 3-6, 7+ words).
    return "1-2 words" if words <= 2 else "3-6 words" if words <= 6 else "7+ words"


def slug(text: str) -> str:
    return "/" + "-".join(re.findall(r"[a-z0-9]+", text.lower())) + "/"


def load(path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    kw = find_column(raw, ["keyword", "query", "top queries", "search term", "keywords"]) or raw.columns[0]
    vol = find_column(raw, ["volume", "search volume", "avg. monthly searches", "impressions"])
    df = pd.DataFrame({"keyword": raw[kw].astype(str).str.strip().str.lower(),
                       "volume": to_number(raw[vol]).astype(int) if vol else 0})
    return df[df["keyword"] != ""].drop_duplicates("keyword").reset_index(drop=True)


def build_tree(df: pd.DataFrame) -> dict:
    """{keyword: parent keyword or None}."""
    items = [(kw, int(v), tokens(kw)) for kw, v in zip(df["keyword"], df["volume"])]
    items = [i for i in items if i[2]]
    items.sort(key=lambda x: (len(x[2]), -x[1], x[0]))
    parent, seen = {}, []
    for kw, vol, tk in items:
        best = None
        for pkw, pvol, ptk in seen:
            if ptk < tk or (ptk == tk and pvol >= vol):   # parent's words all appear in this keyword
                if best is None or (len(ptk), pvol) > (len(best[2]), best[1]):
                    best = (pkw, pvol, ptk)
        parent[kw] = best[0] if best else None
        seen.append((kw, vol, tk))
    return parent


def plan(df: pd.DataFrame, min_spokes: int = MIN_SPOKES) -> pd.DataFrame:
    parent = build_tree(df)
    vol = dict(zip(df["keyword"], df["volume"]))
    children = {}
    for kw, p in parent.items():
        children.setdefault(p, []).append(kw)

    def root_of(kw):
        while parent[kw] is not None:
            kw = parent[kw]
        return kw

    rows = []
    for kw in parent:
        root = root_of(kw)
        n_spokes = len(children.get(root, []))
        depth, k = 0, kw
        while parent[k] is not None:
            k, depth = parent[k], depth + 1
        if n_spokes < min_spokes:
            # too small for a cluster: one page for the root keyword, the rest are sections on it
            role, page = ("standalone" if depth == 0 else "section"), slug(root)
        elif depth == 0:
            role, page = "pillar", slug(kw)
        elif depth == 1:
            role, page = "spoke", slug(kw)
        else:
            spoke = kw
            while parent[spoke] != root:
                spoke = parent[spoke]
            role, page = "section", slug(spoke)
        words = len(kw.split())
        rows.append({"cluster": root, "keyword": kw, "volume": vol[kw], "words": words, "role": role,
                     "parent": parent[kw] or "", "page": page, "length": length_bucket(words)})
    out = pd.DataFrame(rows, columns=PLAN_COLS)
    if out.empty:
        return out
    cv = out.groupby("cluster")["volume"].transform("sum")
    order = {"pillar": 0, "standalone": 0, "spoke": 1, "section": 2}
    out = out.assign(_cv=cv, _r=out["role"].map(order))
    return (out.sort_values(["_cv", "cluster", "_r", "volume"], ascending=[False, True, True, False])
            .drop(columns=["_cv", "_r"]).reset_index(drop=True))


def clusters(p: pd.DataFrame) -> pd.DataFrame:
    cols = ["cluster", "pillar_page", "keywords", "spokes", "sections", "volume", "share_3_plus_words_pct", "type"]
    if p.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    for name, g in p.groupby("cluster", sort=False):
        spokes = int((g["role"] == "spoke").sum())
        vol = int(g["volume"].sum())
        long_vol = int(g.loc[g["words"] >= 3, "volume"].sum())
        rows.append({"cluster": name, "pillar_page": slug(name), "keywords": len(g), "spokes": spokes,
                     "sections": int((g["role"] == "section").sum()), "volume": vol,
                     "share_3_plus_words_pct": round(long_vol / vol * 100, 1) if vol else 0.0,
                     "type": "pillar + spokes" if spokes else "standalone page"})
    return pd.DataFrame(rows, columns=cols)


def link_plan(p: pd.DataFrame, siblings: int = SIBLING_LINKS) -> pd.DataFrame:
    rows = []
    for name, g in p.groupby("cluster", sort=False):
        pillar = g[g["role"] == "pillar"]
        if pillar.empty:
            continue
        pillar_page, pillar_kw = pillar.iloc[0]["page"], pillar.iloc[0]["keyword"]
        spokes = g[g["role"] == "spoke"].sort_values("volume", ascending=False)
        for s in spokes.itertuples():
            rows.append({"cluster": name, "from_page": pillar_page, "to_page": s.page, "anchor": s.keyword,
                         "why": "Pillar links down to every spoke"})
            rows.append({"cluster": name, "from_page": s.page, "to_page": pillar_page, "anchor": pillar_kw,
                         "why": "Every spoke links up to the pillar"})
            for o in spokes[spokes["page"] != s.page].head(siblings).itertuples():
                rows.append({"cluster": name, "from_page": s.page, "to_page": o.page, "anchor": o.keyword,
                             "why": "Sibling link to a big spoke in the same cluster"})
    return pd.DataFrame(rows, columns=LINK_COLS)


def analyze(path, min_spokes=MIN_SPOKES):
    p = plan(load(path), min_spokes)
    return p, clusters(p), link_plan(p)
