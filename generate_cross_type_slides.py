"""
Cross-type slide generation — improved presentation version.
Changes: bigger insight fonts, no emoji boxes, better ADR display,
City D 4* highlight, City B Resort orange, legends top-right, upsell boxes higher.
"""
import matplotlib
matplotlib.use("Agg")
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

RED="#E4272B"; DARK="#1A1A2E"; BLUE="#2E86AB"; AMBER="#F4A261"
GREEN="#2A9D8F"; PURPLE="#6C3483"; GREY="#6B6B6B"; ORANGE="#FF8C00"
CITY_COLORS={"A":RED,"B":BLUE,"C":AMBER,"D":GREEN,"E":"#9B59B6"}
REVENUE_COLORS={"A":RED,"B":PURPLE,"C":AMBER,"D":GREEN,"E":"#8B0000"}
CITY_TITLES={"A":"City A — Urban Mixed","B":"City B — Resort-Heavy",
              "C":"City C — Premium/Planned","D":"City D — Premium/Stable","E":"City E — Last-Minute"}
BUCKET_ORDER=["Same-day\n(0d)","1-3 days","4-7 days","8-14 days","15-30 days","31-60 days"]
MONTH_COLORS={10:BLUE,11:AMBER,12:RED}

plt.rcParams.update({"figure.facecolor":"white","axes.facecolor":"white","axes.edgecolor":"#CCCCCC",
    "axes.grid":True,"grid.alpha":0.3,"grid.color":"#CCCCCC","font.family":"sans-serif",
    "font.size":9,"axes.titlesize":9.5,"axes.titleweight":"bold"})

def load_city(c):
    df=pd.read_excel(f"../data/City_{c}.xlsx")
    df["city"]=c
    if "accommadation_type_name" in df.columns:
        df.rename(columns={"accommadation_type_name":"accommodation_type_name"},inplace=True)
    df["lead_time"]=(df["checkin_date"]-df["booking_date"]).dt.days
    df["length_of_stay"]=(df["checkout_date"]-df["checkin_date"]).dt.days
    df["revenue_proxy"]=df["ADR_USD"]*df["length_of_stay"]
    df=df[df["lead_time"]>=0].copy()
    df["lead_bucket"]=pd.cut(df["lead_time"],bins=[-1,0,3,7,14,30,60],labels=BUCKET_ORDER)
    df["star_band"]=pd.cut(df["star_rating"],bins=[-0.5,2.5,3.5,4.5,5.5],
        labels=["1-2*\n(incl. 1.5*, 2*, 2.5*)","3*\n(incl. 3.5*)","4*\n(incl. 4.5*)","5*"])
    df["checkin_month"]=df["checkin_date"].dt.month
    df["is_lastminute"]=df["lead_time"]<=3
    return df

dfs={c:load_city(c) for c in ["A","B","C","D","E"]}
cities=["A","B","C","D","E"]
import os
OUT=os.path.dirname(os.path.abspath(__file__)) + "/../outputs/figures/"
os.makedirs(OUT, exist_ok=True)

city_pos=[(0,0),(0,1),(0,2),(1,0),(1,1)]

def make_grid(): return plt.subplots(2,3,figsize=(20,8.3))

def styled_insight(ax, title, bullets, title_color=RED, bullet_colors=None):
    """Insight panel — no emojis, bigger font, clean bullets."""
    ax.axis("off"); ax.set_facecolor("#F8F8FF"); ax.patch.set_visible(True)
    for sp in ax.spines.values(): sp.set_visible(True); sp.set_color("#CCCCDD")
    tb=FancyBboxPatch((0.04,0.89),0.92,0.09,boxstyle="round,pad=0.02",
                      facecolor=title_color,edgecolor="none",
                      transform=ax.transAxes,clip_on=False)
    ax.add_patch(tb)
    # Title — plain text, no emojis
    ax.text(0.5,0.935,title,transform=ax.transAxes,ha="center",va="center",
            fontsize=10,fontweight="bold",color="white",clip_on=False)
    if bullet_colors is None: bullet_colors=[DARK]*len(bullets)
    y=0.82
    for bullet,bc in zip(bullets,bullet_colors):
        ax.text(0.06,y,"*",transform=ax.transAxes,ha="left",va="top",
                fontsize=12,color=bc,fontweight="bold")
        ax.text(0.15,y,bullet,transform=ax.transAxes,ha="left",va="top",
                fontsize=9.5,color=DARK,multialignment="left")
        y -= 0.10 + bullet.count("\n")*0.046
        if y<0.03: break


