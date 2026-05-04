"""
Three figure updates:
1. fig_xt_01_monthly.png  — Monthly booking analysis (replaces ADR dist on slide 5)
2. fig_crosscity_eda.png  — Slide 4 Panel A replaced with simpler city price range chart
3. fig_cross_final.png    — Slide 13 legend moved to middle-left of Panel A
"""
import matplotlib
matplotlib.use('Agg')
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

RED='#E4272B'; DARK='#1A1A2E'; BLUE='#2E86AB'; AMBER='#F4A261'
GREEN='#2A9D8F'; PURPLE='#6C3483'; GREY='#6B6B6B'
CITY_COLORS={'A':RED,'B':BLUE,'C':AMBER,'D':GREEN,'E':'#9B59B6'}
REVENUE_COLORS={'A':RED,'B':PURPLE,'C':AMBER,'D':GREEN,'E':'#8B0000'}
CITY_TITLES={
    'A':'City A\nUrban Mixed','B':'City B\nResort-Heavy',
    'C':'City C\nPremium/Planned','D':'City D\nPremium/Stable',
    'E':'City E\nLast-Minute'
}
BUCKET_ORDER=['Same-day\n(0d)','1–3 days','4–7 days','8–14 days','15–30 days','31–60 days']
MONTHS={10:'Oct',11:'Nov',12:'Dec'}
MONTH_COLORS={10:BLUE, 11:AMBER, 12:RED}   # Dec=red = holiday urgency

plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','axes.edgecolor':'#CCCCCC',
    'axes.grid':True,'grid.alpha':0.3,'grid.color':'#CCCCCC','font.family':'sans-serif',
    'font.size':9,'axes.titlesize':10,'axes.titleweight':'bold'})

def load_city(c):
    df=pd.read_excel(f'../data/City_{c}.xlsx')
    df['city']=c
    if 'accommadation_type_name' in df.columns:
        df.rename(columns={'accommadation_type_name':'accommodation_type_name'},inplace=True)
    df['lead_time']=(df['checkin_date']-df['booking_date']).dt.days
    df['length_of_stay']=(df['checkout_date']-df['checkin_date']).dt.days
    df['revenue_proxy']=df['ADR_USD']*df['length_of_stay']
    df=df[df['lead_time']>=0].copy()
    df['lead_bucket']=pd.cut(df['lead_time'],bins=[-1,0,3,7,14,30,60],labels=BUCKET_ORDER)
    df['star_band']=pd.cut(df['star_rating'],bins=[-0.5,2.5,3.5,4.5,5.5],
        labels=['1–2★\n(incl. 1.5★, 2★, 2.5★)','3★\n(incl. 3.5★)','4★\n(incl. 4.5★)','5★'])
    df['checkin_month']=df['checkin_date'].dt.month
    df['booking_month']=df['booking_date'].dt.month
    df['is_lastminute']=df['lead_time']<=3
    return df

dfs={c:load_city(c) for c in ['A','B','C','D','E']}
cities=['A','B','C','D','E']

def insight_panel(ax, lines, bg='#F8F8FF', fontsize=9.5):
    ax.axis('off'); ax.set_facecolor(bg); ax.patch.set_visible(True)
    for spine in ax.spines.values():
        spine.set_visible(True); spine.set_color('#CCCCDD')
    combined='\n\n'.join(lines)
    ax.text(0.5,0.5,combined,transform=ax.transAxes,ha='center',va='center',
            fontsize=fontsize,color=DARK,wrap=True,
            bbox=dict(boxstyle='round,pad=0.5',facecolor=bg,edgecolor='#CCCCDD',alpha=0.0))

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1: Monthly Booking Analysis — all 5 cities
# 2×3 grid: 5 city panels + 1 insight panel
# Each city panel: 3 grouped bars (Oct/Nov/Dec) showing bookings, ADR, last-min%
# ─────────────────────────────────────────────────────────────────────────────
print("Building monthly booking analysis figure...")
fig, axes = plt.subplots(2, 3, figsize=(20, 8.3))
city_pos=[(0,0),(0,1),(0,2),(1,0),(1,1)]

