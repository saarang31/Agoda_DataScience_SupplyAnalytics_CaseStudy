const path = require("path");
const pptxgen = require("pptxgenjs");
const fs = require("fs");

const C = {
  red:"E4272B", dark:"1A1A2E", white:"FFFFFF",
  offwhite:"F7F7F7", grey:"6B6B6B", ltgrey:"F0F0F5",
  amber:"F4A261", blue:"2E86AB", green:"2A9D8F",
};
const CITY_COLORS={A:"E4272B",B:"2E86AB",C:"F4A261",D:"2A9D8F",E:"9B59B6"};
const CITY_NAMES={
  A:"City A — Urban Mixed Market", B:"City B — Resort-Heavy Market",
  C:"City C — Premium, Plans-Ahead Market", D:"City D — Premium, Price-Stable Market",
  E:"City E — Most Last-Minute Market",
};
const CITY_DROPS={A:"-12.9%",B:"-30.9%",C:"-50.6%",D:"-6.5%",E:"-12.8%"};
const CITY_N={A:"22,365",B:"4,932",C:"6,797",D:"10,152",E:"4,815"};
const CITY_LAST3_PCT={A:"37.5%",B:"41.6%",C:"17.8%",D:"28.5%",E:"44.1%"};

const FIGURES_DIR = path.join(__dirname, "../outputs/figures/");
function imgData(n){return "image/png;base64,"+fs.readFileSync(path.join(FIGURES_DIR, n+".png")).toString("base64");}
function lightBg(s){s.background={color:C.white};}
function darkBg(s){s.background={color:C.dark};}
function pill(s,l,w=2.0){
  s.addShape("rect",{x:0.35,y:0.18,w,h:0.28,fill:{color:C.red},line:{color:C.red}});
  s.addText(l.toUpperCase(),{x:0.35,y:0.18,w,h:0.28,fontSize:8,bold:true,color:C.white,align:"center",valign:"middle",margin:0});
}
function slideTitle(s,t){
  s.addText(t,{x:0.4,y:0.55,w:12.5,h:0.55,fontSize:22,bold:true,color:C.dark,fontFace:"Calibri",align:"left",valign:"middle",margin:0});
}
function divider(s,y=1.15,col=C.red){
  s.addShape("line",{x:0.4,y,w:12.5,h:0,line:{color:col,width:1.5}});
}
function footNote(s,t){
  s.addText(t,{x:0.4,y:7.1,w:12.55,h:0.25,fontSize:9,color:C.grey,italic:true,align:"left",margin:0});
}
function insightBar(s,main,sub=""){
  s.addShape("rect",{x:0.4,y:6.35,w:12.55,h:sub?0.92:0.6,fill:{color:C.dark},line:{color:C.dark}});
  s.addText(main,{x:0.55,y:6.37,w:12.2,h:0.38,fontSize:10,color:C.white,valign:"middle",margin:0});
  if(sub) s.addText(sub,{x:0.55,y:6.76,w:12.2,h:0.44,fontSize:9,color:"FFEECC",italic:true,valign:"top",margin:0});
}

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

// ── SLIDE 1: TITLE ────────────────────────────────────────────────────────────
{const s=pres.addSlide(); darkBg(s);
s.addShape("rect",{x:0,y:0,w:0.22,h:7.5,fill:{color:C.red},line:{color:C.red}});
s.addText("AGODA",{x:0.5,y:0.5,w:3,h:0.5,fontSize:18,bold:true,color:C.red,fontFace:"Calibri",charSpacing:6,margin:0});
s.addText("Urgency Messaging\nStrategy Analysis",{x:0.5,y:1.1,w:8,h:2.1,fontSize:44,bold:true,color:C.white,fontFace:"Calibri",align:"left",lineSpacingMultiple:1.15});
s.addText("How hotel prices move as check-in approaches — and what business\nopportunities arise across 5 cities",{x:0.5,y:3.3,w:9,h:0.8,fontSize:14,color:"AAAAAA",italic:true,align:"left"});
s.addShape("line",{x:0.5,y:4.25,w:5,h:0,line:{color:C.red,width:2}});
s.addText("Saarang Ahuja  |  Supply Analytics Case Study",{x:0.5,y:4.45,w:7,h:0.3,fontSize:11,color:"888888",align:"left",margin:0});
[{val:"49,061",lbl:"Total Bookings"},{val:"5",lbl:"Cities Analysed"},
 {val:"880",lbl:"Unique Properties"},{val:"13,236",lbl:"Chain Hotel Bookings"},
 {val:"35,825",lbl:"Non-Chain Bookings"},{val:"Oct–Dec 2016",lbl:"Check-in Date Range"},
].forEach((st,i)=>{
  const col=i%2; const row=Math.floor(i/2); const x=9.1+col*2.2; const y=0.75+row*1.9;
  s.addShape("rect",{x,y,w:2.0,h:1.65,fill:{color:"FFFFFF",transparency:92},line:{color:"444466",width:1}});
  s.addText(st.val,{x,y:y+0.1,w:2.0,h:0.82,fontSize:i<4?24:13,bold:true,color:C.red,align:"center",valign:"middle",margin:0,fontFace:"Calibri"});
  s.addText(st.lbl,{x,y:y+0.92,w:2.0,h:0.65,fontSize:8,color:"AAAAAA",align:"center",valign:"top",margin:0});
});}