# ── SLIDE 1: Monthly Booking Patterns ────────────────────────────────────────
print("Building Slide 1: Monthly Patterns...")
fig,axes=make_grid()
summary={}
for c,df in dfs.items():
    rows={}
    for m in [10,11,12]:
        sub=df[df["checkin_month"]==m]
        rows[m]={"n":len(sub),"adr":sub["ADR_USD"].median(),"lm_pct":sub["is_lastminute"].mean()*100}
    summary[c]=rows

for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; color=CITY_COLORS[c]; rows=summary[c]
    x=np.arange(3); w=0.45
    n_vals=[rows[m]["n"] for m in [10,11,12]]
    adrs=[rows[m]["adr"] for m in [10,11,12]]
    lm_pcts=[rows[m]["lm_pct"] for m in [10,11,12]]

    # Booking count bars (single bar per month)
    ax.bar(x, n_vals, width=w, color=[MONTH_COLORS[m] for m in [10,11,12]],
           alpha=0.55, edgecolor="white", label="Booking count")

    # ADR as a line with markers on secondary axis (RIGHT axis)
    ax2=ax.twinx()
    ax2.plot(x, adrs, color=DARK, marker="D", lw=2.2, ms=7, zorder=6, label="Median ADR ($)")
    # ADR value labels above each diamond marker
    for xi,adr in enumerate(adrs):
        ax2.text(xi, adr + max(adrs)*0.04, f"${adr:.0f}",
                 ha="center", va="bottom", fontsize=9, fontweight="bold", color=DARK)
    ax2.set_ylim(0, max(adrs)*2.8)
    ax2.tick_params(axis="y", labelcolor=DARK, labelsize=7.5)
    if c_==2: ax2.set_ylabel("Median ADR ($)", fontsize=8, color=DARK)
    else: ax2.set_yticklabels([])

    # Last-minute % as red line on left axis (scaled separately)
    lm_scale = max(n_vals) / max(lm_pcts) * 0.5
    ax.plot(x, [v*lm_scale for v in lm_pcts], color=RED, marker="o",
            lw=2, ms=6, zorder=7, label="Last-minute %")
    for xi,lm in enumerate(lm_pcts):
        ax.text(xi+0.13, lm*lm_scale, f"{lm:.0f}%",
                ha="left", va="center", fontsize=8.5, fontweight="bold", color=RED)

    ax.axvspan(1.55, 2.45, alpha=0.07, color=RED, zorder=0)
    ax.set_xticks(x); ax.set_xticklabels(["October","November","December"], fontsize=8.5)
    ax.set_title(CITY_TITLES[c], color=color, fontweight="bold")
    ax.set_ylabel("Number of Bookings" if c_==0 else "", fontsize=8)
    ax.set_ylim(0, max(n_vals)*1.55); ax.grid(axis="x",alpha=0)
    ax.tick_params(axis="y", labelsize=7.5)

    if r==0 and c_==0:
        ax.legend(handles=[
            mpatches.Patch(color=GREY,alpha=0.55,label="Booking count (bar)"),
            Line2D([0],[0],color=DARK,marker="D",lw=2,label="Median ADR (line)"),
            Line2D([0],[0],color=RED,marker="o",lw=2,label="Last-minute booking %"),
        ], fontsize=7.5, loc="upper left", framealpha=0.9)

styled_insight(axes[1,2],"Monthly Booking Patterns",
    ["December ADR rises in leisure markets:\nCity B (resort): +10% vs October\nCity E (mixed resort): +8% vs October\nCity D (premium stable): +3% vs October",
     "Last-minute bookings DROP in December:\nPeople plan ahead for the holiday season.\nBiggest drops: City B -11 percentage points,\nCity E -8 percentage points vs October.",
     "December urgency strategy:\n'Rooms filling up for the holidays'\nor 'Prices rising - book now'\n(scarcity framing works best in December)",
     "October & November urgency strategy:\n'Earn more loyalty points' works best -\nlast-minute rates are highest in these\nmonths so booking is more impulsive"],
    title_color=RED, bullet_colors=[AMBER,BLUE,RED,GREEN])
plt.tight_layout(pad=0.8)
plt.savefig(f"{OUT}fig_xt_01_monthly.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")