# Collect cross-city summary for insight panel
summary = {}
for c, df in dfs.items():
    rows = {}
    for m in [10,11,12]:
        sub = df[df['checkin_month']==m]
        rows[m] = {
            'n': len(sub),
            'adr': sub['ADR_USD'].median(),
            'lm_pct': sub['is_lastminute'].mean()*100,
            'rev': sub['revenue_proxy'].sum()/1000  # in $k
        }
    summary[c] = rows

for (r,c_),c in zip(city_pos, cities):
    ax = axes[r,c_]
    color = CITY_COLORS[c]
    rows = summary[c]
    months = [10,11,12]
    month_labels = ['Oct','Nov','Dec']
    x = np.arange(3); w = 0.25

    # Bar 1: Booking volume (normalised to % of total for comparability)
    total_n = sum(rows[m]['n'] for m in months)
    n_pcts = [rows[m]['n']/total_n*100 for m in months]

    # Bar 2: Median ADR
    adrs = [rows[m]['adr'] for m in months]

    # Bar 3: Last-minute %
    lm_pcts = [rows[m]['lm_pct'] for m in months]

    # Use twin axis: left = ADR, right = % metrics
    ax2 = ax.twinx()

    # Booking volume bars (left axis — raw counts)
    n_vals = [rows[m]['n'] for m in months]
    b1 = ax.bar(x-w, n_vals, width=w, color=[MONTH_COLORS[m] for m in months],
                alpha=0.35, edgecolor='white', label='Bookings (count)')

    # ADR bars (left axis)
    b2 = ax.bar(x, adrs, width=w, color=[MONTH_COLORS[m] for m in months],
                alpha=0.85, edgecolor='white', label='Median ADR ($)')

    # Last-minute % line (right axis)
    ax2.plot(x, lm_pcts, color=RED, marker='o', lw=2, ms=6, label='Last-min %', zorder=5)
    ax2.set_ylim(0, max(lm_pcts)*2.2)
    ax2.set_ylabel('Last-min %' if c_==2 else '', fontsize=8, color=RED)
    ax2.tick_params(axis='y', labelcolor=RED, labelsize=7.5)

    # Labels on ADR bars
    for xi, (adr, n) in enumerate(zip(adrs, n_vals)):
        ax.text(xi, adr+1, f'${adr:.0f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
        ax.text(xi-w, n_vals[xi]+50, f'{n_vals[xi]:,}', ha='center', va='bottom', fontsize=6.5, color=DARK)

    # Last-min % labels
    for xi, lm in enumerate(lm_pcts):
        ax2.text(xi+0.05, lm+0.5, f'{lm:.0f}%', ha='left', va='bottom', fontsize=7.5,
                 fontweight='bold', color=RED)

    # Dec highlight
    ax.axvspan(1.55, 2.45, alpha=0.06, color=RED, zorder=0)

    ax.set_xticks(x)
    ax.set_xticklabels(month_labels, fontsize=9)
    ax.set_title(CITY_TITLES[c], color=color, fontweight='bold')
    ax.set_ylabel('Count / ADR ($)' if c_==0 else '', fontsize=8)
    ax.set_ylim(0, max(max(n_vals), max(adrs))*1.45)
    ax.grid(axis='x', alpha=0)

    # Legend only on first panel
    if r==0 and c_==0:
        legend_handles = [
            mpatches.Patch(color=GREY, alpha=0.35, label='Booking Count (light bar)'),
            mpatches.Patch(color=GREY, alpha=0.85, label='Median ADR $ (solid bar)'),
            Line2D([0],[0], color=RED, marker='o', lw=2, label='Last-min booking % →'),
        ]
        ax.legend(handles=legend_handles, fontsize=7, loc='upper left')

# Insight panel
dec_adr_lifts = []
dec_lm_drops = []
for c in cities:
    oct_adr = summary[c][10]['adr']; dec_adr = summary[c][12]['adr']
    oct_lm  = summary[c][10]['lm_pct']; dec_lm  = summary[c][12]['lm_pct']
    dec_adr_lifts.append((dec_adr-oct_adr)/oct_adr*100)
    dec_lm_drops.append(dec_lm - oct_lm)

insight_panel(axes[1,2],[
    '📅 Monthly Patterns: Key Insights',
    f'December ADR premium vs October:\nB: +{dec_adr_lifts[1]:+.0f}%  D: +{dec_adr_lifts[3]:+.0f}%\nE: +{dec_adr_lifts[4]:+.0f}%  A: +{dec_adr_lifts[0]:+.0f}%',
    'Last-minute booking rate FALLS\nin December across all cities\n(people plan ahead for holidays)',
    f'Biggest last-min drop Oct→Dec:\nCity B: {dec_lm_drops[1]:+.0f}pp  City E: {dec_lm_drops[4]:+.0f}pp',
    '→ Dec urgency strategy shift:\n"Book now — prices rising"\nor "Limited rooms for holidays"\n(scarcity > earn-sooner)',
    '→ Oct/Nov: earn-sooner framing\nworks best (last-min rates high)'
], fontsize=9)

plt.tight_layout(pad=0.8)
plt.savefig('/home/claude/fig_xt_01_monthly.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Monthly figure saved.")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2: Slide 4 — replace Panel A (KDE) with simple city price range chart
# Show: median ADR + IQR bar per city, grouped by Budget vs Premium cluster
# ─────────────────────────────────────────────────────────────────────────────
print("Building slide 4 updated cross-city EDA...")

all_df=pd.concat(dfs.values(),ignore_index=True)
all_df['lead_bucket']=pd.cut(all_df['lead_time'],bins=[-1,0,3,7,14,30,60],labels=BUCKET_ORDER)
all_df['urgency']=pd.cut(all_df['lead_time'],bins=[-1,3,14,60],
    labels=['High Urgency\n(0–3d)','Medium Urgency\n(4–14d)','Low Urgency\n(15–60d)'])
all_df['star_band']=pd.cut(all_df['star_rating'],bins=[-0.5,2.5,3.5,4.5,5.5],
    labels=['1–2★\n(incl. 1.5★, 2★, 2.5★)','3★\n(incl. 3.5★)','4★\n(incl. 4.5★)','5★'])

fig, axes = plt.subplots(2, 2, figsize=(20, 8.3))

# Panel A: City price range — simple horizontal bar showing p25-p75 range + median dot
ax = axes[0,0]
city_labels_full = {
    'A':'City A (Urban Mixed)','B':'City B (Resort-Heavy)',
    'C':'City C (Premium/Planned)','D':'City D (Premium/Stable)',
    'E':'City E (Last-Minute)'
}
y_pos = np.arange(5)
for i,c in enumerate(['A','B','C','D','E']):
    df = dfs[c]
    df_cap = df[df['ADR_USD']<=df['ADR_USD'].quantile(0.97)]
    p10 = df_cap['ADR_USD'].quantile(0.10)
    p25 = df_cap['ADR_USD'].quantile(0.25)
    med = df_cap['ADR_USD'].median()
    p75 = df_cap['ADR_USD'].quantile(0.75)
    p90 = df_cap['ADR_USD'].quantile(0.90)
    color = CITY_COLORS[c]

    # Wide range bar (p10-p90) — light
    ax.barh(i, p90-p10, left=p10, height=0.35, color=color, alpha=0.20, edgecolor='none')
    # IQR bar (p25-p75) — solid
    ax.barh(i, p75-p25, left=p25, height=0.35, color=color, alpha=0.80, edgecolor='none')
    # Median line
    ax.plot([med, med], [i-0.22, i+0.22], color=DARK, lw=2.5, zorder=5)
    # Labels
    ax.text(p25-2, i, f'${p25:.0f}', ha='right', va='center', fontsize=8, color=color)
    ax.text(p75+2, i, f'${p75:.0f}', ha='left',  va='center', fontsize=8, color=color)
    ax.text(med,   i+0.26, f'Med: ${med:.0f}', ha='center', va='bottom', fontsize=8.5,
            fontweight='bold', color=DARK)

ax.set_yticks(y_pos)
ax.set_yticklabels([city_labels_full[c] for c in cities], fontsize=9)
ax.set_xlabel('ADR (USD)')
ax.set_title('A. Price Range by City\n(IQR shown as solid bar; light band = p10–p90; line = median)')

# Cluster annotations
ax.axhspan(1.5, 4.5, alpha=0.04, color=AMBER, zorder=0)
ax.axhspan(-0.5, 1.5, alpha=0.04, color=BLUE, zorder=0)
ax.text(1.01, 0.78, 'Premium\ncluster', transform=ax.transAxes, fontsize=8.5,
        color=AMBER, fontweight='bold', va='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF8E1', alpha=0.9))
ax.text(1.01, 0.12, 'Budget\ncluster', transform=ax.transAxes, fontsize=8.5,
        color=BLUE, fontweight='bold', va='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#EEF5FB', alpha=0.9))
