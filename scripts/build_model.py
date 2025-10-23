from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('.')

# Input assumptions
spot_volume_b = 284.0
deriv_volume_b = 150.0
retail_pct = 0.18
blended_take_bps = 23.0
bear_vol_delta = -0.15
bull_vol_delta = 0.12
bear_take_delta = -0.20
bull_take_delta = 0.08
usdc_supply_b = 67.26
short_rate_pct = 4.29
usdc_share = 0.50
usdc_haircut_bps = 45
staked_aum_b = 60.0
net_staking_yield_pct = 4.0
staking_take_pct = 0.25
custody_auc_b = 245.7
custody_fee_bps = 4.0
other_ss_baseline_m = 120.0
interest_finance_m = 70.0
other_revenue_m = 80.0
bear_ss_delta = -0.12
bull_ss_delta = 0.06
bear_other_delta = -0.15
bull_other_delta = 0.08
base_weight = 0.6
bear_weight = 0.2
bull_weight = 0.2

q2_txn_m = 764.27
q2_total_m = 1497.208

# Scenario helper
def scenario_values(vol_delta, take_delta, ss_delta, other_delta):
    spot_vol = spot_volume_b * (1 + vol_delta)
    deriv_vol = deriv_volume_b * (1 + vol_delta)
    total_vol_b = spot_vol + deriv_vol
    take_bps = blended_take_bps * (1 + take_delta)
    take_dec = take_bps / 10000
    txn_rev_m = total_vol_b * take_dec * 1000

    residual_rate_pct = short_rate_pct - (usdc_haircut_bps / 100)
    usdc_rev_m = usdc_supply_b * (residual_rate_pct / 100) / 4 * usdc_share * 1000 * (1 + ss_delta)

    staking_rev_m = staked_aum_b * (net_staking_yield_pct / 100) / 4 * staking_take_pct * 1000 * (1 + ss_delta)
    custody_rev_m = custody_auc_b * (custody_fee_bps / 10000) / 4 * 1000 * (1 + ss_delta)
    interest_rev_m = interest_finance_m * (1 + ss_delta)
    other_ss_rev_m = other_ss_baseline_m * (1 + ss_delta)

    ss_total_m = usdc_rev_m + staking_rev_m + custody_rev_m + interest_rev_m + other_ss_rev_m
    other_rev_m = other_revenue_m * (1 + other_delta)
    total_rev_m = txn_rev_m + ss_total_m + other_rev_m

    return {
        'spot_vol_b': spot_vol,
        'deriv_vol_b': deriv_vol,
        'total_vol_b': total_vol_b,
        'take_bps': take_bps,
        'take_dec': take_dec,
        'txn_rev_m': txn_rev_m,
        'usdc_rev_m': usdc_rev_m,
        'staking_rev_m': staking_rev_m,
        'custody_rev_m': custody_rev_m,
        'interest_rev_m': interest_rev_m,
        'other_ss_rev_m': other_ss_rev_m,
        'ss_total_m': ss_total_m,
        'other_rev_m': other_rev_m,
        'total_rev_m': total_rev_m,
    }

base = scenario_values(0.0, 0.0, 0.0, 0.0)
bear = scenario_values(bear_vol_delta, bear_take_delta, bear_ss_delta, bear_other_delta)
bull = scenario_values(bull_vol_delta, bull_take_delta, bull_ss_delta, bull_other_delta)

weighted_total_m = (
    base['total_rev_m'] * base_weight
    + bear['total_rev_m'] * bear_weight
    + bull['total_rev_m'] * bull_weight
)
weighted_txn_m = (
    base['txn_rev_m'] * base_weight
    + bear['txn_rev_m'] * bear_weight
    + bull['txn_rev_m'] * bull_weight
)
weighted_ss_m = (
    base['ss_total_m'] * base_weight
    + bear['ss_total_m'] * bear_weight
    + bull['ss_total_m'] * bull_weight
)
weighted_other_m = (
    base['other_rev_m'] * base_weight
    + bear['other_rev_m'] * bear_weight
    + bull['other_rev_m'] * bull_weight
)

rows = [["" for _ in range(8)] for _ in range(240)]

def set_cell(row: int, col: int, value):
    rows[row-1][col-1] = value

# Header
set_cell(1,1,"Company")
set_cell(1,2,"Coinbase Global, Inc.")
set_cell(2,1,"Report")
set_cell(2,2,"Q3'25 Revenue Forecast")
set_cell(3,1,"Date")
set_cell(3,2,datetime.now(timezone.utc).date().isoformat())
set_cell(4,1,"Author")
set_cell(4,2,"Karthik Kallam")