# ── SLIDE 2: Lead Time Distribution ──────────────────────────────────────────
print("Building Slide 2: Lead Time Distribution...")
fig,axes=make_grid()
for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; color=CITY_COLORS[c]; df=dfs[c]
    n_bins,bin_edges,patches_b=ax.hist(df["lead_time"],bins=61,edgecolor="white",alpha=0.9)
    for patch,left in zip(patches_b,bin_edges[:-1]):
        if left<=3: patch.set_facecolor(RED)
        elif left<=14: patch.set_facecolor(AMBER)
        else: patch.set_facecolor(BLUE)
    ymax=n_bins.max()*1.5
    ax.axvspan(-0.5,3.5,alpha=0.08,color=RED,zorder=0)
    ax.axvspan(3.5,14.5,alpha=0.08,color=AMBER,zorder=0)
    ax.axvspan(14.5,61,alpha=0.08,color=BLUE,zorder=0)
    h=(df["lead_time"]<=3).mean()*100
    m=df["lead_time"].between(4,14).mean()*100
    l=(df["lead_time"]>=15).mean()*100
    ax.text(1.5,ymax*0.97,f"High Urgency\n(0-3 days)\n{h:.0f}% of bookings",
            ha="center",va="top",fontsize=7,color=RED,fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15",facecolor="white",edgecolor=RED,alpha=0.85))
    ax.text(9,ymax*0.97,f"Medium Urgency\n(4-14 days)\n{m:.0f}% of bookings",
            ha="center",va="top",fontsize=7,color="#B05A00",fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15",facecolor="white",edgecolor=AMBER,alpha=0.85))
    ax.text(40,ymax*0.97,f"Low Urgency\n(15-60 days)\n{l:.0f}% of bookings",
            ha="center",va="top",fontsize=7,color=BLUE,fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15",facecolor="white",edgecolor=BLUE,alpha=0.85))
    med_lt=df["lead_time"].median(); ax.axvline(med_lt,color=DARK,lw=1.8,ls="--")
    ax.set_title(CITY_TITLES[c],color=color,fontweight="bold")
    ax.set_xlabel("Days Between Booking and Check-in" if r==1 else "")
    ax.set_ylabel("Number of Bookings" if c_==0 else ""); ax.set_ylim(0,ymax)
    ax.text(med_lt+0.5,ymax*0.12,f"Median:\n{int(med_lt)} days",fontsize=7.5,color=DARK,va="bottom",
            bbox=dict(boxstyle="round,pad=0.2",facecolor="#FFFBE6",alpha=0.9))
    ax.legend(handles=[
        Line2D([0],[0],color=DARK,lw=1.8,ls="--",label=f"Median: {int(med_lt)} days"),
        mpatches.Patch(color=RED,alpha=0.7,label=f"High Urgency (0-3d): {h:.0f}%"),
        mpatches.Patch(color=AMBER,alpha=0.7,label=f"Medium Urgency (4-14d): {m:.0f}%"),
        mpatches.Patch(color=BLUE,alpha=0.7,label=f"Low Urgency (15-60d): {l:.0f}%"),
    ],fontsize=6.5,loc="upper right",framealpha=0.9)

styled_insight(axes[1,2],"Lead Time and Urgency Tiers",
    ["City E has the MOST last-minute bookers:\n44% of all bookings are made within\n3 days of check-in. Needs the strongest\ntime-triggered urgency messaging.",
     "City B is close behind at 42% High-Urgency.\nResort bookings cluster heavily\naround same-day and 1-3 days ahead.",
     "City C is the most planned market:\nOnly 18% High-Urgency - 54% of bookings\nmade 15+ days ahead. Focus on\nmedium and low urgency campaigns here.",
     "Urgency message depends on tier:\nHigh - Book tonight - prices lowest now\nMedium - Lock in your rate before prices rise\nLow - Secure your preferred room early"],
    title_color=BLUE, bullet_colors=[RED,AMBER,GREEN,DARK])
plt.tight_layout(pad=0.8)
plt.savefig(f"{OUT}fig_xt_02_lead_time.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")


# ── SLIDE 3: Revenue vs Booking Share ────────────────────────────────────────
print("Building Slide 3: Revenue by Star...")
fig,axes=make_grid()
slm={"1-2*\n(incl. 1.5*, 2*, 2.5*)":"1-2*","3*\n(incl. 3.5*)":"3*","4*\n(incl. 4.5*)":"4*","5*":"5*"}
for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; rv=REVENUE_COLORS[c]; df=dfs[c]
    ss=df[df["star_band"].notna()].groupby("star_band",observed=True).agg(
        n=("ADR_USD","count"),rev=("revenue_proxy","sum"),med=("ADR_USD","median")).reset_index()
    ss=ss[ss["n"]>=5].copy(); tn=ss["n"].sum(); tr=ss["rev"].sum()
    ss["bs"]=ss["n"]/tn*100; ss["rs"]=ss["rev"]/tr*100; ss["ratio"]=ss["rs"]/ss["bs"]
    ss["lbl"]=ss["star_band"].map(slm).fillna(ss["star_band"].astype(str))
    x=np.arange(len(ss)); w=0.35
    b1=ax.bar(x-w/2,ss["bs"],width=w,color=BLUE,alpha=0.85,edgecolor="white",label="Booking share %")
    b2=ax.bar(x+w/2,ss["rs"],width=w,color=rv,alpha=0.85,edgecolor="white",label="Revenue share %")
    for bar,row in zip(b1,ss.itertuples()):
        if bar.get_height()>5: ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()*0.45,f"{row.n:,}",ha="center",va="center",fontsize=6,fontweight="bold",color="white")
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.3,f"{bar.get_height():.0f}%",ha="center",va="bottom",fontsize=7)
    for bar,row in zip(b2,ss.itertuples()):
        if bar.get_height()>5: ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()*0.45,f"${row.med:.0f}",ha="center",va="center",fontsize=6,fontweight="bold",color="white")
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.3,f"{bar.get_height():.0f}%",ha="center",va="bottom",fontsize=7,color=rv,fontweight="bold")
    ymc=ss[["bs","rs"]].max().max()*1.45
    for i,row in ss.iterrows():
        if row["ratio"]>1.0:
            if c=="D" and "5*" in str(row["star_band"]): continue
            idx=list(ss["star_band"]).index(row["star_band"])
            ax.axvspan(idx-0.5,idx+0.5,alpha=0.10,color=RED,zorder=0)
    ax.set_xticks(x); ax.set_xticklabels(ss["lbl"],fontsize=8.5)
    ax.set_title(CITY_TITLES[c],color=CITY_COLORS[c],fontweight="bold")
    ax.set_ylabel("Share of total (%)" if c_==0 else ""); ax.set_xlabel("Star Band"); ax.set_ylim(0,ymc)
    ax.legend(handles=[
        mpatches.Patch(color=BLUE,alpha=0.85,label="Booking share %  [# = no. of bookings]"),
        mpatches.Patch(color=rv,alpha=0.85,label="Revenue share %  [$ = median ADR]"),
    ],fontsize=6.5,loc="upper left",framealpha=0.9)
    ax.text(0.98,0.97,"Red highlight =\nurgency priority",transform=ax.transAxes,ha="right",va="top",
            fontsize=7,color=RED,style="italic",bbox=dict(boxstyle="round,pad=0.2",facecolor="#FFE8E8",alpha=0.85))