ax.legend(handles=[
    mpatches.Patch(color=GREY, alpha=0.80, label='IQR (middle 50% of bookings)'),
    mpatches.Patch(color=GREY, alpha=0.20, label='p10–p90 range'),
    Line2D([0],[0], color=DARK, lw=2.5, label='Median ADR'),
], fontsize=8, loc='lower right')

# Panel B: urgency tier share
ax = axes[0,1]
urgency_share=(all_df.groupby(['city','urgency'],observed=True).size().reset_index(name='n'))
city_totals_u=urgency_share.groupby('city')['n'].transform('sum')
urgency_share['pct']=urgency_share['n']/city_totals_u*100
urgency_pivot=urgency_share.pivot_table(index='city',columns='urgency',values='pct',observed=True).fillna(0)
x_u=np.arange(5); w_u=0.25
for j,(col,uc) in enumerate(zip(
        ['High Urgency\n(0–3d)','Medium Urgency\n(4–14d)','Low Urgency\n(15–60d)'],[RED,AMBER,BLUE])):
    if col in urgency_pivot.columns:
        vals=urgency_pivot[col].values
        bars=ax.bar(x_u+j*w_u-w_u,vals,width=w_u,color=uc,alpha=0.85,label=col.replace('\n',' '),edgecolor='white')
        for bar,v in zip(bars,vals):
            if v>8: ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.5,f'{v:.0f}%',
                            ha='center',va='bottom',fontsize=7.5,fontweight='bold',color=uc)