# Inputs
set_cell(10,1,"Inputs (edit cells in column B)")
set_cell(10,2,"Value")
set_cell(10,3,"Units / guidance")

inputs = [
    (11, "Spot volume", spot_volume_b, "$B spot (CryptoCompare Jul-Sep; Sep 24-30 inferred)"),
    (12, "Derivatives volume", deriv_volume_b, "$B effective notional (inferred)"),
    (13, "Retail share", retail_pct, "Decimal"),
    (14, "Blended take rate", blended_take_bps, "bps blended"),
    (15, "Bear volume delta", bear_vol_delta, "Decimal vs base"),
    (16, "Bull volume delta", bull_vol_delta, "Decimal vs base"),
    (17, "Bear take delta", bear_take_delta, "Decimal"),
    (18, "Bull take delta", bull_take_delta, "Decimal"),
    (19, "Avg USDC supply", usdc_supply_b, "$B (CoinGecko mkt cap proxy)"),
    (20, "Avg short rate", short_rate_pct, "% (FRED DGS3MO avg)"),
    (21, "USDC share", usdc_share, "Decimal Coinbase share of residual"),
    (22, "USDC haircut", usdc_haircut_bps, "bps off short rate"),
    (23, "ETH staked AUM", staked_aum_b, "$B inferred from Q2"),
    (24, "Net staking yield", net_staking_yield_pct, "% annual"),
    (25, "Staking take %", staking_take_pct, "Decimal"),
    (26, "Custody AUC", custody_auc_b, "$B avg"),
    (27, "Custody fee", custody_fee_bps, "bps annual"),
    (28, "Other S&S baseline", other_ss_baseline_m, "$M"),
    (29, "Interest & finance baseline", interest_finance_m, "$M"),
    (30, "Other revenue baseline", other_revenue_m, "$M"),
    (31, "Bear S&S delta", bear_ss_delta, "Decimal"),
    (32, "Bull S&S delta", bull_ss_delta, "Decimal"),
    (33, "Bear other delta", bear_other_delta, "Decimal"),
    (34, "Bull other delta", bull_other_delta, "Decimal"),
    (35, "Base weight", base_weight, "Probability"),
    (36, "Bear weight", bear_weight, "Probability"),
    (37, "Bull weight", bull_weight, "Probability"),
]

for row, label, val, note in inputs:
    set_cell(row,1,label)
    set_cell(row,2,str(val))
    set_cell(row,3,note)

set_cell(38,1,"Weight sum check")
set_cell(38,2,"=B35+B36+B37")
set_cell(38,3,"Should equal 1.0")

# Drivers header
set_cell(10,4,"Drivers")
set_cell(10,5,"Base")
set_cell(10,6,"Bear")
set_cell(10,7,"Bull")
set_cell(10,8,"Units / notes")

drivers = [
    (11, "Spot volume ($B)", "=B11", "=B11*(1+$B$15)", "=B11*(1+$B$16)", "CryptoCompare"),
    (12, "Derivatives volume ($B)", "=B12", "=B12*(1+$B$15)", "=B12*(1+$B$16)", "Effective notional"),
    (13, "Total traded volume ($B)", "=E11+E12", "=F11+F12", "=G11+G12", "Spot + derivatives"),
    (14, "Retail mix %", "=B13", "=B13", "=B13", "Input"),
    (15, "Blended take rate (bps)", "=B14", "=B14*(1+$B$17)", "=B14*(1+$B$18)", "Input +/- deltas"),
    (16, "Blended take rate (decimal)", "=E15/10000", "=F15/10000", "=G15/10000", "bps/10,000"),
    (17, "Transaction revenue ($M)", "=E13*E16*1000", "=F13*F16*1000", "=G13*G16*1000", "TxnRev formula"),
    (18, "Residual rate (%)", "=$B$20-($B$22/100)", "=$B$20-($B$22/100)", "=$B$20-($B$22/100)", "Short rate less haircut"),
    (19, "USDC interest ($M)", "=$B$19*(E18/100)/4*$B$21*1000", "=E19*(1+$B$31)", "=E19*(1+$B$32)", "Coinbase share"),
    (20, "Staking revenue ($M)", "=$B$23*($B$24/100)/4*$B$25*1000", "=E20*(1+$B$31)", "=E20*(1+$B$32)", "ETH staking"),
    (21, "Custody revenue ($M)", "=$B$26*($B$27/10000)/4*1000", "=E21*(1+$B$31)", "=E21*(1+$B$32)", "AUC x fee"),
    (22, "Interest & finance ($M)", "=$B$29", "=E22*(1+$B$31)", "=E22*(1+$B$32)", "Prime financing"),
    (23, "Other S&S ($M)", "=$B$28", "=E23*(1+$B$31)", "=E23*(1+$B$32)", "Other services"),
    (24, "Subscription & Services ($M)", "=SUM(E19:E23)", "=SUM(F19:F23)", "=SUM(G19:G23)", "USDC+Staking+Custody+Other"),
    (25, "Other revenue ($M)", "=$B$30", "=$B$30*(1+$B$33)", "=$B$30*(1+$B$34)", "Corporate interest etc."),
    (26, "Total revenue ($M)", "=E17+E24+E25", "=F17+F24+F25", "=G17+G24+G25", "Sum"),
    (27, "Weighted contribution ($M)", "=E26*$B$35", "=F26*$B$36", "=G26*$B$37", "Scenario weight"),
    (28, "Prob-weighted total ($M)", "=SUM(E27:G27)", "", "", "Probability weighted"),
    (29, "Implied take rate (bps)", "=IF(E13>0,E17/(E13*1000)*10000,0)", "=IF(F13>0,F17/(F13*1000)*10000,0)", "=IF(G13>0,G17/(G13*1000)*10000,0)", "Check vs input"),
    (30, "Txn vs Q2 delta %", f"=IF({q2_txn_m}>0,(E17-{q2_txn_m})/{q2_txn_m},0)", f"=IF({q2_txn_m}>0,(F17-{q2_txn_m})/{q2_txn_m},0)", f"=IF({q2_txn_m}>0,(G17-{q2_txn_m})/{q2_txn_m},0)", "QoQ growth"),
    (31, "Total vs Q2 delta %", f"=IF({q2_total_m}>0,(E26-{q2_total_m})/{q2_total_m},0)", f"=IF({q2_total_m}>0,(F26-{q2_total_m})/{q2_total_m},0)", f"=IF({q2_total_m}>0,(G26-{q2_total_m})/{q2_total_m},0)", "QoQ growth"),
]