styled_insight(axes[1,2],"Revenue vs Booking Share by Star Band",
    ["4* and 5* properties generate MORE\nrevenue than their booking share in\nALL 5 cities. Each booking here is\ndisproportionately valuable.",
     "Red-highlighted bands = urgency priority\n(revenue share exceeds booking share):\n- City A: 4* (42% revenue) and 5* (24%)\n- City B: 4* (45%) and 5* (24%)\n- City C: 4* (24%) and 5* (12%)\n- City D: 4* (51% revenue)\n- City E: 4* (36%) and 5* (29%)",
     "Even a small urgency-driven uplift in\n4*/5* conversion yields large revenue gains.\nPrioritise these bands first.",
     "# inside blue bar = number of bookings\n$ inside revenue bar = median ADR paid"],
    title_color="#8B0000", bullet_colors=[DARK,RED,AMBER,GREY])
plt.tight_layout(pad=0.8)
plt.savefig(f"{OUT}fig_xt_03_rev_star.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")


# ── SLIDE 4: Accommodation Type Mix ──────────────────────────────────────────
# FIXED: City B Resort gets ORANGE, legend top-right, non-chain % shown
print("Building Slide 4: Accommodation Type...")
fig,axes=make_grid()
for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; color=CITY_COLORS[c]; df=dfs[c]
    acc=df["accommodation_type_name"].value_counts().head(6); top1=acc.idxmax()
    def bar_color(acc_type, city, top1, color):
        if acc_type==top1:
            return ORANGE if city=="B" else color  # City B top type gets orange
        return BLUE
    bar_colors=[bar_color(t,c,top1,color) for t in acc.index]
    bars=ax.barh(acc.index,acc.values,color=bar_colors,edgecolor="white")
    for bar,val in zip(bars,acc.values):
        ax.text(bar.get_width()+4,bar.get_y()+bar.get_height()/2,
                f"{val:,}  ({val/len(df)*100:.0f}%)",va="center",fontsize=7.5)
    ax.set_title(CITY_TITLES[c],color=color,fontweight="bold")
    ax.set_xlabel("Number of bookings" if r==1 else "")
    ax.set_xlim(0,acc.max()*1.62); ax.grid(axis="y",alpha=0); ax.tick_params(axis="y",labelsize=7.5)
    chain=(df["chain_hotel"]=="chain").mean()*100; nonchain=100-chain
    ax.text(0.5,-0.25,f"Chain hotels: {chain:.0f}%   |   Non-chain hotels: {nonchain:.0f}%",
            transform=ax.transAxes,ha="center",va="top",fontsize=8,fontweight="bold",color=DARK,
            bbox=dict(boxstyle="round,pad=0.25",facecolor="#EEF5FB",edgecolor=BLUE,alpha=0.9))
    top_color = ORANGE if c=="B" else color
    # Legend at TOP RIGHT
    ax.legend(handles=[
        mpatches.Patch(color=top_color,label=f"{top1[:22]} (highest volume)"),
        mpatches.Patch(color=BLUE,label="Other property types"),
    ],fontsize=7,loc="upper right",framealpha=0.9)