ax.set_xticks(x_u); ax.set_xticklabels([f'City {c}' for c in urgency_pivot.index])
ax.set_title('B. Lead Time Urgency Tier Share per City\n(Cities E & B: highest last-minute share → high-urgency messaging needed)')
ax.set_ylabel("% of City's Bookings"); ax.set_ylim(0,75)
ax.legend(title='Urgency Tier',fontsize=9)
avg_high=urgency_pivot.get('High Urgency\n(0–3d)',pd.Series([0]*5)).mean()
ax.axhline(avg_high,color=DARK,lw=1.2,ls='--',alpha=0.5)
ax.text(4.6,avg_high+0.8,f'Avg\n{avg_high:.0f}%',fontsize=7.5,color=DARK,alpha=0.7)

# Panel C: Revenue vs booking share per city (same as before)
ax = axes[1,0]
star_bands_short=['1–2★','3★','4★','5★']
star_band_keys=['1–2★\n(incl. 1.5★, 2★, 2.5★)','3★\n(incl. 3.5★)','4★\n(incl. 4.5★)','5★']
star_colors_c=[BLUE,AMBER,RED,'#8B0000']
city_star_rev={}
for c,df in dfs.items():
    sub=df[df['star_band'].notna()]
    grp=sub.groupby('star_band',observed=True).agg(n=('ADR_USD','count'),rev=('revenue_proxy','sum')).reset_index()
    total_n_=grp['n'].sum(); total_rev_=grp['rev'].sum()
    grp['book_share']=grp['n']/total_n_*100; grp['rev_share']=grp['rev']/total_rev_*100
    city_star_rev[c]=grp
