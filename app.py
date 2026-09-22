import math
from datetime import datetime, date, time, timedelta
import pandas as pd
import streamlit as st
import swisseph as swe

st.set_page_config(page_title='Sarvatobhadra Chakra', page_icon='☸️', layout='wide')

# ---------------- Astronomy ----------------
NAKSHATRAS_27 = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya',
    'Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati',
    'Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha',
    'Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'
]
NAKSHATRAS_28 = NAKSHATRAS_27[:21] + ['Abhijit'] + NAKSHATRAS_27[21:]
RASHIS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE,
}
BENEFICS = {'Moon','Mercury','Jupiter','Venus'}
MALEFICS = {'Sun','Mars','Saturn','Rahu','Ketu'}

def norm360(x): return x % 360.0

def sidereal_longitude(jd_ut, body):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    if body == 'Ketu':
        xx, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, flags)
        return norm360(xx[0] + 180), xx[3]
    xx, _ = swe.calc_ut(jd_ut, PLANETS[body], flags)
    return norm360(xx[0]), xx[3]

def nakshatra_info(lon):
    # 27 equal nakshatras for Moon/transit classification; Abhijit is a special SBC cell.
    span = 360/27
    idx = int(lon // span)
    frac = (lon - idx*span)/span
    pada = min(4, int(frac*4)+1)
    return NAKSHATRAS_27[idx], pada, idx, frac

def rashi(lon): return RASHIS[int(lon//30)]

def jd_from_local(dt, utc_offset):
    utc = dt - timedelta(hours=utc_offset)
    return swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)

def tithi_info(sun_lon, moon_lon):
    elong = norm360(moon_lon - sun_lon)
    n = int(elong // 12) + 1
    paksha = 'Shukla' if n <= 15 else 'Krishna'
    paksha_tithi = n if n <= 15 else n-15
    names = ['Pratipada','Dvitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami','Ashtami','Navami','Dashami','Ekadashi','Dwadashi','Trayodashi','Chaturdashi','Purnima/Amavasya']
    return n, paksha, paksha_tithi, names[paksha_tithi-1]

def tithi_group(tithi_number):
    # Classical five repeating families.
    m = tithi_number % 5
    return {1:'Nanda',2:'Bhadra',3:'Jaya',4:'Rikta',0:'Poorna'}[m]

def calc_positions(dt, utc_offset):
    jd = jd_from_local(dt, utc_offset)
    out=[]
    for p in PLANETS:
        lon,speed = sidereal_longitude(jd,p)
        nk,pada,idx,frac = nakshatra_info(lon)
        out.append({'Planet':p,'Longitude':lon,'Rashi':rashi(lon),'Nakshatra':nk,'Pada':pada,'Speed':speed,'Retrograde':speed < -1e-6})
    df=pd.DataFrame(out)
    sun=df.loc[df.Planet=='Sun','Longitude'].iloc[0]
    moon=df.loc[df.Planet=='Moon','Longitude'].iloc[0]
    tn,pk,pt,tnm=tithi_info(sun,moon)
    return jd,df,{'tithi_number':tn,'paksha':pk,'paksha_tithi':pt,'tithi_name':tnm,'tithi_group':tithi_group(tn),'weekday':dt.strftime('%A')}

# ---------------- Sarvatobhadra 9x9 ----------------
# The nested-ring construction follows the classical 81-cell architecture:
# outer 32 = 28 nakshatras + 4 corner vowels; next 24 = 20 consonants + 4 vowels;
# next 16 = 12 rashis + 4 vowels; next 8 = 4 tithi groups + 4 vowels; center = Poorna.
VOWELS = ['a','aa','i','ii','u','uu','e','ai','o','au','am','ah','ri','rii','lu','luu']
CONSONANTS = ['k','kh','g','gh','ch','chh','j','jh','t','th','d','dh','p','ph','b','bh','m','y','r','l']

def ring_coords(k):
    # clockwise perimeter coordinates for an odd square ring side length k
    maxc=k-1
    coords=[]
    for c in range(k): coords.append((0,c))
    for r in range(1,k): coords.append((r,maxc))
    for c in range(maxc-1,-1,-1): coords.append((maxc,c))
    for r in range(maxc-1,0,-1): coords.append((r,0))
    return coords

def build_grid():
    grid=[[{'label':'','type':'','key':''} for _ in range(9)] for __ in range(9)]
    # 9x9 outer ring
    outer=ring_coords(9)
    # Reserve corners for vowels; seven cells per side.
    # Classical placement used by the common Sarvatobhadra layout:
    # East: Krittika -> Ashlesha; South: Magha -> Vishakha;
    # West: Anuradha -> Shravana (with Abhijit between Uttara Ashadha and Shravana);
    # North: Dhanishtha -> Bharani.
    side_naks=[
        ['Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha'],
        ['Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha'],
        ['Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Abhijit','Shravana'],
        ['Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati','Ashwini','Bharani'],
    ]
    segments=[[(r,8) for r in range(1,8)],[(8,c) for c in range(7,0,-1)],[(r,0) for r in range(7,0,-1)],[(0,c) for c in range(1,8)]]
    for seg,vals in zip(segments,side_naks):
        for pos,val in zip(seg,vals): grid[pos[0]][pos[1]]={'label':val,'type':'nakshatra','key':val}
    # Corner vowels
    for pos,val in zip([(0,0),(0,8),(8,8),(8,0)], VOWELS[:4]): grid[pos[0]][pos[1]]={'label':val,'type':'vowel','key':val}
    # Inner ring 7x7
    coords=ring_coords(7)
    noncorn=[p for p in coords if p not in [(1,1),(1,7),(7,7),(7,1)]]
    # 20 consonants
    for p,val in zip(noncorn,CONSONANTS): grid[p[0]][p[1]]={'label':val,'type':'consonant','key':val}
    for p,val in zip([(1,1),(1,7),(7,7),(7,1)],VOWELS[4:8]): grid[p[0]][p[1]]={'label':val,'type':'vowel','key':val}
    # Inner ring 5x5: 12 rashis + 4 vowels
    coords=ring_coords(5); noncorn=[p for p in coords if p not in [(2,2),(2,6),(6,6),(6,2)]]
    for p,val in zip(noncorn,RASHIS): grid[p[0]][p[1]]={'label':val,'type':'rashi','key':val}
    for p,val in zip([(2,2),(2,6),(6,6),(6,2)],VOWELS[8:12]): grid[p[0]][p[1]]={'label':val,'type':'vowel','key':val}
    # Inner ring 3x3: tithi families + 4 vowels
    coords=ring_coords(3); noncorn=[p for p in coords if p not in [(3,3),(3,5),(5,5),(5,3)]]
    for p,val in zip(noncorn,['Nanda','Bhadra','Jaya','Rikta']): grid[p[0]][p[1]]={'label':val,'type':'tithi','key':val}
    for p,val in zip([(3,3),(3,5),(5,5),(5,3)],VOWELS[12:16]): grid[p[0]][p[1]]={'label':val,'type':'vowel','key':val}
    grid[4][4]={'label':'Poorna','type':'tithi','key':'Poorna'}
    return grid

GRID=build_grid()
NAK_COORD={cell['key']:(r,c) for r,row in enumerate(GRID) for c,cell in enumerate(row) if cell['type']=='nakshatra'}

def direction_targets(r,c):
    # Three principal rays from a border nakshatra: front (inward/opposite side),
    # and the two crossward diagonal rays. The returned cells are the border/end cells
    # reached by those lines, matching the visual 9x9 construction.
    rays={'front':[],'left':[],'right':[]}
    if c==8:  # east border: front goes west
        rays['front']=[(r,0)]
        rays['left']=[(0,8-r)]
        rays['right']=[(8,8-r)]
    elif r==8:  # south border: front goes north
        rays['front']=[(0,c)]
        rays['left']=[(8-c,0)]
        rays['right']=[(8-c,8)]
    elif c==0:  # west border: front goes east
        rays['front']=[(r,8)]
        rays['left']=[(0,r)]
        rays['right']=[(8,r)]
    elif r==0:  # north border: front goes south
        rays['front']=[(8,c)]
        rays['left']=[(c,0)]
        rays['right']=[(c,8)]
    return rays

def vedha_for_planet(row, rule_mode='classical-motion'):
    p=row['Planet']; nk=row['Nakshatra']; r,c=NAK_COORD[nk]
    rays=direction_targets(r,c)
    speed=row['Speed']; retro=row['Retrograde']
    if p in {'Sun','Moon','Rahu','Ketu'}:
        active=['front','left','right']; rule='all three rays'
    else:
        if retro:
            active=['left']; rule='retrograde → left'
        elif abs(speed) > 0.95:
            active=['right']; rule='fast/direct → right'
        else:
            active=['front']; rule='normal/direct → front'
    targets=[]
    for a in active:
        for pos in rays[a]:
            rr,cc=pos
            if 0<=rr<9 and 0<=cc<9:
                cell=GRID[rr][cc]
                if cell['label'] and cell['type'] not in {'vowel'}:
                    targets.append({'Ray':a,'Row':rr+1,'Col':cc+1,**cell})
    return targets,rule

def make_html_grid(highlights, transit_cells=None):
    transit_cells=transit_cells or {}
    html='<style>table.sbc{border-collapse:collapse;width:100%;table-layout:fixed}table.sbc td{border:1px solid #777;height:58px;text-align:center;font-size:12px;padding:3px} .nk{background:#eef5ff}.ben{outline:3px solid #2e8b57}.mal{outline:3px solid #c0392b}.nat{box-shadow:inset 0 0 0 3px #8e44ad}.hit{background:#fff1a8!important;font-weight:700}.small{font-size:9px}</style><table class="sbc">'
    for r,row in enumerate(GRID):
        html+='<tr>'
        for c,cell in enumerate(row):
            key=(r,c); cls=[]
            if cell['type']=='nakshatra': cls.append('nk')
            if key in highlights: cls += highlights[key]
            txt=cell['label']
            if key in transit_cells:
                txt += '<br><span class="small">'+', '.join(transit_cells[key])+'</span>'
            html+=f'<td class="{" ".join(cls)}">{txt}</td>'
        html+='</tr>'
    return html+'</table>'

# ---------------- UI ----------------
st.title('☸️ Sarvatobhadra Chakra — Historical Astrology Workbench')
st.caption('Sidereal/Lahiri • 28-nakshatra 9×9 chakra • historical transit replay • Panchaka & Vedha analysis')

with st.sidebar:
    st.header('Birth / Reference')
    bdate=st.date_input('Birth date', value=date(1983,5,23), min_value=date(1900,1,1), max_value=date(2100,12,31))
    btime=st.time_input('Birth time', value=time(4,15))
    offset=st.number_input('UTC offset', value=5.5, min_value=-12.0, max_value=14.0, step=0.5)
    lat=st.number_input('Latitude', value=28.95, format='%.5f')
    lon=st.number_input('Longitude', value=77.22, format='%.5f')
    name=st.text_input('Name / first sound (optional)', value='')
    st.divider()
    st.header('Historical transit')
    tdate=st.date_input('Analysis date', value=date.today(), min_value=date(1900,1,1), max_value=date(2100,12,31))
    ttime=st.time_input('Analysis time', value=time(12,0), key='analysis_time')
    show_rays=st.checkbox('Show Vedha rays on natal points', value=True)
    selected_planet=st.selectbox('Planet focus', ['All','Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'])
    st.divider()
    st.info('The app calculates astronomy; interpretations are presented as traditional rule-based indicators, not guaranteed predictions.')

birth_dt=datetime.combine(bdate,btime)
transit_dt=datetime.combine(tdate,ttime)

try:
    _, natal, natalcal=calc_positions(birth_dt,offset)
    _, trans, transcal=calc_positions(transit_dt,offset)
except Exception as e:
    st.error(f'Astronomical calculation failed: {e}')
    st.stop()

moon_natal=natal[natal.Planet=='Moon'].iloc[0]
moon_trans=trans[trans.Planet=='Moon'].iloc[0]

# Natal reference points: Moon nakshatra, Moon sign, birth tithi group, weekday; name optional.
ref_nk=moon_natal.Nakshatra
ref_rashi=moon_natal.Rashi
ref_tithi=natalcal['tithi_group']
ref_weekday=natalcal['weekday']

# Highlight natal points
highlights={}
for nk, cls in [(ref_nk,['nat'])]:
    if nk in NAK_COORD: highlights[NAK_COORD[nk]]=cls
for r in range(9):
    for c in range(9):
        cell=GRID[r][c]
        if cell['type']=='rashi' and cell['label']==ref_rashi: highlights[(r,c)]=['nat']
        if cell['type']=='tithi' and cell['label']==ref_tithi: highlights[(r,c)]=['nat']

# Transit vedha analysis
records=[]; transit_cells={}
for _,row in trans.iterrows():
    if selected_planet!='All' and row.Planet!=selected_planet: continue
    targets,rule=vedha_for_planet(row)
    for x in targets:
        key=(x['Row']-1,x['Col']-1)
        transit_cells.setdefault(key,[]).append(row.Planet)
        hit=False; hit_type=''
        if x['type']=='nakshatra' and x['label']==ref_nk: hit=True; hit_type='Janma Nakshatra'
        if x['type']=='rashi' and x['label']==ref_rashi: hit=True; hit_type='Janma Rashi'
        if x['type']=='tithi' and x['label']==ref_tithi: hit=True; hit_type='Janma Tithi group'
        if hit:
            records.append({'Planet':row.Planet,'Transit Nakshatra':row.Nakshatra,'Pada':int(row.Pada),'Retrograde':bool(row.Retrograde),'Target':hit_type,'Target value':x['label'],'Ray':x['Ray'],'Rule':rule,'Nature':'Benefic' if row.Planet in BENEFICS else 'Malefic'})

st.subheader('Reference Panchaka')
cols=st.columns(5)
for c,title,val in zip(cols,['Janma Nakshatra','Janma Rashi','Janma Tithi','Janma Weekday','Name sound'],[ref_nk,ref_rashi,ref_tithi,ref_weekday,name or '—']):
    c.metric(title,val)

st.subheader('Historical transit sky')
trans_view=trans[['Planet','Rashi','Nakshatra','Pada','Speed','Retrograde']].copy()
trans_view['Longitude']=trans_view['Longitude'].map(lambda x:round(x,4))
st.dataframe(trans_view,hide_index=True,use_container_width=True)

left,right=st.columns([1.35,1])
with left:
    st.subheader('Sarvatobhadra Chakra')
    st.markdown(make_html_grid(highlights,transit_cells if show_rays else {}),unsafe_allow_html=True)
    st.caption('Purple outline = natal reference. Yellow cells = current transit Vedha targets. Planet names inside cells show which transit rays reach the cell.')
with right:
    st.subheader('Vedha hits')
    if records:
        hitdf=pd.DataFrame(records)
        st.dataframe(hitdf,hide_index=True,use_container_width=True)
        score=0
        for x in records: score += 1 if x['Nature']=='Benefic' else -1
        if score>0: st.success(f'Net traditional Vedha indicator: {score:+d} (benefic hits exceed malefic hits)')
        elif score<0: st.warning(f'Net traditional Vedha indicator: {score:+d} (malefic hits exceed benefic hits)')
        else: st.info('Net traditional Vedha indicator: 0 (mixed/equal)')
    else:
        st.info('No selected-planet Vedha hit on the tracked natal Panchaka points at this moment.')

st.subheader('Historical replay')
replay_start=st.date_input('Replay start',value=tdate-timedelta(days=30),min_value=date(1900,1,1),max_value=date(2100,12,31))
replay_end=st.date_input('Replay end',value=tdate,min_value=date(1900,1,1),max_value=date(2100,12,31))
replay_hour=st.slider('Local time for each historical day',0,23,12)
if replay_start>replay_end: st.error('Replay start must be on or before replay end.')
else:
    if st.button('Run historical replay',type='primary'):
        rows=[]
        d=replay_start
        while d<=replay_end:
            dt=datetime.combine(d,time(replay_hour,0))
            _,td,tc=calc_positions(dt,offset)
            day_hits=0; day_ben=0; day_mal=0
            for _,pr in td.iterrows():
                if selected_planet!='All' and pr.Planet!=selected_planet: continue
                targets,_=vedha_for_planet(pr)
                for x in targets:
                    if (x['type']=='nakshatra' and x['label']==ref_nk) or (x['type']=='rashi' and x['label']==ref_rashi) or (x['type']=='tithi' and x['label']==ref_tithi):
                        day_hits+=1
                        if pr.Planet in BENEFICS: day_ben+=1
                        else: day_mal+=1
            rows.append({'Date':d,'Benefic hits':day_ben,'Malefic hits':day_mal,'Net':day_ben-day_mal,'Tithi':tc['tithi_name'],'Moon Nakshatra':td[td.Planet=='Moon'].iloc[0].Nakshatra})
            d+=timedelta(days=1)
        rdf=pd.DataFrame(rows)
        st.dataframe(rdf,hide_index=True,use_container_width=True)
        st.line_chart(rdf.set_index('Date')[['Benefic hits','Malefic hits','Net']])
        st.download_button('Download replay CSV',rdf.to_csv(index=False),'sarvatobhadra_replay.csv','text/csv')

st.divider()
st.caption('Method notes: planetary positions use Swiss Ephemeris with Lahiri sidereal mode. Sarvatobhadra construction/vedha conventions vary between classical sources; this implementation exposes the chosen motion-based convention rather than silently mixing schools.')