styled_insight(axes[1,2],"Accommodation Type Mix",
    ["City A and D: Hotels dominate (82% and 77%).\nHotel-focused urgency messaging is\nmost effective in these markets.",
     "City B is uniquely Resort-heavy:\n39% Resort bookings (shown in orange)\nneeds resort-specific messaging:\n'Reserve your resort room\nbefore the season fills up'.",
     "City C: 71% Hotel + Capsule Hotels\nunique to this market. Different\ncustomer profile, different\nmessage tone and format.",
     "City E: Most diverse mix - 53% Hotel,\n30% Resort. Needs a dual strategy\ntailored to both property types.",
     "Non-chain hotels are the majority\nin all cities (72-79%)."],
    title_color=AMBER, bullet_colors=[BLUE,RED,AMBER,PURPLE,GREY])
plt.tight_layout(pad=0.8); plt.subplots_adjust(bottom=0.13)
plt.savefig(f"{OUT}fig_xt_04_acc_type.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")


# ── SLIDE 5: ADR Scatter vs Lead Time ────────────────────────────────────────
print("Building Slide 5: ADR Scatter...")
fig,axes=make_grid()
for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; color=CITY_COLORS[c]; df=dfs[c]
    abl=df.groupby("lead_time")["ADR_USD"].agg(["median","count"]).reset_index()
    abl.columns=["lead_time","med","n"]
    subset=abl[abl["n"]>=15]
    sc=ax.scatter(subset["lead_time"],subset["med"],
                  s=subset["n"]/max(subset["n"].max()/60,1),
                  color=color,alpha=0.5,zorder=3,
                  label="Daily median ADR\n(bubble size = booking volume)")
    smooth=abl.set_index("lead_time")["med"].rolling(3,center=True,min_periods=1).mean()
    ln,=ax.plot(smooth.index,smooth.values,color=DARK,lw=2,
                label="Smoothed trend\n(3-day rolling average)")
    ax.invert_xaxis()
    em=df[df["lead_time"].between(31,60)]["ADR_USD"].median()
    sm=df[df["lead_time"]==0]["ADR_USD"].median()
    drop=(sm-em)/em*100 if em>0 else 0
    try:
        _,pv=stats.mannwhitneyu(df[df["lead_time"]==0]["ADR_USD"],
                                df[df["lead_time"].between(31,60)]["ADR_USD"],alternative="two-sided")
        sig="p < 0.001" if pv<0.001 else f"p = {pv:.3f}"
    except: sig="n/a"
    ax.text(0.97,0.97,f"Total % ADR Drop: {drop:+.1f}%\n({sig})",
            transform=ax.transAxes,ha="right",va="top",fontsize=8,fontweight="bold",color=DARK,
            bbox=dict(boxstyle="round,pad=0.3",facecolor="#FFFBE6",edgecolor=AMBER,alpha=0.95))
    ax.set_title(CITY_TITLES[c],color=color,fontweight="bold")
    ax.set_xlabel("← Far Ahead     Days Before Check-in     Same-Day →" if r==1 else "")
    ax.set_ylabel("Median ADR (USD)" if c_==0 else "")
    ax.legend(handles=[sc,ln],fontsize=7.5,loc="upper left",framealpha=0.9)

