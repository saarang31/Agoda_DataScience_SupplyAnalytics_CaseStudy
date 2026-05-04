"""
Final corrected figures:
1. Graph D: only #1 accommodation type gets city color, all others blue
2. Graph C: highlight bands where revenue/booking ratio > 1.0 (not just highest revenue)
   City D: highlight both 4★ and 5★ as user requested
3. Slide 14+15 condensed: new 4-panel cross-city combined figure
   Panel A: ADR trend (no upsell window, no red urgency highlight)
   Panel B: urgency tier share per city
   Panel C: revenue vs booking share per city
   Panel D: price direction per city
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
BUCKET_ORDER=['Same-day\n(0d)','1–3 days','4–7 days','8–14 days','15–30 days','31–60 days']

plt.rcParams.update({'figure.facecolor':'white','axes.facecolor':'white','axes.edgecolor':'#CCCCCC',
    'axes.grid':True,'grid.alpha':0.35,'grid.color':'#CCCCCC','font.family':'sans-serif',
    'font.size':10,'axes.titlesize':11,'axes.titleweight':'bold'})

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
    return df

dfs={c:load_city(c) for c in ['A','B','C','D','E']}

def make_eda(city, df):
    """Rebuilt EDA with corrected Graph C and D logic."""
    color=CITY_COLORS[city]; rev_color=REVENUE_COLORS[city]
    df_no_out=df[df['ADR_USD']<=1000].copy()
    n_out=len(df)-len(df_no_out)
    chain_n=(df['chain_hotel']=='chain').sum(); nonchain_n=(df['chain_hotel']=='non-chain').sum()

    # Star summary with ratio
    star_summary=df[df['star_band'].notna()].groupby('star_band',observed=True).agg(
        n_bookings=('ADR_USD','count'),total_revenue=('revenue_proxy','sum'),
        median_adr=('ADR_USD','median')).reset_index()
    star_summary=star_summary[star_summary['n_bookings']>=5].copy()
    total_n=star_summary['n_bookings'].sum(); total_rev=star_summary['total_revenue'].sum()
    star_summary['booking_share']=star_summary['n_bookings']/total_n*100
    star_summary['revenue_share']=star_summary['total_revenue']/total_rev*100
    star_summary['ratio']=star_summary['revenue_share']/star_summary['booking_share']

    fig,axes=plt.subplots(2,2,figsize=(20,8.3))

    # Panel A: ADR distribution
    ax=axes[0,0]
    if n_out>0:
        ax.hist(df['ADR_USD'],bins=60,color=GREY,alpha=0.3,edgecolor='white',label=f'With {n_out} outlier(s) >$1,000')
        ax.hist(df_no_out['ADR_USD'],bins=60,color=color,alpha=0.8,edgecolor='white',label='Outliers removed')
    else:
        ax.hist(df['ADR_USD'],bins=60,color=color,alpha=0.8,edgecolor='white')
    med_val=df_no_out['ADR_USD'].median()
    ax.axvline(med_val,color=DARK,lw=2,ls='--')
    p25,p75=df_no_out['ADR_USD'].quantile([0.25,0.75])
    legend_handles=[Line2D([0],[0],color=DARK,lw=2,ls='--',label=f'Median ADR: ${med_val:.0f}')]
    if n_out>0:
        legend_handles+=[mpatches.Patch(color=GREY,alpha=0.4,label=f'Incl. {n_out} outlier(s) >$1,000'),
                         mpatches.Patch(color=color,alpha=0.8,label='Outliers removed')]
    ax.legend(handles=legend_handles,fontsize=8.5)
    counts,_=np.histogram(df_no_out['ADR_USD'],bins=60); ymax_a=counts.max()*1.15
    xtxt=min(p75+50,df_no_out['ADR_USD'].quantile(0.92))
    ax.annotate(f'50% of bookings\nfall between ${p25:.0f} – ${p75:.0f}',
                xy=(med_val,ymax_a*0.50),xytext=(xtxt,ymax_a*0.72),fontsize=9,color=DARK,
                arrowprops=dict(arrowstyle='->',color=DARK,lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3',facecolor='#FFFBE6',alpha=0.9))
    ax.set_title('A. ADR Distribution'); ax.set_xlabel('ADR (USD)'); ax.set_ylabel('Number of Bookings')
    ax.set_xlim(0,min(df['ADR_USD'].quantile(0.99)*1.1,1000))

    # Panel B: Lead time urgency tiers
    ax=axes[0,1]
    lead_vals=df['lead_time'].values
    n_bins,bin_edges,patches_b=ax.hist(lead_vals,bins=61,edgecolor='white',alpha=0.9)
    for patch,left in zip(patches_b,bin_edges[:-1]):
        if left<=3: patch.set_facecolor(RED)
        elif left<=14: patch.set_facecolor(AMBER)
        else: patch.set_facecolor(BLUE)
    ymax=n_bins.max()*1.3
    ax.axvspan(-0.5,3.5,alpha=0.06,color=RED,zorder=0)
    ax.axvspan(3.5,14.5,alpha=0.06,color=AMBER,zorder=0)
    ax.axvspan(14.5,61,alpha=0.06,color=BLUE,zorder=0)
    h_pct=(df['lead_time']<=3).mean()*100
    m_pct=df['lead_time'].between(4,14).mean()*100
    l_pct=(df['lead_time']>=15).mean()*100
    ax.text(1.5,ymax*0.93,f'HIGH\nURGENCY\n0–3d\n{h_pct:.1f}%',ha='center',va='top',fontsize=8,color=RED,fontweight='bold')
    ax.text(9,ymax*0.93,f'MEDIUM\nURGENCY\n4–14d\n{m_pct:.1f}%',ha='center',va='top',fontsize=8,color='#B05A00',fontweight='bold')
    ax.text(38,ymax*0.93,f'LOW\nURGENCY\n15–60d\n{l_pct:.1f}%',ha='center',va='top',fontsize=8,color=BLUE,fontweight='bold')
    med_lt=df['lead_time'].median()
    ax.axvline(med_lt,color=DARK,lw=2,ls='--')
    ax.legend(handles=[Line2D([0],[0],color=DARK,lw=2,ls='--',label=f'Median lead time: {int(med_lt)} days'),
                       mpatches.Patch(color=RED,alpha=0.7,label='High Urgency (0–3d)'),
                       mpatches.Patch(color=AMBER,alpha=0.7,label='Medium Urgency (4–14d)'),
                       mpatches.Patch(color=BLUE,alpha=0.7,label='Low Urgency (15–60d)')],fontsize=7.5,loc='upper right')
    ax.set_title('B. Lead Time Distribution (Coloured by urgency tier)')
    ax.set_xlabel('Days Between Booking and Check-in'); ax.set_ylabel('Number of Bookings'); ax.set_ylim(0,ymax)

    # Panel C: Revenue vs booking share — CORRECTED: highlight where ratio > 1
    ax=axes[1,0]
    x=np.arange(len(star_summary)); w=0.35
    bars1=ax.bar(x-w/2,star_summary['booking_share'],width=w,color=BLUE,alpha=0.85,edgecolor='white')
    bars2=ax.bar(x+w/2,star_summary['revenue_share'],width=w,color=rev_color,alpha=0.85,edgecolor='white')
    for bar,row in zip(bars1,star_summary.itertuples()):
        if bar.get_height()>5:
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()*0.45,f'{row.n_bookings:,}',
                    ha='center',va='center',fontsize=7,fontweight='bold',color='white')
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.3,f'{bar.get_height():.0f}%',
                ha='center',va='bottom',fontsize=7.5)
    for bar,row in zip(bars2,star_summary.itertuples()):
        if bar.get_height()>5:
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()*0.45,f'${row.median_adr:.0f}',
                    ha='center',va='center',fontsize=7,fontweight='bold',color='white')
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.3,f'{bar.get_height():.0f}%',
                ha='center',va='bottom',fontsize=7.5,color=rev_color,fontweight='bold')

    # Highlight bands where revenue/booking ratio > 1.0 (revenue share exceeds booking share)
    priority_bands = star_summary[star_summary['ratio'] > 1.0]
    # City D override: user specifically wants 4★ AND 5★ highlighted
    if city == 'D':
        priority_bands = star_summary[star_summary['star_band'].str.contains('4★|5★',na=False)]

    ymax_c=star_summary[['booking_share','revenue_share']].max().max()*1.38
    for _,prow in priority_bands.iterrows():
        pidx=list(star_summary['star_band']).index(prow['star_band'])
        ax.axvspan(pidx-0.5,pidx+0.5,alpha=0.10,color=RED,zorder=0)

    # Annotation pointing to the priority band(s)
    if len(priority_bands)>0:
        # Find the highest-ratio band for annotation
        top_ratio_idx = priority_bands['ratio'].idxmax()
        top_pidx = list(star_summary['star_band']).index(priority_bands.loc[top_ratio_idx,'star_band'])
        top_ratio = priority_bands.loc[top_ratio_idx,'ratio']
        ax.annotate('Urgency priority:\nrevenue share >\nbooking share here',
                    xy=(top_pidx+w/2, star_summary.loc[top_ratio_idx,'revenue_share']+0.5),
                    xytext=(top_pidx+1.3, ymax_c*0.85),
                    fontsize=7.5,color=RED,fontweight='bold',
                    arrowprops=dict(arrowstyle='->',color=RED,lw=1.2),
                    bbox=dict(boxstyle='round,pad=0.2',facecolor='#FFE8E8',alpha=0.9))

    ax.set_xticks(x); ax.set_xticklabels(star_summary['star_band'],fontsize=8)
    ax.set_title('C. Booking Volume vs Revenue Share by Star Band\n(Highlighted = bands where revenue share exceeds booking share)')
    ax.set_ylabel('Share of Total (%)'); ax.set_xlabel('Star Band')
    ax.legend(handles=[mpatches.Patch(color=BLUE,alpha=0.85,label='Share of Bookings (%)  [# = Number of Bookings]'),
                       mpatches.Patch(color=rev_color,alpha=0.85,label='Share of Revenue (%)  [$ = Median ADR]')],fontsize=8,loc='upper left')
    ax.set_ylim(0,ymax_c)

    # Panel D: Accommodation type — CORRECTED: only #1 type gets city color, all others blue
    ax=axes[1,1]
    acc_counts=df['accommodation_type_name'].value_counts()
    acc_sorted=acc_counts.sort_values(ascending=True)
    top1_type=acc_counts.idxmax()
    bar_cols_d=[color if acc_type==top1_type else BLUE for acc_type in acc_sorted.index]
    bars=ax.barh(acc_sorted.index,acc_sorted.values,color=bar_cols_d,edgecolor='white')
    for bar,val in zip(bars,acc_sorted.values):
        ax.text(bar.get_width()+5,bar.get_y()+bar.get_height()/2,
                f'{val:,}  ({val/len(df)*100:.1f}%)',va='center',fontsize=8.5)
    # Urgency annotation on the top type only
    top_val=acc_counts.max()
    top_idx=list(acc_sorted.index).index(top1_type)
    ax.annotate('Highest-volume type:\npriority for urgency\nmessaging reach',
                xy=(top_val*0.85, top_idx),
                xytext=(top_val*0.5, max(0,top_idx-2)),
                fontsize=7.5,color=RED,fontweight='bold',
                arrowprops=dict(arrowstyle='->',color=RED,lw=1.2),
                bbox=dict(boxstyle='round,pad=0.2',facecolor='#FFE8E8',alpha=0.9))
    ax.set_title(f'D. Accommodation Type Mix\n({top1_type} = highest volume → urgency messaging priority)')
    ax.set_xlabel('Number of Bookings'); ax.set_xlim(0,acc_sorted.max()*1.65); ax.grid(axis='y',alpha=0)
    ax.text(0.5,-0.16,
            f'Chain bookings: {chain_n:,} ({chain_n/len(df)*100:.1f}%)          '
            f'Non-chain bookings: {nonchain_n:,} ({nonchain_n/len(df)*100:.1f}%)',
            transform=ax.transAxes,ha='center',va='top',fontsize=9,fontweight='bold',color=DARK,
            bbox=dict(boxstyle='round,pad=0.3',facecolor='#EEF5FB',edgecolor=BLUE,alpha=0.95))

    plt.tight_layout(pad=1.0); plt.subplots_adjust(bottom=0.09)
    plt.savefig(f'/home/claude/fig_{city}_eda.png',dpi=150,bbox_inches='tight')
    plt.close()
    print(f"  City {city} EDA saved.")

for city in ['A','B','C','D','E']:
    make_eda(city, dfs[city])

# ─────────────────────────────────────────────────────────────────────────────
# NEW CONDENSED CROSS-CITY SLIDE (replaces slides 14 and 15)
# Panel A: ADR trend (clean — no upsell, no red urgency region)
# Panel B: Urgency tier share per city
# Panel C: Revenue vs booking share per city
# Panel D: Price direction per city
# ─────────────────────────────────────────────────────────────────────────────
all_df=pd.concat(dfs.values(),ignore_index=True)
all_df['lead_bucket']=pd.cut(all_df['lead_time'],bins=[-1,0,3,7,14,30,60],labels=BUCKET_ORDER)
all_df['urgency']=pd.cut(all_df['lead_time'],bins=[-1,3,14,60],
    labels=['High Urgency\n(0–3d)','Medium Urgency\n(4–14d)','Low Urgency\n(15–60d)'])
all_df['star_band']=pd.cut(all_df['star_rating'],bins=[-0.5,2.5,3.5,4.5,5.5],
    labels=['1–2★\n(incl. 1.5★, 2★, 2.5★)','3★\n(incl. 3.5★)','4★\n(incl. 4.5★)','5★'])

cities=['A','B','C','D','E']
city_bucket=(all_df.groupby(['city','lead_bucket'],observed=True)['ADR_USD']
             .agg(['median','count']).reset_index().rename(columns={'median':'median_adr','count':'n'}))
city_total=all_df.groupby('city')['ADR_USD'].count().rename('total')
city_bucket=city_bucket.merge(city_total,on='city')
city_bucket['pct_bookings']=city_bucket['n']/city_bucket['total']*100

city_drop={}
for c,df in dfs.items():
    em=df[df['lead_time'].between(31,60)]['ADR_USD'].median()
    sm=df[df['lead_time']==0]['ADR_USD'].median()
    city_drop[c]={'early':em,'same':sm,'drop':(sm-em)/em*100 if em>0 else 0}

fig,axes=plt.subplots(2,2,figsize=(20,8.3))

# Panel A: ADR trend — CLEAN (no upsell window, no red region)
ax=axes[0,0]
city_vals={}
for c in cities:
    sub=city_bucket[city_bucket['city']==c].set_index('lead_bucket')['median_adr']
    sub=sub.reindex(BUCKET_ORDER)
    city_vals[c]=sub
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
ax.set_xticks(range(len(BUCKET_ORDER)))
ax.set_xticklabels(BUCKET_ORDER,fontsize=8.5,rotation=10,ha='right')
ax.invert_xaxis()
ax.set_title('A. Median ADR by Lead Time — All 5 Cities\n(% drop shown per city at same-day point)')
ax.set_xlabel('← Booked Far Ahead       Lead Time       Same-day →')
ax.set_ylabel('Median ADR (USD)')
ax.legend(title='City',fontsize=9,loc='upper right')
ax.text(0.98,0.98,'All 5 cities show prices\nfalling as check-in approaches.\nMagnitude differs significantly.',
        transform=ax.transAxes,va='top',ha='right',fontsize=8,style='italic',color=DARK,
        bbox=dict(boxstyle='round,pad=0.2',facecolor='#FFFBE6',alpha=0.7))

# Panel B: Urgency tier share per city (grouped bars)
ax=axes[0,1]
urgency_share=(all_df.groupby(['city','urgency'],observed=True).size().reset_index(name='n'))
city_totals_u=urgency_share.groupby('city')['n'].transform('sum')
urgency_share['pct']=urgency_share['n']/city_totals_u*100
urgency_pivot=urgency_share.pivot_table(index='city',columns='urgency',values='pct',observed=True).fillna(0)
x_u=np.arange(5); w_u=0.25
for j,(col,uc) in enumerate(zip(['High Urgency\n(0–3d)','Medium Urgency\n(4–14d)','Low Urgency\n(15–60d)'],[RED,AMBER,BLUE])):
    if col in urgency_pivot.columns:
        vals=urgency_pivot[col].values
        bars=ax.bar(x_u+j*w_u-w_u,vals,width=w_u,color=uc,alpha=0.85,label=col.replace('\n',' '),edgecolor='white')
        for bar,v in zip(bars,vals):
            if v>8: ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.5,f'{v:.0f}%',ha='center',va='bottom',fontsize=7.5,fontweight='bold',color=uc)
ax.set_xticks(x_u); ax.set_xticklabels([f'City {c}' for c in urgency_pivot.index])
ax.set_title('B. Lead Time Urgency Tier Share per City\n(Cities E & B show highest High-Urgency share → different messaging needed)')
ax.set_ylabel("% of City's Bookings"); ax.set_ylim(0,75); ax.legend(title='Urgency Tier',fontsize=9)
ax.axhline(34,color=DARK,lw=1.2,ls='--',alpha=0.5); ax.text(4.6,35,'Avg',fontsize=8,color=DARK,alpha=0.7)

# Panel C: Revenue vs booking share per city (from old slide 14)
ax=axes[1,0]
star_bands_short=['1–2★','3★','4★','5★']
star_band_keys=['1–2★\n(incl. 1.5★, 2★, 2.5★)','3★\n(incl. 3.5★)','4★\n(incl. 4.5★)','5★']
star_colors=[BLUE,AMBER,RED,'#8B0000']
city_star_rev={}
for c,df in dfs.items():
    sub=df[df['star_band'].notna()]
    grp=sub.groupby('star_band',observed=True).agg(n=('ADR_USD','count'),rev=('revenue_proxy','sum')).reset_index()
    total_n_=grp['n'].sum(); total_rev_=grp['rev'].sum()
    grp['book_share']=grp['n']/total_n_*100
    grp['rev_share']=grp['rev']/total_rev_*100
    city_star_rev[c]=grp
x_c=np.arange(5); n_bands=4; bar_w=0.09
for j,(band_key,band_short,sc) in enumerate(zip(star_band_keys,star_bands_short,star_colors)):
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
legend_handles=[mpatches.Patch(color=sc,alpha=0.9,label=f'{bs} Revenue%') for bs,sc in zip(star_bands_short,star_colors)] + \
               [mpatches.Patch(color=sc,alpha=0.35,label=f'{bs} Booking%',hatch='//') for bs,sc in zip(star_bands_short,star_colors)]
ax.legend(handles=legend_handles,fontsize=7,loc='upper right',ncol=2); ax.set_ylim(0,70)

# Panel D: Price direction per city (from old slide 14)
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
print("Cross-city condensed figure saved.")
print("\n✓ All figures complete.")