// ── SLIDE 2: CONTEXT & ASSUMPTIONS ────────────────────────────────────────────
{const s=pres.addSlide(); lightBg(s);
pill(s,"Context",2.2); slideTitle(s,"Business Question & Key Assumptions"); divider(s);
s.addText("Dataset Limitations",{x:0.4,y:1.3,w:5.8,h:0.35,fontSize:14,bold:true,color:C.dark,margin:0});
s.addText([
  "Three months of data (Oct\u2013Dec 2016) \u2014 seasonal effects may not reflect full-year behaviour.",
  "No competitor pricing data \u2014 Agoda\u2019s price positioning relative to the market is unknown.",
  "No booking funnel data \u2014 conversion rates at each stage cannot be directly measured.",
  "No occupancy/availability data \u2014 scarcity messaging cannot be validated from this dataset.",
  "City IDs only \u2014 market context (resort vs urban vs business) is inferred, not labelled.",
  "Price direction classification limited to 565 of 880 properties \u2014 315 lacked sufficient bookings in both early and last-minute windows. These contributed to all other analyses.",
].map((l,i,arr)=>({text:l,options:{bullet:true,breakLine:i<arr.length-1,fontSize:11,color:C.dark,paraSpaceAfter:5}})),
  {x:0.4,y:1.72,w:5.8,h:5.1,valign:"top",margin:4});
s.addText("Key Assumptions & Methodology",{x:6.5,y:1.3,w:6.9,h:0.35,fontSize:13,bold:true,color:C.dark,margin:0});
[{head:"Lead Time Formula",body:"Lead Time (days) = Check-in Date \u2212 Booking Date. 3 records with negative values excluded."},
 {head:"Lead Time Buckets \u2014 Rationale",body:"Buckets reflect natural planning horizons: same-day, last-minute (1\u20133d), short-advance (4\u20137d), medium (8\u201314d), planned (15\u201330d, 31\u201360d). Interpretability was prioritised over k-means."},
 {head:"Why Median, Not Mean",body:"Median ignores extreme outliers and shows what the typical booker paid \u2014 more honest than mean which is pulled by luxury outliers."},
 {head:"Price Direction Classification (\u00b15% Threshold)",body:"Each property\u2019s last-minute price (0\u20133d) vs early price (15+ days). >5% higher \u2192 Rising. >5% lower \u2192 Falling. Within 5% \u2192 Stable. Buffer prevents random fluctuations from being classified as meaningful change."},
].forEach((a,i)=>{
  const y=1.72+i*1.35;
  s.addShape("rect",{x:6.5,y,w:6.9,h:1.25,fill:{color:i%2===0?"F8F8FF":"F0F0F5"},line:{color:"CCCCDD",width:1}});
  s.addText(a.head,{x:6.65,y:y+0.07,w:6.6,h:0.28,fontSize:11,bold:true,color:C.dark,margin:0});
  s.addText(a.body,{x:6.65,y:y+0.38,w:6.6,h:0.84,fontSize:9.5,color:C.grey,align:"left",valign:"top",margin:0});
});
footNote(s,"Dataset: 49,061 bookings · 5 cities · 880 unique properties · Check-in dates Oct\u2013Dec 2016 · 3 records excluded (negative lead time)");}