x_c=np.arange(5); n_bands=4; bar_w=0.09
for j,(band_key,band_short,sc) in enumerate(zip(star_band_keys,star_bands_short,star_colors_c)):
    rev_vals=[]; book_vals=[]
    for c in cities:
        row=city_star_rev[c][city_star_rev[c]['star_band']==band_key]
        rev_vals.append(row['rev_share'].values[0] if len(row)>0 else 0)
        book_vals.append(row['book_share'].values[0] if len(row)>0 else 0)
    ax.bar(x_c+j*bar_w*2-n_bands*bar_w+bar_w/2,rev_vals,width=bar_w,color=sc,alpha=0.9,edgecolor='white',label=f'{band_short} Rev%')
    ax.bar(x_c+j*bar_w*2-n_bands*bar_w+bar_w*1.5,book_vals,width=bar_w,color=sc,alpha=0.35,edgecolor='white',hatch='//',label=f'{band_short} Book%')
ax.set_xticks(x_c); ax.set_xticklabels([f'City {c}' for c in cities])
ax.set_title('C. Revenue vs Booking Share by Star Band — All Cities\n(Solid = Revenue %, Hatched = Booking %  |  4★/5★ Revenue > Booking share in all cities)')
ax.set_ylabel('Share of Total (%)')
legend_handles=[mpatches.Patch(color=sc,alpha=0.9,label=f'{bs} Rev%') for bs,sc in zip(star_bands_short,star_colors_c)] + \
               [mpatches.Patch(color=sc,alpha=0.35,label=f'{bs} Book%',hatch='//') for bs,sc in zip(star_bands_short,star_colors_c)]
ax.legend(handles=legend_handles,fontsize=7,loc='upper right',ncol=2); ax.set_ylim(0,70)

# Panel D: Accommodation type stacked % (same as before)
ax = axes[1,1]
top_types_all=all_df['accommodation_type_name'].value_counts().head(6).index.tolist()
colors_acc=[RED,BLUE,AMBER,GREEN,PURPLE,'#8B0000','#AAAAAA']
city_acc_pct={}
for c,df in dfs.items():
    counts=df['accommodation_type_name'].value_counts(); pcts={}
    for t in top_types_all: pcts[t]=counts.get(t,0)/len(df)*100
    pcts['Other']=max(0,100-sum(pcts.values()))
    city_acc_pct[c]=pcts
x_a=np.arange(5); bar_w_a=0.55; bottom=np.zeros(5)
type_list=top_types_all+['Other']
type_colors=colors_acc[:len(type_list)]
for t,tc in zip(type_list,type_colors):
    vals=np.array([city_acc_pct[c].get(t,0) for c in cities])
    ax.bar(x_a,vals,bottom=bottom,width=bar_w_a,color=tc,edgecolor='white',alpha=0.85,label=t)
    for xi,(b,v) in enumerate(zip(bottom,vals)):
        if v>5: ax.text(xi,b+v/2,f'{v:.0f}%',ha='center',va='center',fontsize=8,fontweight='bold',color='white')
    bottom+=vals
ax.set_xticks(x_a); ax.set_xticklabels([f'City {c}' for c in cities])
ax.set_title('D. Accommodation Type Mix per City\n(% of bookings by property type)')
ax.set_ylabel('% of Bookings'); ax.set_ylim(0,115)
ax.legend(fontsize=8,loc='upper right',bbox_to_anchor=(1.0,1.0))

plt.tight_layout(pad=1.0)
plt.savefig('/home/claude/fig_crosscity_eda.png',dpi=150,bbox_inches='tight')
plt.close()
print("  Slide 4 EDA figure saved.")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3: Slide 13 — fix legend position in Panel A of fig_cross_final
# ─────────────────────────────────────────────────────────────────────────────
print("Building slide 13 cross-city final with legend moved to middle-left...")

city_drop={}
for c,df in dfs.items():
    em=df[df['lead_time'].between(31,60)]['ADR_USD'].median()
    sm=df[df['lead_time']==0]['ADR_USD'].median()
    city_drop[c]={'early':em,'same':sm,'drop':(sm-em)/em*100 if em>0 else 0}