for row, label, base_f, bear_f, bull_f, note in drivers:
    set_cell(row,4,label)
    if base_f:
        set_cell(row,5,base_f)
    if bear_f:
        set_cell(row,6,bear_f)
    if bull_f:
        set_cell(row,7,bull_f)
    set_cell(row,8,note)

# Forecast table
set_cell(45,1,"Forecast by Category")
set_cell(46,1,"Category")
set_cell(46,2,"Base ($M)")
set_cell(46,3,"Bear ($M)")
set_cell(46,4,"Bull ($M)")
set_cell(46,5,"Prob-weighted ($M)")
set_cell(46,6,"Q2'25 actual ($M)")
set_cell(46,7,"Δ vs Q2 (Base)")
set_cell(46,8,"Notes")

forecast_rows = [
    (47, "Transaction Revenue", "=E17", "=F17", "=G17", "=SUMPRODUCT(B35:B37,B47:D47)", q2_txn_m, "=B47-F47", "Volumes & take"),
    (48, " - Spot volume ($B)", "=E11", "=F11", "=G11", "=SUMPRODUCT(B35:B37,E11:G11)", 237.0, "=B48-F48", "CryptoCompare"),
    (49, " - Derivatives volume ($B)", "=E12", "=F12", "=G12", "=SUMPRODUCT(B35:B37,E12:G12)", 0.0, "=B49-F49", "Effective notional"),
    (50, " - Blended take rate (bps)", "=E15", "=F15", "=G15", "=SUMPRODUCT(B35:B37,E15:G15)", blended_take_bps, "=B50-F50", ""),
    (52, "Subscription & Services", "=E24", "=F24", "=G24", "=SUMPRODUCT(B35:B37,E24:G24)", 655.826, "=B52-F52", "USDC + staking + custody"),
    (53, " - USDC interest", "=E19", "=F19", "=G19", "=SUMPRODUCT(B35:B37,E19:G19)", 332.497, "=B53-F53", ""),
    (54, " - Staking revenue", "=E20", "=F20", "=G20", "=SUMPRODUCT(B35:B37,E20:G20)", 144.535, "=B54-F54", ""),
    (55, " - Custody fees", "=E21", "=F21", "=G21", "=SUMPRODUCT(B35:B37,E21:G21)", 119.478, "=B55-F55", "Record inflows"),
    (56, " - Interest & finance", "=E22", "=F22", "=G22", "=SUMPRODUCT(B35:B37,E22:G22)", 59.316, "=B56-F56", "Prime financing"),
    (57, " - Other S&S", "=E23", "=F23", "=G23", "=SUMPRODUCT(B35:B37,E23:G23)", 119.478, "=B57-F57", "Onchain services"),
    (60, "Other Revenue", "=E25", "=F25", "=G25", "=SUMPRODUCT(B35:B37,E25:G25)", 77.112, "=B60-F60", "Corporate interest"),
    (62, "Total Revenue", "=E26", "=F26", "=G26", "=SUMPRODUCT(B35:B37,E26:G26)", q2_total_m, "=B62-F62", ""),
]