// ── SLIDE 3: EXECUTIVE SUMMARY ────────────────────────────────────────────────
{const s=pres.addSlide(); darkBg(s); pill(s,"Executive Summary",2.2);
s.addText("Key Findings & Recommendations \u2014 All 5 Cities",{x:0.4,y:0.55,w:12.5,h:0.55,fontSize:23,bold:true,color:C.white,fontFace:"Calibri",align:"left",valign:"middle",margin:0});
const cards=[
  {stat:"\u221222.7%",head:"Average ADR Drop (31\u201360 Days Ahead \u2192 Same-Day)",
   body:"Average fall in ADR from the 31\u201360 day window to same-day booking, across all 5 cities:\nCity A: \u221212.9%  |  City B: \u221230.9%  |  City C: \u221250.6%  |  City D: \u22126.5%  |  City E: \u221212.8%"},
  {stat:"34%",head:"High-Volume Last-Minute Window",
   body:"34% of all bookings across 5 cities are made within 3 days of check-in. City E peaks at 44%; City C is lowest at 18% \u2014 each city needs a calibrated urgency strategy."},
  {stat:"456 of 880",head:"Properties Confirmed to Price Last-Minute Lower or Flat",
   body:"456 unique properties (52% of all 880) confirmed to price the same or lower last-minute. 315 lacked sufficient data to classify. Only 109 genuinely raise prices last-minute."},
];
cards.forEach((card,i)=>{
  const x=0.4+i*4.35;
  s.addShape("rect",{x,y:1.35,w:4.05,h:2.9,fill:{color:C.ltgrey},line:{color:"CCCCDD",width:1}});
  s.addShape("rect",{x,y:1.35,w:4.05,h:0.08,fill:{color:C.red},line:{color:C.red}});
  s.addText(card.stat,{x,y:1.5,w:4.05,h:0.8,fontSize:i===2?22:32,bold:true,color:C.red,align:"center",valign:"middle",margin:0,fontFace:"Calibri"});
  s.addText(card.head,{x:x+0.1,y:2.35,w:3.85,h:0.45,fontSize:11,bold:true,color:C.dark,align:"left",margin:0});
  s.addText(card.body,{x:x+0.1,y:2.85,w:3.85,h:1.25,fontSize:i===0?9:9.5,color:"444444",align:"left",valign:"top",margin:0});
});
s.addShape("rect",{x:8.75,y:4.35,w:4.25,h:1.67,fill:{color:"FFF8E1"},line:{color:C.amber,width:1}});
s.addText("\u26a0 Data note: 315 of 880 properties lacked sufficient bookings in both the early (15+ days) and last-minute (0\u20133 days) windows to classify price direction. These properties contributed to all other analyses (ADR trends, EDA, segmentation) but could not be included in the rising/stable/falling comparison.",
  {x:8.75,y:4.35,w:4.25,h:1.67,fontSize:8.5,color:"5D4037",italic:true,valign:"top",align:"left",margin:3});
s.addText("CITY-BY-CITY SNAPSHOT",{x:0.4,y:4.38,w:3.5,h:0.28,fontSize:9,bold:true,color:C.amber,align:"left",charSpacing:2,margin:0});
s.addShape("rect",{x:0.4,y:4.7,w:8.2,h:1.05,fill:{color:"22223A"},line:{color:"444466",width:1}});
s.addText("City   |   ADR Drop (31\u201360d\u2192same-day)   |   3-day booking share   |   % Rising   |   Market",
  {x:0.55,y:4.72,w:8.0,h:0.25,fontSize:8,bold:true,color:C.amber,margin:0,valign:"middle"});
["City A  |  \u221212.9%  |  37.5%  |  13%  |  Urban mixed",
 "City B  |  \u221230.9%  |  41.6%  |  20%  |  Resort-heavy",
 "City C  |  \u221250.6%  |  17.8%  |  18%  |  Premium, plans ahead",
 "City D  |  \u22126.5%   |  28.5%  |  31%  |  Premium, price-stable",
 "City E  |  \u221212.8%  |  44.1%  |  24%  |  Most last-minute",
].forEach((row,i)=>s.addText(row,{x:0.55,y:4.99+i*0.15,w:8.0,h:0.14,fontSize:8,color:i%2===0?"FFFFFF":"CCCCCC",margin:0,valign:"middle"}));
s.addText("RECOMMENDATION",{x:0.4,y:5.92,w:2.2,h:0.28,fontSize:9,bold:true,color:C.red,align:"left",charSpacing:3,margin:0});
s.addShape("rect",{x:0.4,y:6.24,w:12.55,h:1.0,fill:{color:"22223A"},line:{color:"444466",width:1}});
s.addText([
  {text:'Avoid blanket \u201cprices rising\u201d urgency claims \u2014 only truthful for 109 of 880 properties; the majority price last-minute lower or flat',options:{bullet:true,breakLine:true,fontSize:10,color:C.white,paraSpaceAfter:2}},
  {text:'Use specific types of urgency messaging for different scenarios \u2014 for example, use \u201cearn more loyalty points\u201d urgency messaging for budget and mid-range properties as their prices fall further; honest framing captures the booking, builds goodwill and earns customer loyalty',options:{bullet:true,breakLine:true,fontSize:10,color:C.white,paraSpaceAfter:2}},
  {text:'4\u2605 properties are the highest revenue segment in 4 of 5 cities (A, B, D, E); in City C where 3\u2605 dominates, the same logic applies \u2014 A/B testing should validate the optimal message type per city before full rollout',options:{bullet:true,breakLine:false,fontSize:10,color:C.white,paraSpaceAfter:2}},
],{x:0.6,y:6.27,w:12.1,h:0.93,valign:"top",margin:3});}

