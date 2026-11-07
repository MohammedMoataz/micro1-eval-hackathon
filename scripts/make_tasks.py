"""python scripts/make_tasks.py -> data/tasks.jsonl (deterministic; fixed seeds).

Eight synthetic tasks, two per trap. Companies and numbers are invented. Six tasks keep the *table shape*
of a real FinQA record (Chen et al., EMNLP 2021, MIT licence); two use original structures. Every answer
comes from the reference solution written here, never from FinQA's labels (three FinQA labels we inspected
were wrong). `slip` is the answer a model gets from the trap mistake; the grader must reject it.

Version 2 (harder): the v1 tasks were solved 8/8 by three models, so each task now needs a reading skill a
shortcut gets wrong: sub-period returns, CAGR, "of which" rows, restatements, a derived missing cell,
fiscal-to-calendar conversion, a text amount in a different unit, and average-vs-closing FX rates.
"""
import json
import pathlib
import random

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "tasks.jsonl"


def finqa(rec):
    return f"synthetic numbers; table shape adapted from FinQA record {rec} (MIT, Chen et al. 2021)"


ORIGINAL = "synthetic numbers; original table structure"


def md(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(lines + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def task(tid, context, table, question, rule, answer, slip, trap, why, ref, src):
    assert answer != slip, tid
    prompt = (f"Below is an excerpt from a company annual report.\n\n{context}\n\n{table}\n\n"
              f"Question: {question}\n\nWork through the calculation, then end your reply with one final "
              f"line in exactly this form:\nANSWER: <number>\n{rule}")
    assert answer not in prompt, tid  # no leak
    return {"id": tid, "prompt": prompt, "answer": answer, "grader": "numeric",
            "metadata": {"domain": "financial reports", "trap": trap, "difficulty": "hard",
                         "source": src, "why_hard": why, "reference": ref, "slip": slip}}


def f2(x):
    return f"{x:.2f}"


def walk(rng, n):
    v = [100.0]
    for _ in range(n - 1):
        v.append(round(v[-1] * (1 + rng.uniform(-0.12, 0.30)), 2))
    return v


D6 = ["12/31/2013", "12/31/2014", "12/31/2015", "12/31/2016", "12/31/2017", "12/31/2018"]


def returns_table(company, idx, other, a, b, c):
    fmt = lambda row: [f"$ {x:.2f}" for x in row]
    ctx = (f"The graph assumes $100 was invested on {D6[0]} in {company} common stock and in each index, "
           f"with dividends reinvested. The table shows the value of each investment at each date.")
    return ctx, md([""] + D6, [[company] + fmt(a), [idx] + fmt(b), [other] + fmt(c)])


def subperiod_returns(tid, seed):
    rng = random.Random(seed)
    company, idx, other = "Cedar Systems Inc.", "Nasdaq composite", "S&P 400 information technology"
    a, b, c = walk(rng, 6), walk(rng, 6), walk(rng, 6)
    ctx, table = returns_table(company, idx, other, a, b, c)
    q = (f"Over the three years from {D6[2]} to {D6[5]}, what was the difference, in percentage points, between "
         f"the total return of {company} and the total return of the {idx}?")
    rule = f"Give the number only, without a % sign, rounded to 2 decimals. Use a negative number if {company} is lower."
    ans = f2((a[5] / a[2] - b[5] / b[2]) * 100)
    slip = f2((a[5] - 100) - (b[5] - 100))
    return task(tid, ctx, table, q, rule, ans, slip, "pct-vs-points",
                "The window starts mid-table, so 'value - 100' (the shortcut that works from the $100 base) is wrong; "
                "each return must be end/start - 1.",
                f"({a[5]} / {a[2]} - {b[5]} / {b[2]}) * 100 = {ans}", finqa("CDNS/2015/page_30.pdf-3"))


def annualized_returns(tid, seed):
    rng = random.Random(seed)
    company, idx, other = "Meridian Freight Inc.", "Dow Jones transportation average", "S&P 500 index"
    a, b, c = walk(rng, 6), walk(rng, 6), walk(rng, 6)
    ctx, table = returns_table(company, idx, other, a, b, c)
    q = (f"What was the difference, in percentage points, between the compound annual growth rate of the "
         f"{company} investment and that of the {idx} investment over the five years from {D6[0]} to {D6[5]}?")
    rule = f"Give the number only, without a % sign, rounded to 2 decimals. Use a negative number if {company} is lower."
    cagr = lambda v: ((v[5] / 100) ** (1 / 5) - 1) * 100
    ans = f2(cagr(a) - cagr(b))
    slip = f2(((a[5] - 100) - (b[5] - 100)) / 5)
    return task(tid, ctx, table, q, rule, ans, slip, "pct-vs-points",
                "Annualized means compounding (5th root); dividing the cumulative point gap by 5 is the common shortcut.",
                f"((({a[5]}/100)^(1/5) - 1) - (({b[5]}/100)^(1/5) - 1)) * 100 = {ans}", finqa("UPS/2012/page_32.pdf-2"))


def of_which_rows(tid, seed):
    rng = random.Random(seed)
    years = ["2016", "2015", "2014"]
    parents = ["Agricultural products", "Automotive", "Chemicals", "Coal", "Industrial products", "Intermodal"]
    val = {p: [rng.randint(2000, 4500) for _ in years] for p in parents}
    subs = {"Chemicals": "of which: plastics", "Coal": "of which: export coal",
            "Industrial products": "of which: construction materials"}
    sub_val = {p: [round(x * rng.uniform(0.3, 0.6)) for x in val[p]] for p in subs}
    other = [rng.randint(1200, 1500) for _ in years]
    rows = []
    for p in parents:
        rows.append([p] + val[p])
        if p in subs:
            rows.append([subs[p]] + sub_val[p])
    rows.append(["Other revenues"] + other)
    ctx = ("Operating revenues of Plains Pacific Railroad Corporation (amounts in millions of dollars). Freight "
           "revenue is the revenue of the commodity groups; other revenues are not freight revenue.")
    q = ("What percent of freight revenue for 2014 through 2016 combined came from commodity groups other than coal "
         "and intermodal?")
    rule = "Give the number only, without a % sign, rounded to 2 decimals."
    keep = [p for p in parents if p not in ("Coal", "Intermodal")]
    num, den = sum(sum(val[p]) for p in keep), sum(sum(val[p]) for p in parents)
    ans = f2(num / den * 100)
    sub_keep, sub_all = sum(sum(sub_val[p]) for p in keep if p in subs), sum(sum(v) for v in sub_val.values())
    slip = f2((num + sub_keep) / (den + sub_all) * 100)
    return task(tid, ctx, md(["millions"] + years, rows), q, rule, ans, slip, "lookup",
                "No subtotal is given, so freight revenue must be summed by hand; 'of which' rows are already inside "
                "their parent line and adding them double-counts.",
                f"sum({', '.join(keep)}) over 3 years = {num}; / sum(all 6 groups) {den} * 100 = {ans}",
                finqa("UNP/2016/page_52.pdf-3"))


def restated_line(tid, seed):
    rng = random.Random(seed)
    cf = [rng.randint(1000, 1500), rng.randint(1200, 1700)]
    cl = [rng.randint(200, 300), rng.randint(600, 800)]
    rf = [rng.randint(900, 1100), rng.randint(1700, 1900)]
    rl = [rng.randint(0, 150), rng.randint(100, 200)]
    oth = [rng.randint(200, 260), rng.randint(230, 290)]
    ct, rt = [cf[i] + cl[i] for i in (0, 1)], [rf[i] + rl[i] for i in (0, 1)]
    tot = [ct[i] + rt[i] + oth[i] for i in (0, 1)]
    restated = cf[1] - rng.randint(150, 300)
    rows = [["Commercial mortgages at fair value"] + cf, ["Commercial mortgages at lower of cost or market"] + cl,
            ["Total commercial mortgages"] + ct, ["Residential mortgages at fair value"] + rf,
            ["Residential mortgages at lower of cost or market"] + rl, ["Total residential mortgages"] + rt,
            ["Other"] + oth, ["Total"] + tot]
    ctx = ("Mortgage loans held for sale of Lakeshore Financial Corporation (in millions of dollars). The table shows "
           f"amounts as originally reported. In 2009 the company restated one 2008 figure: commercial mortgages at fair "
           f"value at December 31, 2008 were ${restated} million. No other line item was restated; totals were "
           f"updated accordingly.")
    q = "Using the restated figures, what percent of total commercial mortgages at December 31, 2008 was carried at fair value?"
    rule = "Give the number only, without a % sign, rounded to 2 decimals."
    ans = f2(restated / (restated + cl[1]) * 100)
    slip = f2(cf[1] / ct[1] * 100)
    return task(tid, ctx, md(["in millions", "Dec. 31, 2009", "Dec. 31, 2008"], rows), q, rule, ans, slip,
                "lookup", "The restated number lives in the text and changes both numerator and the commercial total; "
                "reading the table as-is gives the originally reported share.",
                f"{restated} / ({restated} + {cl[1]}) * 100 = {ans}", finqa("PNC/2009/page_41.pdf-4"))


def derived_missing_cell(tid, seed):
    rng = random.Random(seed)
    years, cols, b = ["2010", "2011", "2012"], {}, rng.randint(250, 320)
    begin = b
    acq = {"2010": rng.randint(3, 6), "2011": 0, "2012": rng.randint(9, 14)}
    for y in years:
        add_p, red_p = rng.randint(4, 22), -rng.randint(1, 17)
        add_c, lapse, sett = rng.randint(35, 70), rng.choice([0, -8]), -rng.randint(8, 30)
        end = b + add_p + red_p + add_c + lapse + sett + acq[y]
        cols[y] = [b, add_p, red_p, add_c, lapse, sett, acq[y], end]
        b = end
    labels = ["Balance at January 1", "Additions for tax positions of prior years",
              "Reductions for tax positions of prior years", "Additions based on tax positions related to current year",
              "Lapse of statute of limitations", "Settlements", "Positions assumed in acquisitions", "Balance at December 31"]
    order = ["2012", "2011", "2010"]

    def cell(y, i):
        if y == "2011" and i == 5:
            return "n/a"
        return "—" if cols[y][i] == 0 else cols[y][i]
    rows = [[labels[i]] + [cell(y, i) for y in order] for i in range(8)]
    ctx = ("Reconciliation of unrecognized tax benefits for Harbor Asset Management Inc. (amounts in millions of "
           "dollars). A dash means zero. One figure was not available when this excerpt was prepared and is shown as "
           "n/a; every other figure, including all balances, is as reported.")
    q = ("What were total settlements over 2010, 2011 and 2012 combined, as a percent of the balance at January 1, "
         "2010? Treat settlements as a positive amount.")
    rule = "Give the number only, without a % sign, rounded to 2 decimals."
    sett = [-cols[y][5] for y in years]
    ans = f2(sum(sett) / begin * 100)
    slip = f2((sett[0] + sett[2]) / begin * 100)
    return task(tid, ctx, md(["(in millions)"] + [f"Year ended Dec. 31, {y}" for y in order], rows), q, rule, ans, slip,
                "multi-step", "The 2011 settlement must be derived from the roll-forward identity (end = start + all "
                "movements); treating n/a as zero or skipping it is the slip.",
                f"2011 settlement = {cols['2011'][7]} - ({' + '.join(str(cols['2011'][i]) for i in (0, 1, 2, 3, 4, 6))}) "
                f"= {-sett[1]}; ({' + '.join(map(str, sett))}) / {begin} * 100 = {ans}", finqa("BLK/2012/page_160.pdf-2"))


def fiscal_to_calendar(tid, seed):
    rng = random.Random(seed)
    fys = ["2019", "2020", "2021", "2022", "2023"]
    v = [rng.randint(60, 90)]
    for _ in range(4):
        v.append(max(8, v[-1] - rng.randint(5, 20)))
    ctx = ("Northgate Medical Devices Inc.'s fiscal year ends on September 30; fiscal 2020, for example, runs from "
           "October 1, 2019 to September 30, 2020. The table presents estimated amortization expense for other "
           "intangible assets by fiscal year.")
    q = ("Assuming the expense is incurred evenly across the months of each fiscal year, what is the estimated "
         "amortization expense for calendar year 2020 (January 1 to December 31, 2020), in millions of dollars?")
    rule = "Give the number only, rounded to 2 decimals."
    ans = f2(0.75 * v[1] + 0.25 * v[2])
    slip = f2(0.25 * v[1] + 0.75 * v[2])
    return task(tid, ctx, md(["Fiscal year", "(in millions)"], [[y, v[i]] for i, y in enumerate(fys)]), q, rule, ans,
                slip, "multi-step", "Calendar 2020 = 9 months of fiscal 2020 + 3 months of fiscal 2021; models often "
                "flip the weights or just report fiscal 2020.",
                f"0.75 * {v[1]} + 0.25 * {v[2]} = {ans}", finqa("HUM/2017/page_118.pdf-3") + "; fiscal-year shift is original")


def eps_mixed_units(tid, seed):
    rng = random.Random(seed)
    rev = [rng.randint(4000, 9000), rng.randint(4000, 9000)]
    ni = [rng.randint(300, 900), rng.randint(300, 900)]
    basic = [rng.randint(150000, 400000), rng.randint(150000, 400000)]
    dil = [x + rng.randint(2000, 9000) for x in basic]
    gain = rng.randint(25000, 90000)
    rows = [["Revenue"] + rev, ["Net income"] + ni, ["Weighted-average shares outstanding — basic"] + basic,
            ["Weighted-average shares outstanding — diluted"] + dil]
    ctx = ("Selected financial data of Brightwater Logistics Corp. (in millions of dollars, except share counts, which "
           f"are in thousands). Net income for 2019 includes a one-time gain on the sale of a warehouse of "
           f"${gain:,} thousand, before and after tax.")
    q = "What was 2019 diluted earnings per share, in dollars, excluding the one-time gain?"
    rule = "Give the number only, rounded to 2 decimals."
    ans = f2((ni[0] - gain / 1000) * 1000 / dil[0])
    slip = f2((ni[0] - gain / 1_000_000) * 1000 / dil[0])
    return task(tid, ctx, md(["", "2019", "2018"], rows), q, rule, ans, slip, "units",
                "Three scales in one excerpt (dollars in millions, shares in thousands, the gain in thousands of "
                "dollars); converting the gain as if it were in dollars leaves it almost unsubtracted.",
                f"({ni[0]} - {gain}/1000) * 1000 / {dil[0]} = {ans}", ORIGINAL)


def fx_average_rate(tid, seed):
    rng = random.Random(seed)
    rev = [rng.randint(80000, 150000), rng.randint(80000, 150000)]
    oi = [rng.randint(9000, 20000), rng.randint(9000, 20000)]
    assets = [rng.randint(200000, 350000), rng.randint(200000, 350000)]
    avg, close = round(rng.uniform(1.10, 1.18), 4), round(rng.uniform(1.04, 1.09), 4)
    rows = [["Revenue"] + rev, ["Operating income"] + oi, ["Total assets"] + assets]
    rates = md(["US dollars per euro", "2019", "2018"],
               [["Average rate for the year", avg, round(avg + 0.05, 4)],
                ["Rate at December 31", close, round(close + 0.06, 4)]])
    ctx = ("Lakeland GmbH, a subsidiary of Lakeland Holdings Inc., reports in euros (amounts below in thousands of "
           "euros). Group policy: income statement items are translated into US dollars at the average rate for the "
           "year; balance sheet items at the rate at the balance sheet date.")
    q = "What was Lakeland GmbH's 2019 operating income in millions of US dollars?"
    rule = "Give the number only, rounded to 2 decimals."
    ans = f2(oi[0] / 1000 * avg)
    slip = f2(oi[0] / 1000 * close)
    return task(tid, ctx, md(["EUR thousands", "2019", "2018"], rows) + "\n\n" + rates, q, rule, ans, slip, "units",
                "Two rate rows and two unit scales; translating an income item at the closing rate (the balance-sheet "
                "rule) is the slip.",
                f"{oi[0]} / 1000 * {avg} = {ans}", ORIGINAL)


def build():
    return [
        subperiod_returns("fin-pp-001", 11),
        annualized_returns("fin-pp-002", 12),
        of_which_rows("fin-lk-001", 21),
        restated_line("fin-lk-002", 22),
        derived_missing_cell("fin-ms-001", 31),
        fiscal_to_calendar("fin-ms-002", 32),
        eps_mixed_units("fin-un-001", 41),
        fx_average_rate("fin-un-002", 42),
    ]


if __name__ == "__main__":
    tasks = build()
    OUT.write_text("\n".join(json.dumps(t, ensure_ascii=False) for t in tasks) + "\n", encoding="utf-8")
    for t in tasks:
        print(t["id"], t["answer"], "(slip", t["metadata"]["slip"] + ")")