city_bucket=(all_df.groupby(['city','lead_bucket'],observed=True)['ADR_USD']
             .agg(['median','count']).reset_index().rename(columns={'median':'median_adr','count':'n'}))
city_total=all_df.groupby('city')['ADR_USD'].count().rename('total')
city_bucket=city_bucket.merge(city_total,on='city')
city_bucket['pct_bookings']=city_bucket['n']/city_bucket['total']*100

all_df['urgency2']=pd.cut(all_df['lead_time'],bins=[-1,3,14,60],
    labels=['High Urgency\n(0–3d)','Medium Urgency\n(4–14d)','Low Urgency\n(15–60d)'])
urgency_share2=(all_df.groupby(['city','urgency2'],observed=True).size().reset_index(name='n'))
city_totals_u2=urgency_share2.groupby('city')['n'].transform('sum')
urgency_share2['pct']=urgency_share2['n']/city_totals_u2*100
urgency_pivot2=urgency_share2.pivot_table(index='city',columns='urgency2',values='pct',observed=True).fillna(0)

city_drop_df=pd.DataFrame([{'city':c,'drop':city_drop[c]['drop'],
    'early':city_drop[c]['early'],'same':city_drop[c]['same']} for c in cities])

fig,axes=plt.subplots(2,2,figsize=(20,8.3))

# Panel A: ADR trend — legend at middle-left (loc='center left')
ax=axes[0,0]
city_vals={}
for c in cities:
    sub=city_bucket[city_bucket['city']==c].set_index('lead_bucket')['median_adr']
    sub=sub.reindex(BUCKET_ORDER); city_vals[c]=sub
    ax.plot(range(len(BUCKET_ORDER)),sub.values,marker='o',color=CITY_COLORS[c],lw=2.5,label=f'City {c}',markersize=7)
    same_val=sub.iloc[0]; d=city_drop[c]['drop']
    if pd.notna(same_val):
        if c=='D':
            ax.text(-0.4,same_val-12,f'City {c}: {d:+.1f}%',ha='center',va='top',fontsize=8,color=CITY_COLORS[c],fontweight='bold')
        elif c=='E':
            ax.annotate(f'City {c}: {d:+.1f}%',xy=(0,same_val),xytext=(-0.3,same_val-7),fontsize=8,color=CITY_COLORS[c],fontweight='bold',ha='center')
        elif c=='A':
            ax.annotate(f'City {c}: {d:+.1f}%',xy=(0,same_val),xytext=(-0.3,same_val+5),fontsize=8,color=CITY_COLORS[c],fontweight='bold',ha='center')
        else:
            ax.annotate(f'City {c}: {d:+.1f}%',xy=(0,same_val),xytext=(-0.3,same_val+(8 if c=='C' else 4)),fontsize=8,color=CITY_COLORS[c],fontweight='bold',ha='center')
ax.set_xticks(range(len(BUCKET_ORDER))); ax.set_xticklabels(BUCKET_ORDER,fontsize=8.5,rotation=10,ha='right')
ax.invert_xaxis()
ax.set_title('A. Median ADR by Lead Time — All 5 Cities\n(% drop shown per city at same-day point)')
ax.set_xlabel('← Booked Far Ahead       Lead Time       Same-day →'); ax.set_ylabel('Median ADR (USD)')
# LEGEND MOVED TO MIDDLE-LEFT — away from top-right annotation
ax.legend(title='City',fontsize=9,loc='center left')
ax.text(0.98,0.98,'All 5 cities: prices fall\nas check-in approaches.',
        transform=ax.transAxes,va='top',ha='right',fontsize=8,style='italic',color=DARK,
        bbox=dict(boxstyle='round,pad=0.2',facecolor='#FFFBE6',alpha=0.7))