// ── SLIDE 4: CROSS-CITY EDA OVERVIEW ─────────────────────────────────────────
{const s=pres.addSlide(); lightBg(s);
pill(s,"Cross-City EDA Overview",2.6); slideTitle(s,"Cross-City Exploratory Data Analysis \u2014 All 5 Cities"); divider(s);
s.addImage({data:imgData("fig_crosscity_eda"),x:0.4,y:1.25,w:12.55,h:5.0});
s.addShape("rect",{x:0.4,y:6.35,w:12.55,h:0.92,fill:{color:C.dark},line:{color:C.dark}});
s.addText("Two distinct market clusters: Budget/last-minute (A, B, E \u2014 median ADR $79\u2013$94, High-Urgency 38\u201344%) vs Premium (C, D \u2014 median ADR $190\u2013$192, High-Urgency 18\u201328%). 4\u2605/5\u2605 revenue share exceeds booking share in all 5 cities.",
  {x:0.55,y:6.37,w:12.2,h:0.42,fontSize:10,color:C.white,valign:"middle",margin:0});
s.addText("Per-graph cross-city analysis on the following slides \u2014 each slide shows one graph type across all 5 cities simultaneously.",
  {x:0.55,y:6.78,w:12.2,h:0.4,fontSize:9,color:"FFEECC",italic:true,valign:"top",margin:0});}