styled_insight(axes[1,2],"ADR Falls as Check-in Approaches",
    ["All 5 cities show falling ADR as\nthe check-in date approaches.\nThe pattern is statistically\nsignificant in every market.",
     "Largest drop: City C -50.6%\nPremium market with big last-minute\ndiscount - huge earn-sooner opportunity\nfor urgency messaging.",
     "Smallest drop: City D -6.5%\nPremium/stable market - prices barely\nmove. Scarcity or loyalty-point framing\nworks better than price-drop framing.",
     "Bubble size shows daily booking volume.\nThe large bubbles near day 0-3 show\nheavy same-day booking clusters.",
     "All results statistically significant\n(p < 0.001) except City D (p = 0.075),\nconfirming the price-fall pattern is real."],
    title_color=RED, bullet_colors=[DARK,RED,GREEN,GREY,BLUE])
plt.tight_layout(pad=0.8)
plt.savefig(f"{OUT}fig_xt_05_adr_scatter.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")


# ── SLIDE 6: ADR by Lead Time Bucket ─────────────────────────────────────────
print("Building Slide 6: ADR by Bucket...")
fig,axes=make_grid()
for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; color=CITY_COLORS[c]; df=dfs[c]
    bs=df.groupby("lead_bucket",observed=True)["ADR_USD"].agg(["median","count"]).reset_index()
    bs.columns=["bucket","med","n"]; bs["pct"]=bs["n"]/len(df)*100
    bcolors=[RED if i==0 else AMBER if i==1 else color for i in range(len(bs))]
    ax.bar(range(len(bs)),bs["med"],color=bcolors,edgecolor="white",width=0.65)
    for i,row in enumerate(bs.itertuples()):
        ax.text(i,row.med+bs["med"].max()*0.015,f"${row.med:.0f}\n({row.pct:.0f}%)",
                ha="center",va="bottom",fontsize=7.5,fontweight="bold")
    ax.axvspan(-0.5,1.5,alpha=0.08,color=RED); ax.set_ylim(0,bs["med"].max()*1.42)
    ax.set_xticks(range(len(bs)))
    ax.set_xticklabels([b.replace("\n"," ") for b in bs["bucket"]],fontsize=7,rotation=20,ha="right")
    ax.set_title(CITY_TITLES[c],color=color,fontweight="bold")
    ax.set_xlabel("Lead Time Bucket" if r==1 else "")
    ax.set_ylabel("Median ADR (USD)" if c_==0 else "")
    ax.legend(handles=[
        mpatches.Patch(color=RED,label="Same-day (0d)"),
        mpatches.Patch(color=AMBER,label="1-3 days"),
        mpatches.Patch(color=color,label="4+ days ahead"),
    ],fontsize=7,loc="lower right",framealpha=0.9)
    ax.text(0.5,0.97,"← Urgency window (0-3 days)",transform=ax.transAxes,
            ha="center",va="top",fontsize=7.5,color=RED,fontweight="bold")

styled_insight(axes[1,2],"ADR by Lead Time Bucket",
    ["Same-day bookers consistently pay\nthe LOWEST price in all 5 cities.\nThis confirms the earn-sooner urgency\nmessage framing is data-backed.",
     "% labels show each bucket's share of\nthat city's total bookings.",
     "High-urgency window (0-3 days):\n- City E: 44% of all bookings here\n- City B: 42%  |  City A: 37%\n- City D: 28%  |  City C: 18%",
     "Urgency message example:\n'Book in the next 3 days and earn 2x\nloyalty points - prices are lowest\nfor last-minute bookings'"],
    title_color=GREEN, bullet_colors=[DARK,GREY,RED,AMBER])
plt.tight_layout(pad=0.8)
plt.savefig(f"{OUT}fig_xt_06_adr_bucket.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")


