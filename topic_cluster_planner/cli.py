"""Command line entry point: `topic-cluster-planner KEYWORDS.csv`."""
from pathlib import Path

import click

from . import __version__, core
from .benchmark import STATS
from .report import Report, write_excel


@click.command()
@click.argument("keywords_file", type=click.Path(exists=True))
@click.option("--min-spokes", default=core.MIN_SPOKES, show_default=True,
              help="Spokes a topic needs to become a pillar; smaller topics become one standalone page.")
@click.option("-o", "--output", default="topic_clusters", show_default=True,
              help="Report name; writes <name>.html and <name>.xlsx")
@click.version_option(__version__)
def main(keywords_file, min_spokes, output):
    """Group the keywords in KEYWORDS_FILE into pillar + spoke pages and write an internal link plan.

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """
    p, cl, links = core.analyze(keywords_file, min_spokes)
    roles = p["role"].value_counts()
    report = Report(title="Topic cluster plan", subtitle=f"{Path(keywords_file).name} · {len(p):,} keywords",
                    tool="topic-cluster-planner")
    report.add_cards([
        ("Keywords", len(p)),
        ("Pillar pages", int(roles.get("pillar", 0)), "good"),
        ("Spoke pages", int(roles.get("spoke", 0)), "good"),
        ("Sections (H2/FAQ)", int(roles.get("section", 0))),
        ("Standalone pages", int(roles.get("standalone", 0)), "warn"),
        ("Internal links", len(links)),
    ])
    report.add_benchmark(STATS[0], how_used="Keywords are planned as topics: one pillar page per core theme, spoke "
                         "pages for its sub-topics, and the link plan follows the insight 'use internal linking to "
                         "reinforce topic authority'.")
    report.add_benchmark(STATS[1], how_used="The cluster table shows how much of each topic's volume sits in "
                         "keywords of 3+ words, the length NP Digital found drives most SEO traffic. Those are "
                         "usually your spokes.")
    report.add_table("Clusters", cl, sheet="Clusters", note="Sorted by total volume. Page URLs are suggestions.")
    report.add_table("Page plan", p, sheet="Page plan",
                     note="Pillar = hub page for the topic. Spoke = its own page linked to the pillar. "
                          "Section = an H2 or FAQ on the page in the 'page' column. Standalone = topic too small "
                          "for a cluster, one page.")
    report.add_table("Internal link plan", links, sheet="Link plan",
                     note="Pillar to every spoke, every spoke to the pillar, and each spoke to its biggest siblings.")

    html_path = report.save_html(Path(output).with_suffix(".html"))
    xlsx_path = write_excel(report.sheets, Path(output).with_suffix(".xlsx"))
    click.secho(f"Report: {html_path}\nData:   {xlsx_path}", fg="green", bold=True)
    click.echo(cl[["cluster", "keywords", "spokes", "volume", "type"]].to_string(index=False))


if __name__ == "__main__":
    main()
