"""
Final figure generation:
- Star bands regrouped (1–2★, 3★, 4★, 5★) with half-star note
- All figure suptitles removed (slide title already covers this)
- Applied to all 5 cities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

AGODA_RED    = '#E4272B'
AGODA_DARK   = '#1A1A2E'
AGODA_BLUE   = '#2E86AB'
AGODA_AMBER  = '#F4A261'
AGODA_GREEN  = '#2A9D8F'
AGODA_PURPLE = '#6C3483'
AGODA_GREY   = '#6B6B6B'
CITY_COLORS  = {'A':AGODA_RED,'B':AGODA_BLUE,'C':AGODA_AMBER,'D':AGODA_GREEN,'E':'#9B59B6'}
REVENUE_COLORS = {'A':AGODA_RED,'B':AGODA_PURPLE,'C':AGODA_AMBER,'D':AGODA_GREEN,'E':'#8B0000'}
CITY_NAMES = {
    'A':'City A — Urban Mixed Market',
    'B':'City B — Resort-Heavy Market',
    'C':'City C — Premium, Plans-Ahead Market',
    'D':'City D — Premium, Price-Stable Market',
    'E':'City E — Most Last-Minute Market',
}

plt.rcParams.update({
    'figure.facecolor':'white','axes.facecolor':'white','axes.edgecolor':'#CCCCCC',
    'axes.grid':True,'grid.alpha':0.35,'grid.color':'#CCCCCC',
    'font.family':'sans-serif','font.size':11,'axes.titlesize':13,'axes.titleweight':'bold',
})
OUT = '/home/claude/'

# ── LOAD ALL CITIES ───────────────────────────────────────────────────────────
dfs = {}
for c in ['A','B','C','D','E']:
    df = pd.read_excel(f'../data/City_{c}.xlsx')
    df['city'] = c
    if 'accommadation_type_name' in df.columns:
        df.rename(columns={'accommadation_type_name':'accommodation_type_name'}, inplace=True)
    df['lead_time']      = (df['checkin_date'] - df['booking_date']).dt.days
    df['length_of_stay'] = (df['checkout_date'] - df['checkin_date']).dt.days
    df['revenue_proxy']  = df['ADR_USD'] * df['length_of_stay']
    df = df[df['lead_time'] >= 0].copy()
    bins   = [-1,0,3,7,14,30,60]
    labels = ['Same-day\n(0d)','1–3 days','4–7 days','8–14 days','15–30 days','31–60 days']
    df['lead_bucket'] = pd.cut(df['lead_time'], bins=bins, labels=labels)
    # Grouped star bands (includes half-stars in the group)
    df['star_band'] = pd.cut(df['star_rating'],
        bins=[-0.5, 2.5, 3.5, 4.5, 5.5],
        labels=['1–2★\n(incl. 1.5★, 2★, 2.5★)', '3★\n(incl. 3.5★)',
                '4★\n(incl. 4.5★)', '5★'])
    dfs[c] = df
print("All cities loaded.")


def compute_star_summary(df):
    """Revenue vs booking share by grouped star band."""
    summary = df[df['star_band'].notna()].groupby('star_band', observed=True).agg(
        n_bookings=('ADR_USD','count'),
        total_revenue=('revenue_proxy','sum'),
        median_adr=('ADR_USD','median')
    ).reset_index()
    summary = summary[summary['n_bookings'] >= 5].copy()
    total_n   = summary['n_bookings'].sum()
    total_rev = summary['total_revenue'].sum()
    summary['booking_share'] = summary['n_bookings'] / total_n * 100
    summary['revenue_share'] = summary['total_revenue'] / total_rev * 100
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE REVENUE BY STAR (Slide 5 equivalent)
# ─────────────────────────────────────────────────────────────────────────────
def make_revenue_star(city, df):
    rev_color = REVENUE_COLORS[city]
    summary   = compute_star_summary(df)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    # NO suptitle — slide title covers it
    x = np.arange(len(summary)); w = 0.35

    bars1 = ax.bar(x-w/2, summary['booking_share'], width=w,
                   color=AGODA_BLUE, alpha=0.85, edgecolor='white')
    bars2 = ax.bar(x+w/2, summary['revenue_share'], width=w,
                   color=rev_color, alpha=0.85, edgecolor='white')

    for bar, row in zip(bars1, summary.itertuples()):
        if bar.get_height() > 5:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*0.48,
                    f'{row.n_bookings:,}',
                    ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=9)

    for bar, row in zip(bars2, summary.itertuples()):
        if bar.get_height() > 5:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*0.48,
                    f'${row.median_adr:.0f}',
                    ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                f'{bar.get_height():.1f}%', ha='center', va='bottom',
                fontsize=9, color=rev_color, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(summary['star_band'], fontsize=10)
    ax.set_title('Booking Volume vs Revenue Contribution by Star Band', fontsize=13, fontweight='bold')
    ax.set_ylabel('Share of Total (%)')
    ax.set_xlabel('Star Band  (note: half-star ratings are grouped into the band above them)')

    legend_handles = [
        mpatches.Patch(color=AGODA_BLUE, alpha=0.85,
                       label='Share of Bookings (%)   [# = Number of Bookings inside bar]'),
        mpatches.Patch(color=rev_color, alpha=0.85,
                       label='Share of Revenue (%)   [$ = Median ADR inside bar]'),
    ]
    ax.legend(handles=legend_handles, fontsize=10, loc='upper left')
    ax.set_ylim(0, summary[['booking_share','revenue_share']].max().max() * 1.32)

    ax.text(0.99, 0.98,
            "Data gap: To understand what moves customers\n"
            "to a higher star rating band we would need:\n"
            "• Price sensitivity / willingness-to-pay\n"
            "• Booking abandonment at higher-tier pages\n"
            "• Guest satisfaction scores by star band\n"
            "• Competitor pricing at each tier",
            transform=ax.transAxes, ha='right', va='top', fontsize=8.5,
            color=AGODA_DARK, style='italic',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF8E1',
                      edgecolor=AGODA_AMBER, alpha=0.95))

    plt.tight_layout()
    plt.savefig(f'{OUT}fig_{city}_revenue_star.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  City {city} Revenue by Star saved.")


# ─────────────────────────────────────────────────────────────────────────────
# EDA OVERVIEW — no suptitle, Panel C = revenue chart with correct legend
# ─────────────────────────────────────────────────────────────────────────────
def make_eda(city, df):
    color      = CITY_COLORS[city]
    rev_color  = REVENUE_COLORS[city]
    df_no_out  = df[df['ADR_USD'] <= 1000].copy()
    n_out      = len(df) - len(df_no_out)
    chain_n    = (df['chain_hotel']=='chain').sum()
    nonchain_n = (df['chain_hotel']=='non-chain').sum()
    summary    = compute_star_summary(df)

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    # NO suptitle — slide title covers this

    # Panel A: ADR distribution
    ax = axes[0,0]
    if n_out > 0:
        ax.hist(df['ADR_USD'], bins=60, color=AGODA_GREY, alpha=0.3,
                edgecolor='white', label=f'With {n_out} outlier(s) >$1,000')
        ax.hist(df_no_out['ADR_USD'], bins=60, color=color, alpha=0.8,
                edgecolor='white', label='Outliers removed')
    else:
        ax.hist(df['ADR_USD'], bins=60, color=color, alpha=0.8, edgecolor='white')
    med_val = df_no_out['ADR_USD'].median()
    ax.axvline(med_val, color=AGODA_DARK, lw=2, ls='--')
    p25, p75 = df_no_out['ADR_USD'].quantile([0.25, 0.75])
    legend_handles = [Line2D([0],[0],color=AGODA_DARK,lw=2,ls='--',
                             label=f'Median ADR: ${med_val:.0f}')]
    if n_out > 0:
        legend_handles += [
            mpatches.Patch(color=AGODA_GREY,alpha=0.4,label=f'Incl. {n_out} outlier(s) >$1,000'),
            mpatches.Patch(color=color,alpha=0.8,label='Outliers removed'),
        ]
    ax.legend(handles=legend_handles, fontsize=8.5)
    xtxt = min(p75 + 60, df_no_out['ADR_USD'].quantile(0.92))
    ymax_a = df_no_out['ADR_USD'].value_counts().max() * 1.2
    ax.annotate(f'50% of bookings\nfall between ${p25:.0f} – ${p75:.0f}',
                xy=(med_val, ymax_a * 0.5),
                xytext=(xtxt, ymax_a * 0.72),
                fontsize=9, color=AGODA_DARK,
                arrowprops=dict(arrowstyle='->', color=AGODA_DARK, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFBE6', alpha=0.9))
    ax.set_title('A. ADR Distribution')
    ax.set_xlabel('ADR (USD) — Average Daily Rate paid by customer')
    ax.set_ylabel('Number of Bookings')
    ax.set_xlim(0, min(df['ADR_USD'].quantile(0.99)*1.1, 1000))

    # Panel B: Lead time urgency tiers
    ax = axes[0,1]
    lead_vals = df['lead_time'].values
    n_bins, bin_edges, patches_b = ax.hist(lead_vals, bins=61, edgecolor='white', alpha=0.9)
    for patch, left in zip(patches_b, bin_edges[:-1]):
        if left <= 3:    patch.set_facecolor(AGODA_RED)
        elif left <= 14: patch.set_facecolor(AGODA_AMBER)
        else:            patch.set_facecolor(AGODA_BLUE)
    ymax = n_bins.max() * 1.3
    ax.axvspan(-0.5,3.5,  alpha=0.06, color=AGODA_RED,   zorder=0)
    ax.axvspan(3.5, 14.5, alpha=0.06, color=AGODA_AMBER,  zorder=0)
    ax.axvspan(14.5,61,   alpha=0.06, color=AGODA_BLUE,   zorder=0)
    h_pct = (df['lead_time']<=3).mean()*100
    m_pct =  df['lead_time'].between(4,14).mean()*100
    l_pct = (df['lead_time']>=15).mean()*100
    ax.text(1.5, ymax*0.93,f'HIGH\nURGENCY\n0–3d\n{h_pct:.1f}%',
            ha='center',va='top',fontsize=8,color=AGODA_RED,fontweight='bold')
    ax.text(9,   ymax*0.93,f'MEDIUM\nURGENCY\n4–14d\n{m_pct:.1f}%',
            ha='center',va='top',fontsize=8,color='#B05A00',fontweight='bold')
    ax.text(38,  ymax*0.93,f'LOW\nURGENCY\n15–60d\n{l_pct:.1f}%',
            ha='center',va='top',fontsize=8,color=AGODA_BLUE,fontweight='bold')
    med_lt = df['lead_time'].median()
    ax.axvline(med_lt, color=AGODA_DARK, lw=2, ls='--')
    ax.legend(handles=[
        Line2D([0],[0],color=AGODA_DARK,lw=2,ls='--',label=f'Median lead time: {int(med_lt)} days'),
        mpatches.Patch(color=AGODA_RED,   alpha=0.7, label='High Urgency (0–3d)'),
        mpatches.Patch(color=AGODA_AMBER, alpha=0.7, label='Medium Urgency (4–14d)'),
        mpatches.Patch(color=AGODA_BLUE,  alpha=0.7, label='Low Urgency (15–60d)'),
    ], fontsize=7.5, loc='upper right')
    ax.set_title('B. Lead Time Distribution\n(Coloured by urgency tier — % shown per tier)')
    ax.set_xlabel('Days Between Booking and Check-in')
    ax.set_ylabel('Number of Bookings')
    ax.set_ylim(0, ymax)

    # Panel C: Revenue vs Booking Share — CORRECT legend with # and $
    ax = axes[1,0]
    x = np.arange(len(summary)); w = 0.35
    bars1 = ax.bar(x-w/2, summary['booking_share'], width=w,
                   color=AGODA_BLUE, alpha=0.85, edgecolor='white')
    bars2 = ax.bar(x+w/2, summary['revenue_share'], width=w,
                   color=rev_color, alpha=0.85, edgecolor='white')

    for bar, row in zip(bars1, summary.itertuples()):
        if bar.get_height() > 5:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*0.45,
                    f'{row.n_bookings:,}', ha='center', va='center',
                    fontsize=7, fontweight='bold', color='white')
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                f'{bar.get_height():.0f}%', ha='center', va='bottom', fontsize=7.5)

    for bar, row in zip(bars2, summary.itertuples()):
        if bar.get_height() > 5:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*0.45,
                    f'${row.median_adr:.0f}', ha='center', va='center',
                    fontsize=7, fontweight='bold', color='white')
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                f'{bar.get_height():.0f}%', ha='center', va='bottom',
                fontsize=7.5, color=rev_color, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(summary['star_band'], fontsize=8)
    ax.set_title('C. Booking Volume vs Revenue Share by Star Band')
    ax.set_ylabel('Share of Total (%)')
    ax.set_xlabel('Star Band')
    # FIXED legend: includes # and $ explanations
    ax.legend(handles=[
        mpatches.Patch(color=AGODA_BLUE, alpha=0.85,
                       label='Share of Bookings (%)  [# = Number of Bookings]'),
        mpatches.Patch(color=rev_color,  alpha=0.85,
                       label='Share of Revenue (%)  [$ = Median ADR]'),
    ], fontsize=8, loc='upper left')
    ax.set_ylim(0, summary[['booking_share','revenue_share']].max().max()*1.38)

    # Panel D: Accommodation type
    ax = axes[1,1]
    acc_counts = df['accommodation_type_name'].value_counts()
    acc_sorted = acc_counts.sort_values(ascending=True)
    bar_cols_d = [color if i==len(acc_sorted)-1 else AGODA_BLUE
                  for i in range(len(acc_sorted))]
    bars = ax.barh(acc_sorted.index, acc_sorted.values, color=bar_cols_d, edgecolor='white')
    for bar, val in zip(bars, acc_sorted.values):
        ax.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2,
                f'{val:,}  ({val/len(df)*100:.1f}%)', va='center', fontsize=8.5)
    ax.set_title('D. Accommodation Type Mix')
    ax.set_xlabel('Number of Bookings')
    ax.set_xlim(0, acc_sorted.max()*1.6)
    ax.grid(axis='y', alpha=0)
    ax.text(0.5, -0.20,
            f'Chain bookings: {chain_n:,} ({chain_n/len(df)*100:.1f}%)          '
            f'Non-chain bookings: {nonchain_n:,} ({nonchain_n/len(df)*100:.1f}%)',
            transform=ax.transAxes, ha='center', va='top', fontsize=11,
            fontweight='bold', color=AGODA_DARK,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#EEF5FB',
                      edgecolor=AGODA_BLUE, alpha=0.95))

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.10)
    plt.savefig(f'{OUT}fig_{city}_eda.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  City {city} EDA saved.")


# ─────────────────────────────────────────────────────────────────────────────
# ADR vs LEAD TIME — no suptitle
# ─────────────────────────────────────────────────────────────────────────────
def make_adr_leadtime(city, df):
    color = CITY_COLORS[city]
    adr_by_lead = (df.groupby('lead_time')['ADR_USD']
                   .agg(['median','count']).reset_index()
                   .rename(columns={'median':'median_adr','count':'n'}))
    bucket_stats = (df.groupby('lead_bucket', observed=True)['ADR_USD']
                    .agg(['median','count']).reset_index()
                    .rename(columns={'median':'median_adr','count':'n'}))
    bucket_stats['pct'] = bucket_stats['n']/len(df)*100

    early_adr = df[df['lead_time'].between(31,60)]['ADR_USD']
    same_adr  = df[df['lead_time']==0]['ADR_USD']
    early_med = early_adr.median()
    same_med  = same_adr.median()
    pct_drop  = (same_med-early_med)/early_med*100 if early_med>0 else 0
    try:
        _, pval = stats.mannwhitneyu(same_adr, early_adr, alternative='two-sided')
        sig = f"p {'< 0.001' if pval<0.001 else f'= {pval:.3f}'}"
    except:
        sig = "n/a"

    fig, axes = plt.subplots(1, 2, figsize=(17, 7))
    # NO suptitle

    ax = axes[0]
    subset = adr_by_lead[adr_by_lead['n']>=20]
    ax.scatter(subset['lead_time'], subset['median_adr'],
               s=subset['n']/max(subset['n'].max()/200,1), color=color, alpha=0.5,
               label='Daily median ADR (bubble = volume)')
    smooth = adr_by_lead.set_index('lead_time')['median_adr'].rolling(3,center=True,min_periods=1).mean()
    ax.plot(smooth.index, smooth.values, color=AGODA_DARK, lw=2.5,
            label='Smoothed trend (3-day rolling avg)')
    ax.invert_xaxis()
    ax.text(0.97, 0.72,
            f'ADR drops {pct_drop:+.1f}%\n(31–60d → same-day)\n{sig}',
            transform=ax.transAxes, ha='right', va='top', fontsize=10,
            color=AGODA_DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFBE6', alpha=0.9))
    ax.set_title('A. Median ADR by Days to Check-in\n(right = same-day, left = far ahead)')
    ax.set_xlabel('Days Before Check-in ← (right = same-day)')
    ax.set_ylabel('Median ADR (USD)')
    ax.legend(loc='upper right', fontsize=9)

    ax = axes[1]
    bar_colors = [AGODA_RED if i==0 else AGODA_AMBER if i==1 else color
                  for i in range(len(bucket_stats))]
    bars = ax.bar(bucket_stats['lead_bucket'], bucket_stats['median_adr'],
                  color=bar_colors, edgecolor='white', width=0.6)
    for bar, row in zip(bars, bucket_stats.itertuples()):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                f'${row.median_adr:.0f}\n({row.pct:.0f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylim(0, bucket_stats['median_adr'].max()*1.35)
    ax.axvspan(-0.5, 1.5, alpha=0.07, color=AGODA_RED)
    last3_pct = (df['lead_time']<=3).mean()*100
    ax.annotate(
        f'Urgency window:\n{last3_pct:.1f}% of {city} bookings\nhappen within 3 days of check-in.\nTime-triggered messaging opportunity.',
        xy=(0.5, bucket_stats.iloc[0]['median_adr']),
        xytext=(2.5, bucket_stats['median_adr'].max()*1.18),
        fontsize=8.5, color=AGODA_RED, fontweight='bold',
        arrowprops=dict(arrowstyle='->', color=AGODA_RED, lw=1.5),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE8E8', alpha=0.9))
    ax.set_title("B. Median ADR by Lead Time Bucket\n(% = share of city's bookings)")
    ax.set_xlabel('Lead Time Bucket (left = last-minute)')
    ax.set_ylabel('Median ADR (USD)')
    ax.tick_params(axis='x', labelsize=9)
    ax.legend(handles=[
        mpatches.Patch(color=AGODA_RED,   label='Same-day (0d)'),
        mpatches.Patch(color=AGODA_AMBER, label='1–3 days'),
        mpatches.Patch(color=color,       label='4+ days ahead'),
    ], fontsize=9, loc='lower right')

    plt.tight_layout()
    plt.savefig(f'{OUT}fig_{city}_adr_leadtime.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  City {city} ADR vs Lead Time saved.")


# ─────────────────────────────────────────────────────────────────────────────
# SEGMENTATION — no suptitle
# ─────────────────────────────────────────────────────────────────────────────
def make_segmentation(city, df):
    color = CITY_COLORS[city]
    star_bucket = (df.groupby(['star_band','lead_bucket'], observed=True)['ADR_USD']
                   .agg(['median','count']).reset_index()
                   .rename(columns={'median':'median_adr','count':'n'}))
    star_bucket = star_bucket[star_bucket['star_band'].notna()]
    valid_stars = star_bucket.groupby('star_band', observed=True)['n'].sum()
    valid_stars = valid_stars[valid_stars>=30].index.tolist()
    star_bucket = star_bucket[star_bucket['star_band'].isin(valid_stars)]
    if len(valid_stars) == 0:
        print(f"  City {city} — not enough star data."); return

    fig, axes = plt.subplots(1, 2, figsize=(17, 7.5))
    # NO suptitle

    key_buckets = ['Same-day\n(0d)','1–3 days','15–30 days','31–60 days']
    star_key    = star_bucket[star_bucket['lead_bucket'].isin(key_buckets)]
    star_pivot  = star_key.pivot(index='star_band', columns='lead_bucket', values='median_adr')
    for kb in key_buckets:
        if kb not in star_pivot.columns: star_pivot[kb] = np.nan
    star_pivot = star_pivot.reindex(valid_stars)
    x = np.arange(len(star_pivot)); w = 0.2
    bucket_colors = [AGODA_RED, AGODA_AMBER, AGODA_BLUE, AGODA_DARK]
    for i,(bucket,bc) in enumerate(zip(key_buckets,bucket_colors)):
        vals = star_pivot[bucket].fillna(0).values
        if vals.sum() > 0:
            axes[0].bar(x+i*w-1.5*w, vals, width=w, color=bc, alpha=0.85,
                        label=bucket.replace('\n',' '), edgecolor='white')
    axes[0].set_xticks(x)
    # Shorter x-tick labels for grouped bands
    axes[0].set_xticklabels(
        [str(s).split('\n')[0] for s in star_pivot.index], fontsize=10)
    axes[0].set_title('A. Median ADR by Star Band and Lead Time')
    axes[0].set_ylabel('Median ADR (USD)'); axes[0].set_xlabel('Star Band')
    axes[0].legend(title='Lead Time', fontsize=9)

    ax = axes[1]
    bucket_order = ['Same-day\n(0d)','1–3 days','4–7 days','8–14 days','15–30 days','31–60 days']
    colors_map   = {'5★':'#8B0000',
                    '4★\n(incl. 4.5★)':AGODA_RED,
                    '3★\n(incl. 3.5★)':AGODA_AMBER,
                    '1–2★\n(incl. 1.5★, 2★, 2.5★)':AGODA_BLUE}
    x_pos = range(len(bucket_order))
    y_vals_all = []

    for star in valid_stars:
        col = colors_map.get(star, color)
        sub = star_bucket[star_bucket['star_band']==star].set_index('lead_bucket')['median_adr']
        sub = sub.reindex(bucket_order)
        if sub.notna().sum() >= 2:
            # Shorter legend label
            short_label = str(star).split('\n')[0]
            ax.plot(list(x_pos), sub.values, marker='o', color=col, lw=2.5,
                    label=short_label, markersize=7)
            y_vals_all.extend(sub.dropna().values)
            first_val = sub.iloc[-1]; last_val = sub.iloc[0]
            if pd.notna(first_val) and pd.notna(last_val) and first_val > 0:
                pct_drop = (last_val-first_val)/first_val*100
                if '5★' in str(star):
                    ax.annotate(f'{short_label}: {pct_drop:+.1f}%',
                                xy=(0, last_val), xytext=(0.8, last_val-12),
                                fontsize=8.5, color=col, fontweight='bold',
                                arrowprops=dict(arrowstyle='->', color=col, lw=1.2))
                else:
                    offset = 8 if '4★' in str(star) else -10 if '1–2★' in str(star) else 6
                    ax.annotate(f'{short_label}: {pct_drop:+.1f}%',
                                xy=(0, last_val), xytext=(0.8, last_val+offset),
                                fontsize=8.5, color=col, fontweight='bold',
                                arrowprops=dict(arrowstyle='->', color=col, lw=1.2))

    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(bucket_order, fontsize=9, rotation=10, ha='right')
    ax.invert_xaxis()
    ax.set_title('B. ADR Trend by Star Band — % drop shown for each band\n(Right = same-day, Left = 31–60 days ahead)')
    ax.set_xlabel('← Far Ahead       Lead Time       Same-day →')
    ax.set_ylabel('Median ADR (USD)')
    ax.legend(title='Star Band', fontsize=10, loc='upper right')

    if any('1–2★' in str(s) for s in valid_stars) and any('3★' in str(s) for s in valid_stars):
        ax.axvspan(3.5, 5.5, alpha=0.1, color=AGODA_GREEN, zorder=0)
        if y_vals_all:
            ax.text(4.5, min(y_vals_all)*0.97,
                    'Upsell window:\n1–2★ ≈ 3★ prices here',
                    ha='center', va='top', fontsize=8, color=AGODA_GREEN, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#E8F8F2', alpha=0.9))

    plt.tight_layout()
    plt.savefig(f'{OUT}fig_{city}_segmentation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  City {city} Segmentation saved.")


# ─────────────────────────────────────────────────────────────────────────────
# CROSS-CITY FIGURES — no suptitles
# ─────────────────────────────────────────────────────────────────────────────
def make_cross_city_figs():
    all_df = pd.concat(dfs.values(), ignore_index=True)
    bins   = [-1,0,3,7,14,30,60]
    labels = ['Same-day\n(0d)','1–3 days','4–7 days','8–14 days','15–30 days','31–60 days']
    all_df['lead_bucket'] = pd.cut(all_df['lead_time'], bins=bins, labels=labels)

    city_bucket = (all_df.groupby(['city','lead_bucket'],observed=True)['ADR_USD']
                   .agg(['median','count']).reset_index()
                   .rename(columns={'median':'median_adr','count':'n'}))
    city_total  = all_df.groupby('city')['ADR_USD'].count().rename('total')
    city_bucket = city_bucket.merge(city_total, on='city')
    city_bucket['pct_bookings'] = city_bucket['n']/city_bucket['total']*100

    city_drop = {}
    for c, df in dfs.items():
        em = df[df['lead_time'].between(31,60)]['ADR_USD'].median()
        sm = df[df['lead_time']==0]['ADR_USD'].median()
        city_drop[c] = {'early':em,'same':sm,'drop':(sm-em)/em*100 if em>0 else 0}

    # Fig 7 — no suptitle
    fig, axes = plt.subplots(1,2,figsize=(17,7))
    bucket_order = ['Same-day\n(0d)','1–3 days','4–7 days','8–14 days','15–30 days','31–60 days']
    ax = axes[0]
    for c in ['A','B','C','D','E']:
        sub = city_bucket[city_bucket['city']==c].set_index('lead_bucket')['median_adr']
        sub = sub.reindex(bucket_order)
        ax.plot(range(len(bucket_order)), sub.values, marker='o',
                color=CITY_COLORS[c], lw=2.5, label=f'City {c}', markersize=7)
        same_val = sub.iloc[0]
        if pd.notna(same_val):
            d = city_drop[c]['drop']
            ax.annotate(f'City {c}: {d:+.1f}%',
                        xy=(0, same_val),
                        xytext=(-0.3, same_val+(8 if c in ['C','D'] else -6 if c=='B' else 4)),
                        fontsize=8, color=CITY_COLORS[c], fontweight='bold', ha='center')
    ax.set_xticks(range(len(bucket_order)))
    ax.set_xticklabels(bucket_order, fontsize=9, rotation=10, ha='right')
    ax.invert_xaxis()
    ax.set_title('A. Median ADR by Lead Time — All 5 Cities\n(% drop shown per city at same-day point)')
    ax.set_xlabel('← Booked Far Ahead       Lead Time       Same-day →')
    ax.set_ylabel('Median ADR (USD)')
    ax.legend(title='City', fontsize=10)
    ax.text(0.98,0.98,'All 5 cities show prices\nfalling as check-in approaches.\nMagnitude differs significantly.',
            transform=ax.transAxes, va='top', ha='right', fontsize=9, style='italic', color=AGODA_DARK,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFBE6', alpha=0.9))

    ax = axes[1]
    x = np.arange(len(bucket_order)); w = 0.15
    for i,c in enumerate(['A','B','C','D','E']):
        sub = city_bucket[city_bucket['city']==c].set_index('lead_bucket')['pct_bookings']
        sub = sub.reindex(bucket_order).fillna(0)
        ax.bar(x+i*w-2*w, sub.values, width=w, color=CITY_COLORS[c], alpha=0.85,
               label=f'City {c}', edgecolor='white')
    ax.set_xticks(x)
    ax.set_xticklabels(bucket_order, fontsize=9, rotation=10, ha='right')
    ax.set_title("B. Booking Volume Distribution by Lead Time\n(% of each city's total bookings)")
    ax.set_xlabel('Lead Time Bucket  (left = last-minute)')
    ax.set_ylabel("% of City's Bookings")
    ax.legend(title='City', fontsize=9)
    plt.tight_layout()
    plt.savefig(f'{OUT}fig7_cross_city_adr.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Fig7 saved.")

    # Fig 8 — no suptitle
    cities = ['A','B','C','D','E']
    fig, axes = plt.subplots(2,2,figsize=(16,11))

    ax = axes[0,0]
    x = np.arange(5); w = 0.35
    early_vals = [city_drop[c]['early'] for c in cities]
    same_vals  = [city_drop[c]['same']  for c in cities]
    ax.bar(x-w/2, early_vals, width=w,
           color=[CITY_COLORS[c] for c in cities], alpha=0.35, edgecolor='white',
           label='Early booking (31–60 days ahead)')
    ax.bar(x+w/2, same_vals,  width=w,
           color=[CITY_COLORS[c] for c in cities], alpha=0.9, edgecolor='white',
           label='Same-day booking')
    for i,(e,s,c) in enumerate(zip(early_vals, same_vals, cities)):
        ax.text(i-w/2, e+2, f'${e:.0f}', ha='center', va='bottom', fontsize=8)
        ax.text(i+w/2, s+2, f'${s:.0f}', ha='center', va='bottom', fontsize=8)
        drop = city_drop[c]['drop']
        if c == 'C':
            ax.text(i-w/2+w*0.95, e*0.55, f'{drop:+.1f}%', ha='left', va='center',
                    fontsize=9, fontweight='bold', color=CITY_COLORS[c],
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                              edgecolor=CITY_COLORS[c], alpha=0.9))
        else:
            ax.text(i, max(e,s)+8, f'{drop:+.1f}%', ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color=CITY_COLORS[c])
    ax.set_xticks(x)
    ax.set_xticklabels([f'City {c}' for c in cities])
    ax.set_title('A. Early Booking vs Same-Day ADR by City\n(% = ADR drop from early to same-day)')
    ax.set_ylabel('Median ADR (USD)'); ax.legend(fontsize=9)

    ax = axes[0,1]
    city_sameday = [(df['lead_time']==0).mean()*100 for df in dfs.values()]
    bars = ax.bar([f'City {c}' for c in cities], city_sameday,
                  color=[CITY_COLORS[c] for c in cities], edgecolor='white')
    for bar, val in zip(bars, city_sameday):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title('B. Same-Day Booking Rate by City\n(% of bookings made on check-in day)')
    ax.set_ylabel('% Same-Day Bookings')
    ax.axhline(sum(city_sameday)/5, color=AGODA_DARK, lw=1.5, ls='--', label='Average')
    ax.legend()

    ax = axes[1,0]
    city_dir_results = []
    for c, df in dfs.items():
        eh = df[df['lead_time']>=15].groupby('hotel_id')['ADR_USD'].median()
        lh = df[df['lead_time']<=3].groupby('hotel_id')['ADR_USD'].median()
        hd = pd.concat([eh.rename('e'),lh.rename('l')],axis=1).dropna()
        hd['chg'] = (hd['l']-hd['e'])/hd['e']*100
        city_dir_results.append({'city':c,
            'falling':(hd['chg']<-5).mean()*100,
            'stable': ((hd['chg']>=-5)&(hd['chg']<=5)).mean()*100,
            'rising': (hd['chg']>5).mean()*100})
    cdr = pd.DataFrame(city_dir_results)
    x_c = np.arange(5); bottom = np.zeros(5)
    for direction, dcolor in [('falling',AGODA_BLUE),('stable',AGODA_AMBER),('rising',AGODA_RED)]:
        vals = cdr[direction].values
        ax.bar(x_c, vals, bottom=bottom, color=dcolor, edgecolor='white', alpha=0.85,
               label=f'{"Price falls" if direction=="falling" else "Stable" if direction=="stable" else "Price rises"} last-minute')
        for xi,(b,v) in enumerate(zip(bottom,vals)):
            if v>8: ax.text(xi,b+v/2,f'{v:.0f}%',ha='center',va='center',fontsize=9,fontweight='bold',color='white')
        bottom+=vals
    ax.set_xticks(x_c); ax.set_xticklabels([f'City {c}' for c in cdr['city']])
    ax.set_title('C. Hotel Price Direction by City\n(% rising/stable/falling last-minute)')
    ax.set_ylabel('% of Properties'); ax.legend(fontsize=9); ax.set_ylim(0,115)

    ax = axes[1,1]
    city_lt = [df['lead_time'].median() for df in dfs.values()]
    bars = ax.bar([f'City {c}' for c in cities], city_lt,
                  color=[CITY_COLORS[c] for c in cities], edgecolor='white')
    for bar, val in zip(bars, city_lt):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                f'{val:.0f}d', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_title('D. Median Lead Time by City\n(How far ahead does each city typically book?)')
    ax.set_ylabel('Median Lead Time (days)')
    ax.axhline(sum(city_lt)/5, color=AGODA_DARK, lw=1.5, ls='--', label='Average')
    ax.legend()

    plt.tight_layout()
    plt.savefig(f'{OUT}fig8_cross_city_profile.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Fig8 saved.")

    # Fig 9 — no suptitle
    city_drop_df = pd.DataFrame([
        {'city':c,'drop':city_drop[c]['drop'],'early':city_drop[c]['early'],'same':city_drop[c]['same']}
        for c in cities])
    all_df['urgency'] = pd.cut(all_df['lead_time'],bins=[-1,3,14,60],
        labels=['High Urgency\n(0–3 days)','Medium Urgency\n(4–14 days)','Low Urgency\n(15–60 days)'])
    urgency_share  = (all_df.groupby(['city','urgency'],observed=True).size().reset_index(name='n'))
    city_totals    = urgency_share.groupby('city')['n'].transform('sum')
    urgency_share['pct'] = urgency_share['n']/city_totals*100
    urgency_pivot  = urgency_share.pivot_table(index='city',columns='urgency',values='pct',observed=True).fillna(0)

    fig, axes = plt.subplots(1,2,figsize=(17,7))
    ax = axes[0]
    bars = ax.bar([f'City {c}' for c in city_drop_df['city']],
                  city_drop_df['drop'],
                  color=[CITY_COLORS[c] for c in city_drop_df['city']], edgecolor='white')
    for bar, row in zip(bars, city_drop_df.itertuples()):
        ax.text(bar.get_x()+bar.get_width()/2,
                row.drop-0.5 if row.drop<0 else row.drop+0.2,
                f'{row.drop:+.1f}%\n(${row.early:.0f}→${row.same:.0f})',
                ha='center', va='top' if row.drop<0 else 'bottom', fontsize=9, fontweight='bold')
    ax.axhline(0, color=AGODA_DARK, lw=1.5)
    ax.set_ylabel('% Change in Median ADR')
    ax.set_title('A. % ADR Change: 31–60 Days Ahead → Same-Day\n(All cities show price decline last-minute)')

    ax = axes[1]; x_u = np.arange(5); bottom = np.zeros(5)
    for col, ucolor in zip(['High Urgency\n(0–3 days)','Medium Urgency\n(4–14 days)','Low Urgency\n(15–60 days)'],
                           [AGODA_RED, AGODA_AMBER, AGODA_BLUE]):
        if col in urgency_pivot.columns:
            vals = urgency_pivot[col].values
            ax.bar(x_u, vals, bottom=bottom, color=ucolor, edgecolor='white', alpha=0.85,
                   label=col.replace('\n',' '))
            for xi,(b,v) in enumerate(zip(bottom,vals)):
                if v>6: ax.text(xi,b+v/2,f'{v:.0f}%',ha='center',va='center',fontsize=9,fontweight='bold',color='white')
            bottom+=vals
    ax.set_xticks(x_u); ax.set_xticklabels([f'City {c}' for c in urgency_pivot.index])
    ax.set_title('B. Urgency Tier Booking Share by City')
    ax.set_ylabel("% of City's Bookings"); ax.legend(title='Urgency Tier',fontsize=9); ax.set_ylim(0,115)

    plt.tight_layout()
    plt.savefig(f'{OUT}fig9_cross_city_urgency.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Fig9 saved.")


# ── RUN ALL ───────────────────────────────────────────────────────────────────
for city in ['A','B','C','D','E']:
    print(f"\nGenerating City {city}...")
    make_eda(city, dfs[city])
    make_revenue_star(city, dfs[city])
    make_adr_leadtime(city, dfs[city])
    make_segmentation(city, dfs[city])

print("\nGenerating cross-city figures...")
make_cross_city_figs()
print("\n✓ All figures complete.")