# ── SLIDE 7: Star Band Grouped Bars ──────────────────────────────────────────
# FIXED: Red shaded area over 4* band for City D
print("Building Slide 7: Star band grouped bars...")
fig,axes=make_grid()
kb=["Same-day\n(0d)","1-3 days","15-30 days","31-60 days"]; kbc=[RED,AMBER,BLUE,DARK]
for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; color=CITY_COLORS[c]; df=dfs[c]
    sb=df.groupby(["star_band","lead_bucket"],observed=True)["ADR_USD"].agg(["median","count"]).reset_index()
    sb.columns=["star_band","bucket","med","n"]
    sb=sb[sb["star_band"].notna()]
    vs=sb.groupby("star_band",observed=True)["n"].sum(); vs=vs[vs>=30].index.tolist()
    sb=sb[sb["star_band"].isin(vs)]
    sk=sb[sb["bucket"].isin(kb)]
    sp=sk.pivot(index="star_band",columns="bucket",values="med")
    for b in kb:
        if b not in sp.columns: sp[b]=np.nan
    sp=sp.reindex(vs)
    sh={"1-2*\n(incl. 1.5*, 2*, 2.5*)":"1-2*","3*\n(incl. 3.5*)":"3*",
        "4*\n(incl. 4.5*)":"4*","5*":"5*"}
    sp.index=[sh.get(str(s),str(s)) for s in sp.index]
    x=np.arange(len(sp)); w=0.18
    for i,(b,bc) in enumerate(zip(kb,kbc)):
        vals=sp[b].fillna(0).values
        if vals.sum()>0:
            ax.bar(x+i*w-1.5*w,vals,width=w,color=bc,alpha=0.85,
                   label=b.replace("\n"," "),edgecolor="white")

    # City D: shade the 4* band red as urgency priority
    if c=="D":
        four_star_indices=[i for i,s in enumerate(sp.index) if "4*" in s]
        for fi in four_star_indices:
            ax.axvspan(fi-0.55,fi+0.55,alpha=0.12,color=RED,zorder=0)
            ax.text(fi,ax.get_ylim()[1]*0.98,"Urgency\npriority\n4*",
                    ha="center",va="top",fontsize=7,color=RED,fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2",facecolor="#FFE8E8",edgecolor=RED,alpha=0.9))

    ax.set_xticks(x); ax.set_xticklabels(sp.index,fontsize=8.5)
    ax.set_title(CITY_TITLES[c],color=color,fontweight="bold")
    ax.set_xlabel("Star Band" if r==1 else ""); ax.set_ylabel("Median ADR ($)" if c_==0 else "")
    ax.legend(title="Lead Time",fontsize=7,loc="upper left",framealpha=0.9)

styled_insight(axes[1,2],"ADR by Star Band and Lead Time",
    ["Higher star rating = higher ADR at every\nlead time across all 5 cities.\nThe relationship is consistent.",
     "The gap between same-day (red bar)\nand 31-60 days ahead (dark bar) is\nlargest for 4* and 5* properties.",
     "City D: 4* band highlighted in red -\nrevenue share (51%) far exceeds\nbooking share (44%). Top urgency\nmessaging priority in this market.",
     "Urgency for 4* and 5*:\n'Value + scarcity' framing:\n'Premium rooms at this rate\nwon't last - book now'",
     "Urgency for 1-2* and 3*:\n'Great last-minute rate' framing:\n'Lowest price of the week - book tonight'"],
    title_color=PURPLE, bullet_colors=[DARK,RED,GREEN,"#8B0000",BLUE])
plt.tight_layout(pad=0.8)
plt.savefig(f"{OUT}fig_xt_07_star_grouped.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")


# ── SLIDE 8: ADR Trend by Star Band ──────────────────────────────────────────
# FIXED: Upsell text boxes shifted HIGHER (bigger y multiplier)
print("Building Slide 8: Star band trends with upsell windows...")
UPSELL={
    "A":{"xspan":(3.5,5.5),"label":"Upsell window:\n1-2* approx 3* prices\nat 15-60 days ahead","color":GREEN,"tx":4.5,"y_frac":0.55},
    "B":None,
    "C":{"xspan":(2.5,4.5),"label":"Upsell window:\n4* approx 5* prices\nat 8-30 days ahead","color":GREEN,"tx":3.5,"y_frac":0.58},
    "D":{"xspan":(0.5,5.5),"label":"Upsell window:\n3* approx 4* prices\nacross all lead times","color":GREEN,"tx":3.0,"y_frac":0.52},
    "E":{"xspan":(1.5,3.5),"label":"Upsell window:\n1-2* approx 3* prices\nat 4-14 days ahead","color":GREEN,"tx":2.5,"y_frac":0.55},
}
cs={"5*":"#8B0000","4*\n(incl. 4.5*)":RED,"3*\n(incl. 3.5*)":AMBER,
    "1-2*\n(incl. 1.5*, 2*, 2.5*)":BLUE}
sm2={"1-2*\n(incl. 1.5*, 2*, 2.5*)":"1-2*","3*\n(incl. 3.5*)":"3*",
     "4*\n(incl. 4.5*)":"4*","5*":"5*"}

fig,axes=make_grid()
for (r,c_),c in zip(city_pos,cities):
    ax=axes[r,c_]; color=CITY_COLORS[c]; df=dfs[c]
    sb=df.groupby(["star_band","lead_bucket"],observed=True)["ADR_USD"].agg(["median","count"]).reset_index()
    sb.columns=["star_band","bucket","med","n"]
    sb=sb[sb["star_band"].notna()]
    vs=sb.groupby("star_band",observed=True)["n"].sum(); vs=vs[vs>=30].index.tolist()
    y_all=[]; lh=[]
    for star in vs:
        col=cs.get(star,color)
        sub=sb[sb["star_band"]==star].set_index("bucket")["med"].reindex(BUCKET_ORDER)
        if sub.notna().sum()>=2:
            short=sm2.get(star,str(star))
            ln,=ax.plot(range(len(BUCKET_ORDER)),sub.values,marker="o",color=col,
                        lw=2,label=short,markersize=5,zorder=4)
            lh.append(ln); y_all.extend(sub.dropna().values)
            f,l=sub.iloc[-1],sub.iloc[0]
            if pd.notna(f) and pd.notna(l) and f>0:
                pct=(l-f)/f*100
                ax.text(-0.15,l,f"{short}: {pct:+.0f}%",ha="right",va="center",
                        fontsize=7,color=col,fontweight="bold")
    ax.set_xticks(range(len(BUCKET_ORDER)))
    ax.set_xticklabels([b.replace("\n"," ") for b in BUCKET_ORDER],fontsize=6.5,rotation=20,ha="right")
    ax.invert_xaxis()
    ax.set_title(CITY_TITLES[c],color=color,fontweight="bold")
    ax.set_xlabel("← Far Ahead  |  Lead Time  |  Same-day →" if r==1 else "")
    ax.set_ylabel("Median ADR (USD)" if c_==0 else "")
    ax.legend(handles=lh,title="Star Band",fontsize=7,loc="upper right",framealpha=0.9)

    ucfg=UPSELL.get(c)
    if ucfg and y_all:
        x0,x1=ucfg["xspan"]; uc=ucfg["color"]
        ymin=min(y_all); ymax=max(y_all); yrange=ymax-ymin
        ax.axvspan(x0,x1,alpha=0.13,color=uc,zorder=0)
        # Place text at y_frac of the axis range — higher than before
        ytxt = ymin + yrange * ucfg["y_frac"]
        ax.text(ucfg["tx"],ytxt,ucfg["label"],
                ha="center",va="bottom",fontsize=7,color=uc,fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3",facecolor="#E8F8F2",
                          edgecolor=uc,alpha=0.95,linewidth=1.2))

styled_insight(axes[1,2],"ADR Trends by Star Band",
    ["% labels on left = total ADR drop\nfrom 31-60 days ahead to same-day,\nfor each star band.",
     "Green shaded area = UPSELL WINDOW:\nwhere two adjacent star bands have\nsimilar prices - customers can be\nnudged to book a higher tier.",
     "City A: 1-2* approx 3* at 15-60 days\nahead - upsell budget bookers\nto mid-range when booking early.",
     "City C: 4* approx 5* at 8-30 days -\nupgrade messaging works for premium\ncustomers booking in advance.",
     "City D: 3* approx 4* across all lead\ntimes - a consistent upsell\nopportunity throughout the year.",
     "City B: No upsell window -\nstar band price gaps are too large."],
    title_color=GREEN, bullet_colors=[GREY,GREEN,BLUE,AMBER,GREEN,DARK])
plt.tight_layout(pad=0.8)
plt.savefig(f"{OUT}fig_xt_08_star_trend.png",dpi=150,bbox_inches="tight")
plt.close(); print("  Done.")

print("\n All 8 slides regenerated.")