for row, label, base_f, bear_f, bull_f, weighted_f, q2_val, delta_f, note in forecast_rows:
    set_cell(row,1,label)
    set_cell(row,2,base_f)
    set_cell(row,3,bear_f)
    set_cell(row,4,bull_f)
    set_cell(row,5,weighted_f)
    set_cell(row,6,str(q2_val))
    set_cell(row,7,delta_f)
    set_cell(row,8,note)

# Sanity checks
set_cell(85,1,"Sanity Checks")
san_checks = [
    (86, "Scenario weights sum", "=B35+B36+B37", "Should equal 1"),
    (87, "Prob-weighted (drivers)", "=E28", ""),
    (88, "Prob-weighted (table)", "=B62*$B$35+C62*$B$36+D62*$B$37", "Cross-check"),
    (89, "Implied take vs input (bps)", "=B29-$B$14", "Base minus input"),
    (90, "Take rate drift vs hist avg", "=IF(ABS((B29-0.0032217)*10000)>6,\"Review\",\"OK\")", "Flag if >60 bps shift"),
    (91, "Modeled total vs Q2 delta %", "=B31", "QoQ change"),
]
for row, label, formula, note in san_checks:
    set_cell(row,1,label)
    set_cell(row,2,formula)
    set_cell(row,3,note)

# Sensitivity table (transaction only)
set_cell(115,1,"Sensitivity: Total Revenue ($M)")
set_cell(117,1,"Volume change → / Take rate ↓")
labels = ["-20%", "-10%", "Base", "+10%", "+20%"]
for idx, lbl in enumerate(labels, start=2):
    set_cell(117,idx,lbl)

for ridx, row_label in enumerate(labels, start=118):
    label_text = row_label + (" *" if row_label == "Base" else "")
    set_cell(ridx,1,label_text)
    for cidx, col_label in enumerate(labels, start=2):
        def pct(label: str) -> float:
            return 0.0 if label == "Base" else float(label.rstrip('%'))/100
        vol_factor = 1 + pct(col_label)
        take_factor = 1 + pct(row_label)
        formula = (
            f"=($E$13*{vol_factor})*($E$16*{take_factor})*1000+$E$24+$E$25"
        )
        set_cell(ridx,cidx,formula)
set_cell(123,1,"* Base cell")

# Sources & notes
set_cell(165,1,"Sources & Notes")
sources = [
    "- CryptoCompare Coinbase spot volume JSON (https://min-api.cryptocompare.com/data/exchange/histoday?e=Coinbase&tsym=USD)",
    "- CoinGecko market chart range for BTC/ETH/USDC (https://api.coingecko.com/api/v3/coins/{asset}/market_chart/range)",
    "- FRED DGS3MO & FEDFUNDS CSV (https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES)",
    "- DefiLlama cbETH TVL (https://api.llama.fi/protocol/coinbase-wrapped-staked-eth)",
    "- Coinbase Q2'25 Shareholder Letter (local: Quarter 2/Q2-2025-Shareholder-Letter.pdf)",
    "- Coinbase Q1'25 Shareholder Letter (local: Quarter 1/Q1-25-Shareholder-Letter-1.pdf)",
]
row = 166
for item in sources:
    set_cell(row,1,item)
    row += 1

# Version log
set_cell(225,1,"Version Log")
set_cell(226,1,datetime.now(timezone.utc).date().isoformat())


# Write CSV
output_path = ROOT / 'output' / 'coinbase_q3_2025_model.csv'
with output_path.open('w', encoding='utf-8') as f:
    for row in rows:
        f.write(','.join(str(cell) for cell in row) + '\n')

# Summary JSON for downstream use
summary_path = ROOT / 'output' / 'model_summary.json'
with summary_path.open('w', encoding='utf-8') as f:
    import json
    json.dump({
        'base': base,
        'bear': bear,
        'bull': bull,
        'weights': {
            'base': base_weight,
            'bear': bear_weight,
            'bull': bull_weight,
        },
        'weighted': {
            'total_revenue_m': weighted_total_m,
            'transaction_m': weighted_txn_m,
            's_and_s_m': weighted_ss_m,
            'other_m': weighted_other_m,
        }
    }, f, indent=2)

print('Base total revenue (M):', round(base['total_rev_m'],2))
print('Bear total revenue (M):', round(bear['total_rev_m'],2))
print('Bull total revenue (M):', round(bull['total_rev_m'],2))
print('Probability-weighted total (M):', round(weighted_total_m,2))