// ── SLIDES 5–12: CROSS-TYPE SLIDES ────────────────────────────────────────────
const crossTypeSlides = [
  {img:"fig_xt_01_monthly",   title:"Monthly Booking Patterns \u2014 Oct, Nov & Dec Across All 5 Cities",
   note:"December ADR rises in leisure markets (City B: +10%, City E: +8%, City D: +3%). Last-minute booking rate FALLS in December across all cities \u2014 people plan further ahead for holidays. Dec urgency strategy: scarcity/\u201cprice rising\u201d framing. Oct/Nov: earn-sooner framing works best (last-min share highest)."},
  {img:"fig_xt_02_lead_time", title:"Lead Time Distribution (Urgency Tiers) \u2014 All 5 Cities",
   note:"H = High Urgency (0\u20133d) \u00b7 M = Medium (4\u201314d) \u00b7 L = Low (15\u201360d). City E (44% High) and City B (42% High) need time-triggered messaging most urgently. City C (54% Low) needs longer lead-time campaigns."},
  {img:"fig_xt_03_rev_star",  title:"Revenue vs Booking Share by Star Band \u2014 All 5 Cities",
   note:"Highlighted bands = revenue share > booking share (ratio >1x). 4\u2605 is the priority urgency messaging segment in all cities. # inside blue bars = number of bookings; $ inside revenue bars = median ADR."},
  {img:"fig_xt_04_acc_type",  title:"Accommodation Type Mix \u2014 All 5 Cities",
   note:"City-colour bar = highest-volume type (priority for urgency messaging reach). City B uniquely Resort-heavy (39%). City C has Capsule Hotels (unique market). City E has mixed Hotel+Resort split requiring dual strategy."},
  {img:"fig_xt_05_adr_scatter",title:"Median ADR by Days to Check-in \u2014 All 5 Cities",
   note:"Smoothed trend line shows price fall in all 5 cities as check-in approaches. % shown = ADR change from 31\u201360d to same-day. All results statistically significant (p<0.001) except City D (p=0.075 \u2014 most price-stable market)."},
  {img:"fig_xt_06_adr_bucket",title:"Median ADR by Lead Time Bucket \u2014 All 5 Cities",
   note:"Red = same-day (0d) \u00b7 Amber = 1\u20133 days \u00b7 City colour = 4+ days. % labels = share of city\u2019s total bookings. Same-day bookers consistently pay lowest ADR \u2014 validating earn-sooner urgency message framing."},
  {img:"fig_xt_07_star_grouped",title:"ADR by Star Band and Lead Time \u2014 All 5 Cities",
   note:"4 lead time windows shown per star band. Higher star = higher ADR at every lead time in all cities. Gap between same-day and 31\u201360d is largest for 4\u2605/5\u2605 \u2014 these are the highest-value urgency targets."},
  {img:"fig_xt_08_star_trend", title:"ADR Trend by Star Band \u2014 All 5 Cities",
   note:"% labels = ADR drop from 31\u201360d to same-day per star band. Upsell windows: City C: 4\u2605\u22485\u2605 at 8\u201315d \u00b7 City D: 3\u2605\u22484\u2605 across all lead times \u00b7 City E: 1\u20132\u2605\u22483\u2605 at 4\u20138d."},
];

crossTypeSlides.forEach(({img,title,note})=>{
  const s=pres.addSlide(); lightBg(s);
  pill(s,"Cross-City by Graph Type",2.8);
  slideTitle(s,title); divider(s);
  s.addImage({data:imgData(img),x:0.4,y:1.25,w:12.55,h:5.0});
  s.addShape("rect",{x:0.4,y:6.35,w:12.55,h:0.92,fill:{color:C.dark},line:{color:C.dark}});
  s.addText(note,{x:0.55,y:6.37,w:12.2,h:0.85,fontSize:9.5,color:C.white,valign:"middle",margin:0,italic:false});
});

// ── CROSS-CITY FINAL OVERVIEW ─────────────────────────────────────────────────
{const s=pres.addSlide(); lightBg(s);
pill(s,"Cross-City Overview",2.5);
slideTitle(s,"Cross-City: Price Trends, Urgency Profile, Revenue by Segment & Price Direction"); divider(s);
s.addImage({data:imgData("fig_cross_final"),x:0.4,y:1.25,w:12.55,h:5.0});
s.addShape("rect",{x:0.4,y:6.35,w:12.55,h:0.92,fill:{color:C.dark},line:{color:C.dark}});
s.addText("All 5 cities show falling prices last-minute. Cities E & B have the highest share of last-minute bookers (44% and 42%) requiring high-urgency messaging. 4\u2605/5\u2605 bands generate disproportionate revenue across all cities.",
  {x:0.55,y:6.37,w:12.2,h:0.38,fontSize:9.5,color:C.white,bold:false,valign:"middle",margin:0});
s.addText("ADR Drop (31\u201360d \u2192 Same-day):   City A: \u221212.9% ($88\u2192$77)  |  City B: \u221230.9% ($95\u2192$66)  |  City C: \u221250.6% ($210\u2192$104)  |  City D: \u22126.5% ($194\u2192$181)  |  City E: \u221212.8% ($96\u2192$84)",
  {x:0.55,y:6.76,w:12.2,h:0.48,fontSize:9,color:"FFEECC",italic:true,valign:"top",margin:0});}

// ── RECOMMENDATIONS ───────────────────────────────────────────────────────────
{const s=pres.addSlide(); lightBg(s);
pill(s,"Recommendations",2.0); slideTitle(s,"Urgency Messaging Strategy by Segment"); divider(s);
s.addImage({data:imgData("fig6_recommendations"),x:0.4,y:1.25,w:12.55,h:5.5});
footNote(s,"'Earn-sooner' messages capture bookings before prices fall further. A/B test all types before rollout. City-level calibration required given ADR drops ranging from \u22126.5% to \u221250.6% across markets.");}