# Panel B: booking volume distribution
ax=axes[0,1]
x=np.arange(len(BUCKET_ORDER)); w2=0.15
for i,c in enumerate(cities):
    sub=city_bucket[city_bucket['city']==c].set_index('lead_bucket')['pct_bookings']
    sub=sub.reindex(BUCKET_ORDER).fillna(0)
    ax.bar(x+i*w2-2*w2,sub.values,width=w2,color=CITY_COLORS[c],alpha=0.85,label=f'City {c}',edgecolor='white')
ax.set_xticks(x); ax.set_xticklabels(BUCKET_ORDER,fontsize=8.5,rotation=10,ha='right')
ax.set_title("B. Booking Volume Distribution by Lead Time\n(% of each city's total bookings)")
ax.set_xlabel('Lead Time Bucket  (left = last-minute)')
ax.set_ylabel("% of City's Bookings"); ax.legend(title='City',fontsize=9)

# Panel C: revenue vs booking share per city
ax=axes[1,0]
for j,(band_key,band_short,sc) in enumerate(zip(star_band_keys,star_bands_short,star_colors_c)):
    rev_vals=[]; book_vals=[]
    for c in cities:
        row=city_star_rev[c][city_star_rev[c]['star_band']==band_key]
        rev_vals.append(row['rev_share'].values[0] if len(row)>0 else 0)
        book_vals.append(row['book_share'].values[0] if len(row)>0 else 0)
    ax.bar(x_c+j*bar_w*2-n_bands*bar_w+bar_w/2,rev_vals,width=bar_w,color=sc,alpha=0.9,edgecolor='white',label=f'{band_short} Rev%')
    ax.bar(x_c+j*bar_w*2-n_bands*bar_w+bar_w*1.5,book_vals,width=bar_w,color=sc,alpha=0.35,edgecolor='white',hatch='//',label=f'{band_short} Book%')
ax.set_xticks(x_c); ax.set_xticklabels([f'City {c}' for c in cities])
ax.set_title('C. Revenue vs Booking Share by Star Band — All Cities\n(Solid = Revenue %, Hatched = Booking %)')
ax.set_ylabel('Share of Total (%)')
ax.legend(handles=legend_handles,fontsize=7,loc='upper right',ncol=2); ax.set_ylim(0,70)

# Panel D: price direction
ax=axes[1,1]
city_dir_results=[]
for c,df in dfs.items():
    eh=df[df['lead_time']>=15].groupby('hotel_id')['ADR_USD'].median()
    lh=df[df['lead_time']<=3].groupby('hotel_id')['ADR_USD'].median()
    hd=pd.concat([eh.rename('e'),lh.rename('l')],axis=1).dropna()
    hd['chg']=(hd['l']-hd['e'])/hd['e']*100
    city_dir_results.append({'city':c,'falling':(hd['chg']<-5).mean()*100,
        'stable':((hd['chg']>=-5)&(hd['chg']<=5)).mean()*100,'rising':(hd['chg']>5).mean()*100})
cdr=pd.DataFrame(city_dir_results)
x_d=np.arange(5); bottom=np.zeros(5)
for direction,dcolor in [('falling',BLUE),('stable',AMBER),('rising',RED)]:
    vals=cdr[direction].values
    ax.bar(x_d,vals,bottom=bottom,color=dcolor,edgecolor='white',alpha=0.85,
           label=f'{"Price falls" if direction=="falling" else "Stable" if direction=="stable" else "Price rises"} last-minute')
    for xi,(b,v) in enumerate(zip(bottom,vals)):
        if v>8: ax.text(xi,b+v/2,f'{v:.0f}%',ha='center',va='center',fontsize=9,fontweight='bold',color='white')
    bottom+=vals
ax.set_xticks(x_d); ax.set_xticklabels([f'City {c}' for c in cdr['city']])
ax.set_title('D. Hotel Price Direction by City\n(% rising / stable / falling last-minute)')
ax.set_ylabel('% of Properties'); ax.legend(fontsize=9); ax.set_ylim(0,115)

plt.tight_layout(pad=1.0)
plt.savefig('/home/claude/fig_cross_final.png',dpi=150,bbox_inches='tight')
plt.close()
print("  Slide 13 cross-city final saved.")
print("\n✓ All 3 figures complete.")
