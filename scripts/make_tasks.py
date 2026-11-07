"""python scripts/make_tasks.py -> data/tasks.jsonl (deterministic; fixed seeds).

Eight synthetic tasks, two per trap. Companies and numbers are invented; each task copies the *structure*
of a real FinQA record (Chen et al., EMNLP 2021, MIT licence), so the answer cannot be recalled from the
original. Every answer comes from the reference solution written in the generator, never from FinQA's labels
(three FinQA labels we inspected were wrong). `slip` is the answer a model gets from the trap mistake.
"""
import json
import pathlib
import random

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "tasks.jsonl"
FINQA = "synthetic numbers; table structure adapted from FinQA record {} (MIT, Chen et al. 2021)"


def md(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(lines + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def task(tid, context, table, question, rule, answer, slip, trap, why, ref, src):
    assert answer != slip, tid
    prompt = (f"Below is an excerpt from a company annual report.\n\n{context}\n\n{table}\n\n"
              f"Question: {question}\n\nWork through the calculation, then end your reply with one final "
              f"line in exactly this form:\nANSWER: <number>\n{rule}")
    return {"id": tid, "prompt": prompt, "answer": answer, "grader": "numeric",
            "metadata": {"domain": "financial reports", "trap": trap, "difficulty": "medium",
                         "source": FINQA.format(src), "why_hard": why, "reference": ref, "slip": slip}}


def f2(x):
    return f"{x:.2f}"


def f1(x):
    return f"{x:.1f}"


def returns_task(tid, seed, company, idx, other, dates, col, src, trap_note):
    rng = random.Random(seed)

    def walk():
        v = [100.0]
        for _ in range(len(dates) - 1):
            v.append(round(v[-1] * (1 + rng.uniform(-0.08, 0.28)), 2))
        return v
    a, b, c = walk(), walk(), walk()
    fmt = lambda row: [f"$ {x:.2f}" for x in row]
    table = md([""] + dates, [[company] + fmt(a), [idx] + fmt(b), [other] + fmt(c)])
    ctx = (f"The graph assumes $100 was invested on {dates[0]} in {company} common stock and in each index, "
           f"with dividends reinvested. The table shows the value of each investment at each date.")
    q = (f"What was the difference, in percentage points, between {company}'s cumulative total return and the "
         f"{idx}'s cumulative total return for the period ended {dates[col]}?")
    rule = f"Give the number only, without a % sign, rounded to 2 decimals. Use a negative number if {company} is lower."
    ans = f2((a[col] - 100) - (b[col] - 100))
    slip = f2((a[col] / b[col] - 1) * 100) if col == len(dates) - 1 else f2(a[-1] - b[-1])
    return task(tid, ctx, table, q, rule, ans, slip, "pct-vs-points", trap_note,
                f"({a[col]} - 100) - ({b[col]} - 100) = {ans}", src)


def coal_share(tid, seed, src):
    rng = random.Random(seed)
    names = ["Grain and agricultural", "Vehicles", "Chemicals", "Coal", "Industrial products", "Intermodal"]
    years = ["2016", "2015", "2014"]
    cols = {n: [rng.randint(2000, 4500) for _ in years] for n in names}
    cols["Coal"] = [rng.randint(2300, 2700), rng.randint(3000, 3400), rng.randint(3900, 4300)]
    freight = [sum(cols[n][i] for n in names) for i in range(3)]
    other = [rng.randint(1200, 1500) for _ in years]
    total = [freight[i] + other[i] for i in range(3)]
    rows = [[n] + cols[n] for n in names] + [["Total freight revenues"] + freight,
                                              ["Other revenues"] + other, ["Total operating revenues"] + total]
    ctx = "Revenue by commodity group for Plains Pacific Railroad Corporation (amounts in millions of dollars)."
    q = "What percent of total operating revenues for 2014 through 2016 combined came from coal?"
    rule = "Give the number only, without a % sign, rounded to 2 decimals."
    ans = f2(sum(cols["Coal"]) / sum(total) * 100)
    slip = f2(sum(cols["Coal"]) / sum(freight) * 100)
    return task(tid, ctx, md(["millions"] + years, rows), q, rule, ans, slip, "lookup",
                "Total freight revenues and total operating revenues sit one row apart; the wrong denominator is a plausible slip.",
                f"sum(coal) / sum(total operating revenues) * 100 = {ans}", src)


def mortgage_share(tid, seed, src):
    rng = random.Random(seed)
    cf = [rng.randint(1000, 1500), rng.randint(1200, 1700)]
    cl = [rng.randint(200, 300), rng.randint(600, 800)]
    rf = [rng.randint(900, 1100), rng.randint(1700, 1900)]
    rl = [rng.randint(0, 150), rng.randint(100, 200)]
    oth = [rng.randint(200, 260), rng.randint(230, 290)]
    ct, rt = [cf[i] + cl[i] for i in (0, 1)], [rf[i] + rl[i] for i in (0, 1)]
    tot = [ct[i] + rt[i] + oth[i] for i in (0, 1)]
    rows = [["Commercial mortgages at fair value"] + cf, ["Commercial mortgages at lower of cost or market"] + cl,
            ["Total commercial mortgages"] + ct, ["Residential mortgages at fair value"] + rf,
            ["Residential mortgages at lower of cost or market"] + rl, ["Total residential mortgages"] + rt,
            ["Other"] + oth, ["Total"] + tot]
    ctx = "Mortgage loans held for sale of Lakeshore Financial Corporation (in millions of dollars)."
    q = "At December 31, 2008, what percent of total commercial mortgages was carried at fair value?"
    rule = "Give the number only, without a % sign, rounded to 1 decimal."
    ans = f1(cf[1] / ct[1] * 100)
    slip = f1(cf[0] / ct[0] * 100)
    return task(tid, ctx, md(["in millions", "Dec. 31, 2009", "Dec. 31, 2008"], rows), q, rule, ans, slip,
                "lookup", "Eight similar rows and two year columns; the 2009 column or the wrong total row is an easy slip.",
                f"{cf[1]} / {ct[1]} * 100 = {ans}", src)


def tax_rollforward(tid, seed, src):
    rng = random.Random(seed)
    begin = rng.randint(250, 320)
    years, cols, b = ["2010", "2011", "2012"], {}, begin
    acq = {"2010": rng.randint(3, 6), "2011": 0, "2012": rng.randint(9, 14)}
    for y in years:
        add_p, red_p = rng.randint(4, 22), -rng.randint(1, 17)
        add_c, lapse, sett = rng.randint(35, 70), rng.choice([0, -8]), -rng.randint(2, 30)
        end = b + add_p + red_p + add_c + lapse + sett + acq[y]
        cols[y] = [b, add_p, red_p, add_c, lapse, sett, acq[y], end]
        b = end
    labels = ["Balance at January 1", "Additions for tax positions of prior years",
              "Reductions for tax positions of prior years", "Additions based on tax positions related to current year",
              "Lapse of statute of limitations", "Settlements", "Positions assumed in acquisitions", "Balance at December 31"]
    show = lambda v: "—" if v == 0 else v
    order = ["2012", "2011", "2010"]
    rows = [[labels[i]] + [show(cols[y][i]) for y in order] for i in range(8)]
    inc = cols["2012"][7] - cols["2010"][0]
    assert inc > 0
    ctx = ("Reconciliation of unrecognized tax benefits for Harbor Asset Management Inc. (amounts in millions of "
           "dollars). A dash means zero.")
    q = ("What percent of the net increase in the balance from January 1, 2010 to December 31, 2012 came from "
         "positions assumed in acquisitions? (Net increase = balance at December 31, 2012 minus balance at January 1, 2010.)")
    rule = "Give the number only, without a % sign, rounded to 2 decimals."
    tot_acq = sum(acq.values())
    ans = f2(tot_acq / inc * 100)
    slip = f2(tot_acq / cols["2012"][7] * 100)
    return task(tid, ctx, md(["(in millions)"] + [f"Year ended Dec. 31, {y}" for y in order], rows), q, rule, ans, slip,
                "multi-step", "Needs the span-start and span-end balances from different columns, acquisitions summed over three columns (one a dash), then a ratio.",
                f"({acq['2010']} + {acq['2011']} + {acq['2012']}) / ({cols['2012'][7]} - {cols['2010'][0]}) * 100 = {ans}", src)


def amortization(tid, seed, src):
    rng = random.Random(seed)
    v = [rng.randint(60, 70)]
    for _ in range(4):
        v.append(max(8, v[-1] - rng.randint(4, 22)))
    y17 = rng.randint(70, 95)
    ctx = (f"Amortization expense for other intangible assets was approximately ${y17} million in 2017. The following "
           f"table presents estimated amortization expense for each of the five succeeding years. Management expects "
           f"2023 amortization expense to be 30% lower than the 2022 amount.")
    rows = [[y, v[i]] for i, y in enumerate(["2018", "2019", "2020", "2021", "2022"])]
    est23 = v[4] * 0.7
    q = ("Including the 2023 estimate, what percent of the total estimated amortization expense for 2018 through "
         "2023 is expected in 2019 and 2020 combined?")
    rule = "Give the number only, without a % sign, rounded to 1 decimal."
    ans = f1((v[1] + v[2]) / (sum(v) + est23) * 100)
    slip = f1((v[1] + v[2]) / sum(v) * 100)
    return task(tid, ctx, md(["For the years ending December 31", "(in millions)"], rows), q, rule, ans, slip,
                "multi-step", "The 2023 figure must be derived from text (70% of 2022) and added to the total before the ratio; skipping it is a plausible slip.",
                f"({v[1]} + {v[2]}) / ({sum(v)} + 0.7 * {v[4]}) * 100 = {ans}", src)


def debt_36(tid, seed, src):
    rng = random.Random(seed)
    amt = [rng.randint(250000, 1200000) for _ in range(5)]
    rows = [[str(2014 + i), f"$ {amt[i]}"] for i in range(5)]
    ctx = "Annual long-term debt maturities of Delta Valley Power Corporation as of December 31, 2013."
    q = "How much long-term debt, in millions of dollars, is due in the next 36 months?"
    rule = "Give the number only, without commas, rounded to 1 decimal."
    s = sum(amt[:3])
    ans = f1(s / 1000)
    return task(tid, ctx, md(["", "Amount (in thousands)"], rows), q, rule, ans, f1(s), "units",
                "The table is in thousands and the answer is asked in millions; leaving the scale unconverted is the slip.",
                f"({amt[0]} + {amt[1]} + {amt[2]}) / 1000 = {ans}", src)


def debt_24_mixed(tid, seed, src):
    rng = random.Random(seed)
    amt = [rng.randint(300000, 1000000) for _ in range(5)]
    extra = rng.choice([120, 175, 240, 310])
    rows = [[str(2019 + i), f"$ {amt[i]}"] for i in range(5)]
    ctx = (f"Annual long-term debt maturities of Ridgeview Utilities Inc. as of December 31, 2018. In addition, "
           f"notes with a face value of ${extra} million fall due in 2020 and are not included in the table.")
    q = ("In millions of dollars, what is the total of all long-term debt due in the next 24 months (2019 and 2020), "
         "including the notes described in the text?")
    rule = "Give the number only, without commas, rounded to 1 decimal."
    s = amt[0] + amt[1]
    ans = f1(s / 1000 + extra)
    return task(tid, ctx, md(["", "Amount (in thousands)"], rows), q, rule, ans, f1(s / 1000), "units",
                "Table is in thousands, text is in millions; the notes in the text are easy to leave out or to add in the wrong unit.",
                f"({amt[0]} + {amt[1]}) / 1000 + {extra} = {ans}", src)


def build():
    d6 = ["12/31/2013", "12/31/2014", "12/31/2015", "12/31/2016", "12/31/2017", "12/31/2018"]
    return [
        returns_task("fin-pp-001", 11, "Cedar Systems Inc.", "Nasdaq composite", "S&P 400 information technology", d6, 5,
                     "CDNS/2015/page_30.pdf-3", "Index values start at 100, so return = value - 100; the difference is in points, and a ratio of values gives a different number."),
        returns_task("fin-pp-002", 12, "Meridian Freight Inc.", "Dow Jones transportation average", "S&P 500 index", d6, 3,
                     "UPS/2012/page_32.pdf-2", "The question asks about an earlier column than the last, and a third series is a distractor."),
        coal_share("fin-lk-001", 21, "UNP/2016/page_52.pdf-3"),
        mortgage_share("fin-lk-002", 22, "PNC/2009/page_41.pdf-4"),
        tax_rollforward("fin-ms-001", 31, "BLK/2012/page_160.pdf-2"),
        amortization("fin-ms-002", 32, "HUM/2017/page_118.pdf-3"),
        debt_36("fin-un-001", 41, "ETR/2013/page_118.pdf-2"),
        debt_24_mixed("fin-un-002", 42, "ETR/2013/page_118.pdf-2 (plus a text amount in a different unit)"),
    ]


if __name__ == "__main__":
    tasks = build()
    OUT.write_text("\n".join(json.dumps(t, ensure_ascii=False) for t in tasks) + "\n", encoding="utf-8")
    for t in tasks:
        print(t["id"], t["answer"], "(slip", t["metadata"]["slip"] + ")")