// ── NEXT STEPS ────────────────────────────────────────────────────────────────
{const s=pres.addSlide(); lightBg(s);
pill(s,"Next Steps",1.8); slideTitle(s,"Recommended Next Steps"); divider(s);
s.addText("Recommended Next Steps",{x:0.4,y:1.3,w:12.55,h:0.35,fontSize:14,bold:true,color:C.dark,margin:0});
[{n:"1",head:"A/B Test Urgency Message Types",body:"Run controlled tests per segment and city \u2014 compare conversion with earn-sooner vs availability vs value-framing messages."},
 {n:"2",head:"Expand to Full Year Dataset",body:"Seasonal effects (peak vs off-peak) may significantly change price dynamics and urgency effectiveness."},
 {n:"3",head:"Build Real-Time Price Signal",body:"Develop a live model flagging which properties have rising vs falling prices \u2014 enabling dynamic, truthful urgency messages per listing."},
 {n:"4",head:"City-Level Calibration",body:"City C\u2019s \u221250.6% drop vs City D\u2019s \u22126.5% requires very different urgency intensity per market. Localise before rolling out."},
].forEach((step,i)=>{const y=1.72+i*1.55;
  s.addShape("rect",{x:0.4,y,w:0.5,h:0.5,fill:{color:C.red},line:{color:C.red}});
  s.addText(step.n,{x:0.4,y,w:0.5,h:0.5,fontSize:16,bold:true,color:C.white,align:"center",valign:"middle",margin:0});
  s.addText(step.head,{x:1.1,y:y+0.02,w:12.0,h:0.35,fontSize:13,bold:true,color:C.dark,margin:0});
  s.addText(step.body,{x:1.1,y:y+0.4,w:12.0,h:0.9,fontSize:11.5,color:C.grey,margin:0,align:"left"});});}

// ── CLOSING ───────────────────────────────────────────────────────────────────
{const s=pres.addSlide(); darkBg(s);
s.addShape("rect",{x:0,y:0,w:0.22,h:7.5,fill:{color:C.red},line:{color:C.red}});
s.addText("Summary",{x:0.5,y:0.65,w:5,h:0.35,fontSize:12,bold:true,color:C.red,charSpacing:3,margin:0});
s.addText("What We Found\n& What It Means",{x:0.5,y:1.05,w:7,h:1.6,fontSize:36,bold:true,color:C.white,fontFace:"Calibri",lineSpacingMultiple:1.1});
[{stat:"All 5",label:"Cities confirm prices\nfall last-minute",c:C.red},
 {stat:"34%",label:"Bookings made within\n3 days of check-in",c:C.amber},
 {stat:"\u221250.6%",label:"Biggest market drop\n(City C, premium segment)",c:C.green},
].forEach((cl,i)=>{const x=0.5+i*4.25;
  s.addShape("rect",{x,y:2.9,w:4.0,h:2.0,fill:{color:"FFFFFF",transparency:92},line:{color:"444466",width:1}});
  s.addText(cl.stat,{x,y:3.0,w:4.0,h:0.85,fontSize:36,bold:true,color:cl.c,align:"center",margin:0,fontFace:"Calibri"});
  s.addText(cl.label,{x,y:3.85,w:4.0,h:0.85,fontSize:11,color:"BBBBBB",align:"center",valign:"top",margin:4});});
s.addText("Urgency messaging can improve conversion across all 5 markets \u2014 but only when the message is matched to the actual price signal and calibrated per city.",
  {x:0.5,y:5.1,w:12.5,h:0.9,fontSize:12.5,color:"AAAAAA",align:"left",italic:true});
s.addText("Thank you  \u00b7  Questions welcome",{x:0.5,y:6.65,w:6,h:0.35,fontSize:12,color:"666666",italic:true,margin:0});
s.addText("Saarang Ahuja",{x:9.5,y:6.65,w:3.5,h:0.35,fontSize:12,color:"666666",align:"right",margin:0});}

pres.writeFile({fileName:path.join(__dirname, "../outputs/Agoda_CrossType_Format.pptx")})
  .then(()=>console.log("Done — cross-type deck written."))
  .catch(e=>{console.error(e);process.exit(1);});
