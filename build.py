#!/usr/bin/env python3
"""
Simonoto Website Builder v3
============================
Edit content.json, then run: python build.py
Images go in the Images/ folder. The script base64-encodes them into the HTML.

New in v3:
  - Circular hero portrait
  - 3D hero font with layered text-shadows
  - Flip-to-tracklist album cards
  - Per-section CTAs
  - Testimonials section
  - Video placeholders section
  - Interactive hover/click effects throughout
  - Cursor glow on dark sections
  - Service card hover reveals
  - Gear count badges

Usage:
  python build.py              # builds index.html with embedded images
  python build.py --no-embed   # builds with relative image paths (for hosted deployment)
"""

import json, base64, sys, os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONTENT_FILE = SCRIPT_DIR / "content.json"
IMAGES_DIR = SCRIPT_DIR / "Images"
OUTPUT_FILE = SCRIPT_DIR / "index.html"

EMBED_IMAGES = "--no-embed" not in sys.argv

def load_content():
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def img(filename):
    if not filename:
        return ""
    if EMBED_IMAGES:
        filepath = IMAGES_DIR / filename
        if filepath.exists():
            with open(filepath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            ext = filepath.suffix.lower()
            mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}.get(ext.strip("."), "image/jpeg")
            return f"data:{mime};base64,{b64}"
        else:
            print(f"  ⚠ Image not found: {filename}")
            return f"images/{filename}"
    return f"images/{filename}"

def gear_html(categories):
    highlight_cats = categories[:3]
    remaining_cats = categories[3:]
    
    html = '<div class="gear-grid">\n'
    for i, cat in enumerate(highlight_cats):
        count = len(cat["items"])
        d = f' data-d="{i}"' if i > 0 else ''
        html += f'<div class="gear-cat rv"{d}><h3>{cat["name"]}<span class="gear-count">{count}</span></h3><ul>\n'
        for item in cat["items"]:
            note = f'<span class="note">{item["note"]}</span>' if item.get("note") else ""
            html += f'  <li>{item["name"]}{note}</li>\n'
        html += '</ul></div>\n'
    html += '</div>\n'
    
    html += '<div id="gear-full" class="gear-full-wrap" style="max-height:0;overflow:hidden;transition:max-height .6s cubic-bezier(.16,1,.3,1)">\n'
    html += '<div class="gear-grid" style="margin-top:18px">\n'
    for i, cat in enumerate(remaining_cats):
        count = len(cat["items"])
        d = f' data-d="{(i%4)+1}"' if i > 0 else ''
        html += f'<div class="gear-cat rv"{d}><h3>{cat["name"]}<span class="gear-count">{count}</span></h3><ul>\n'
        for item in cat["items"]:
            note = f'<span class="note">{item["note"]}</span>' if item.get("note") else ""
            html += f'  <li>{item["name"]}{note}</li>\n'
        html += '</ul></div>\n'
    html += '</div>\n</div>\n'
    html += '<button id="gear-toggle" class="btn btn-out" style="margin-top:24px;color:var(--brown);border-color:var(--brown)" onclick="toggleGear()">see the full rig →</button>\n'
    return html

def albums_html(albums):
    html = '<div class="albums">\n'
    for i, a in enumerate(albums):
        d = f' data-d="{i}"' if i > 0 else ''
        bc_id = a.get("bandcamp_album_id")
        bc_url = a.get("bandcamp_url", "")
        tracks = a.get("tracks", [])
        if bc_id and bc_id != "PASTE_ALBUM_ID_HERE":
            html += f'<div class="alb alb-bc rv"{d} style="grid-column:span 2"><iframe style="border:0;width:100%;height:274px" src="https://bandcamp.com/EmbeddedPlayer/album={bc_id}/size=large/bgcol=2A1A22/linkcol=FF9090/artwork=small/transparent=true/" seamless></iframe><div class="alb-buy"><a href="{bc_url}" target="_blank" class="btn btn-red" style="font-size:.58rem;padding:10px 22px">buy on bandcamp</a></div></div>\n'
        else:
            badge = f'<div class="alb-badge">{a["badge"]}</div>' if a.get("badge") else ""
            c = a["colors"]
            tracks_list = "".join([f'<li>{t}</li>' for t in tracks])
            html += f'''<div class="alb alb-flip rv"{d} onclick="this.classList.toggle('flipped')">
  <div class="alb-flip-inner">
    <div class="alb-front"><div class="alb-art" style="background:linear-gradient(135deg,{c[0]},{c[1]} 40%,{c[2]})"><span>{a["num"]}</span>{badge}</div><div class="alb-info"><h3>{a["title"]}</h3><p>{a["year"]}</p></div></div>
    <div class="alb-back" style="background:linear-gradient(135deg,{c[0]},{c[1]} 40%,{c[2]})"><div class="alb-back-title">{a["title"]}</div><ol class="alb-tracklist">{tracks_list}</ol><div class="alb-back-hint">tap to flip back</div></div>
  </div>
</div>\n'''
    html += '</div>\n'
    return html

def streaming_html(links):
    html = '<div class="stream-links rv">\n'
    for name, url in links.items():
        html += f'  <a href="{url}" target="_blank">{name}</a>\n'
    html += '</div>\n'
    return html

def services_html(services):
    html = '<div class="svc-grid">\n'
    for i, s in enumerate(services):
        d = f' data-d="{i}"' if i > 0 else ''
        html += f'''<div class="svc rv-rot"{d}>
  <div class="svc-num">{s["num"]}</div>
  <h3>{s["title"]}</h3>
  <p>{s["desc"]}</p>
  <div class="svc-hover-line"></div>
</div>\n'''
    html += '</div>\n'
    return html

def classes_html(classes):
    html = '<div class="classes">\n'
    for i, c in enumerate(classes):
        d = f' data-d="{i}"' if i > 0 else ''
        html += f'<div class="cls rv"{d}><span class="cls-tag">{c["tag"]}</span><h3>{c["title"]}</h3><p>{c["desc"]}</p><div class="cls-foot"><span>{c["foot_1"]}</span><span>{c["foot_2"]}</span></div></div>\n'
    html += '</div>\n'
    return html

def socials_html(socials):
    html = '<div class="socials" style="margin-top:20px">\n'
    for label, url in socials.items():
        html += f'  <a href="{url}" target="_blank">{label}</a>\n'
    html += '</div>\n'
    return html

def testimonials_html(items):
    html = '<div class="test-grid">\n'
    for i, t in enumerate(items):
        d = f' data-d="{i}"' if i > 0 else ''
        img_src = img(t["image"]) if t.get("image") else ""
        avatar = f'<div class="test-avatar"><img src="{img_src}" alt="{t["name"]}"></div>' if img_src else f'<div class="test-avatar test-avatar-placeholder"><span>{t["name"][0]}</span></div>'
        html += f'''<div class="test-card rv"{d}>
  <div class="test-quote">&ldquo;{t["quote"]}&rdquo;</div>
  <div class="test-author">
    {avatar}
    <div><strong>{t["name"]}</strong><span>{t["role"]}</span></div>
  </div>
</div>\n'''
    html += '</div>\n'
    return html

def videos_html(items):
    html = '<div class="vid-grid">\n'
    for i, v in enumerate(items):
        d = f' data-d="{i}"' if i > 0 else ''
        yt_id = v.get("youtube_id", "PLACEHOLDER")
        if yt_id == "PLACEHOLDER":
            html += f'''<div class="vid-card rv"{d}>
  <div class="vid-placeholder"><div class="vid-play-icon">▶</div><span>video coming soon</span></div>
  <div class="vid-info"><h4>{v["title"]}</h4><p>{v["desc"]}</p></div>
</div>\n'''
        else:
            html += f'''<div class="vid-card rv"{d}>
  <div class="vid-embed"><iframe src="https://www.youtube.com/embed/{yt_id}" frameborder="0" allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture" allowfullscreen></iframe></div>
  <div class="vid-info"><h4>{v["title"]}</h4><p>{v["desc"]}</p></div>
</div>\n'''
    html += '</div>\n'
    return html

def build():
    c = load_content()
    print(f"Building site v3{'  (embedded images)' if EMBED_IMAGES else '  (relative paths)'}...")
    
    s = c["site"]
    h = c["hero"]
    mu = c["music"]
    st = c["studio"]
    pb = c["photo_break"]
    g = c["gear"]
    t = c["teaching"]
    gm = c["genre_marquee"]
    ev = c["events"]
    ct = c["contact"]
    cal = c["calendar"]
    mq = c["marquee"]
    ts = c.get("testimonials", {})
    vd = c.get("videos", {})
    
    marquee_items = " ".join([f'<span class="t1">{x}</span><span class="t2">&bull;</span>' for x in mq["items"]])
    genre_items = " ".join([f'<span class="t1">{x}</span><span class="t2">&diams;</span>' for x in gm["items"]])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{s["title"]}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,WONK@0,9..144,300..900,0..1;1,9..144,300..900,0..1&family=Azeret+Mono:wght@300;400;500;600&family=Nunito:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>

<!-- Cursor glow for dark sections -->
<div class="cursor-glow" id="cursorGlow"></div>

<nav id="nb">
  <a href="#" class="nav-logo">{s["nav_logo"]}</a>
  <ul class="nav-links" id="nl">
    <li><a href="#music" onclick="cm()">Music</a></li>
    <li><a href="#studio" onclick="cm()">Studio</a></li>
    <li><a href="#gear" onclick="cm()">Gear</a></li>
    <li><a href="#videos" onclick="cm()">Watch</a></li>
    <li><a href="#teaching" onclick="cm()">Teaching</a></li>
    <li><a href="#events" onclick="cm()">Events</a></li>
    <li><a href="#contact" onclick="cm()">Contact</a></li>
  </ul>
  <button class="menu-btn" id="mb" aria-label="Menu"><span></span><span></span><span></span></button>
</nav>

<section class="hero">
  <div class="hero-video-wrap"><iframe src="https://www.youtube.com/embed/{h.get('video_youtube_id','')}?autoplay=1&mute=1&loop=1&playlist={h.get('video_youtube_id','')}&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1&enablejsapi=1" allow="autoplay" loading="lazy"></iframe><div class="hero-video-overlay"></div></div>
  <div class="deco deco-ring" style="top:15%;left:8%;opacity:.06"></div>
  <div class="deco deco-cross" style="bottom:20%;right:12%;opacity:.08;transform:rotate(15deg)"></div>
  <div class="hero-grid">
    <div class="hero-text">
      <p class="hero-tag">{h["tagline"]}</p>
      <h1><span class="word">{h["name_line1"]}</span> <span class="word">{h["name_line2"]}</span> <span class="word">{h["name_line3"]}</span></h1>
      <p class="hero-sub">{h["subtitle"]}</p>
      <div class="hero-btns">
        <a href="#music" class="btn btn-red">{h["btn_primary"]}</a>
        <a href="#contact" class="btn btn-out">{h["btn_secondary"]}</a>
      </div>
    </div>
    <div class="hero-images">
      <div class="hero-stamp-2">{h["stamp_2"]}</div>
      <div class="hero-img-main"><img src="{img(h["image_main"])}" alt="Simon Keyser Petty"></div>
      <div class="hero-img-accent"><img src="{img(h["image_accent"])}" alt="Playing guitar"></div>
      <div class="hero-stamp">{h["stamp_1"]}</div>
    </div>
  </div>
  <div class="scroll-hint"><span>scroll</span><div class="scroll-arrow"></div></div>
</section>

<div class="marquee"><div class="marquee-inner">{marquee_items}{marquee_items}</div></div>

<section id="music">
  <!-- Skull Banner -->
  <div class="skull-banner">
    <div class="skull-banner-inner">
      <img src="{img('skull_bones.png')}" alt="">
      <img src="{img('skull_1.png')}" alt="">
      <img src="{img('skull_blank.png')}" alt="">
      <img src="{img('skull_4.png')}" alt="">
      <img src="{img('skull_bones.png')}" alt="">
      <img src="{img('skull_1.png')}" alt="">
      <img src="{img('skull_blank.png')}" alt="">
      <img src="{img('skull_4.png')}" alt="">
    </div>
  </div>
  <div class="deco deco-dot" style="top:60px;right:80px;opacity:.2"></div>
  <div class="deco deco-line" style="bottom:100px;left:40px;opacity:.1;transform:rotate(-20deg)"></div>
  <div class="wrap">
    <p class="s-label rv">{mu["label"]}</p>
    <h2 class="s-title" data-split>{mu["title"]}</h2>
    <p class="s-sub rv" style="color:var(--lav)">{mu["subtitle"]}</p>
    <div class="music-layout">
      <div class="music-visual rv-s">
        <div class="music-badge">{mu["badge"]}</div>
        <div class="music-img-1"><img src="{img(mu["image_1"])}" alt="Live performance"></div>
        <div class="music-img-2"><img src="{img(mu["image_2"])}" alt="Performing"></div>
      </div>
      <div>
        {albums_html(mu["albums"])}
        {streaming_html(mu["streaming_links"])}
        <div class="section-cta rv" data-d="3"><a href="{mu.get('streaming_links',dict()).get('bandcamp','#')}" target="_blank" class="btn-cta btn-cta-coral">get the album</a></div>
      </div>
    </div>
  </div>
</section>

<section id="studio">
  <div class="deco deco-ring" style="bottom:120px;right:-40px;opacity:.05"></div>
  <div class="wrap">
    <p class="s-label rv-l">{st["label"]}</p>
    <h2 class="s-title" data-split>{st["title"]}</h2>
    <div class="studio-hero">
      <div class="studio-text">
        <p class="s-sub rv-l" style="color:var(--faded)">{st["subtitle"]}</p>
        <p class="studio-copy rv">{st["copy"]}</p>
        <div class="section-cta rv"><a href="#contact" class="btn-cta btn-cta-red">book a session</a></div>
      </div>
      <div class="studio-images rv-r">
        <div class="studio-img-1"><img src="{img(st["image_1"])}" alt="Studio"></div>
        <div class="studio-img-2"><img src="{img(st["image_2"])}" alt="Console"></div>
        <div class="studio-stamp">{st["stamp"]}</div>
      </div>
    </div>
    {services_html(st["services"])}
    <div class="quote-bar rv-s">
      <blockquote>&ldquo;{st["quote"]}&rdquo;</blockquote>
      <cite>&mdash; {st["quote_author"]}</cite>
    </div>
  </div>
</section>

<div class="photo-break">
  <img src="{img(pb["image"])}" alt="Studio moments">
  <div class="photo-break-stamp">{pb["stamp"]}</div>
</div>

<section id="gear">
  <div class="deco deco-cross" style="top:80px;left:60px;opacity:.08;transform:rotate(22deg)"></div>
  <div class="wrap">
    <p class="s-label rv">{g["label"]}</p>
    <h2 class="s-title" data-split>{g["title"]}</h2>
    <div class="gear-story">
      <div class="gear-story-img rv-l"><img src="{img(g["story_image"])}" alt="Console"></div>
      <div class="gear-story-text rv-r">{g["story_text"]}</div>
    </div>
    {gear_html(g["categories"])}
  </div>
</section>

<section id="videos">
  <div class="deco deco-dot" style="top:80px;right:60px;opacity:.15"></div>
  <div class="wrap">
    <p class="s-label rv">{vd.get("label","Watch")}</p>
    <h2 class="s-title" data-split>{vd.get("title","Sessions & Lessons")}</h2>
    <p class="s-sub rv" style="color:var(--lav)">{vd.get("subtitle","")}</p>
    {videos_html(vd.get("items",[]))}
  </div>
</section>

<section id="testimonials">
  <div class="deco deco-ring" style="top:60px;right:80px;opacity:.06"></div>
  <div class="wrap">
    <p class="s-label rv">{ts.get("label","Kind Words")}</p>
    <h2 class="s-title" data-split>{ts.get("title","What People Say")}</h2>
    {testimonials_html(ts.get("items",[]))}
  </div>
</section>

<section id="teaching">
  <div class="deco deco-dot" style="top:100px;right:100px;opacity:.15"></div>
  <div class="deco deco-line" style="bottom:80px;left:80px;opacity:.08;transform:rotate(35deg)"></div>
  <div class="wrap">
    <p class="s-label rv-l">{t["label"]}</p>
    <h2 class="s-title" data-split>{t["title"]}</h2>
    <div class="teach-layout">
      <div class="teach-img-stack rv-l">
        <div class="teach-stamp">{t["stamp"]}</div>
        <div class="teach-img-1"><img src="{img(t["image_1"])}" alt="Simon"></div>
        <div class="teach-img-2"><img src="{img(t["image_2"])}" alt="Live performance"></div>
      </div>
      <div>
        <p class="teach-intro rv">{t["intro"]}</p>
        {classes_html(t["classes"])}
        <div class="section-cta rv" data-d="3"><a href="#contact" class="btn-cta btn-cta-out">enroll now</a></div>
      </div>
    </div>
  </div>
</section>

<div class="marquee" style="background:var(--wine)"><div class="marquee-inner" style="animation-direction:reverse">{genre_items}{genre_items}</div></div>

<section id="events">
  <div class="wrap">
    <p class="s-label rv">{ev["label"]}</p>
    <h2 class="s-title" data-split>{ev["title"]}</h2>
    <div class="ev-layout">
      <div>
        <div id="live-events">
          <div class="ev-item rv"><span class="ev-date">TBA</span><div class="ev-info"><h4>Simonoto Ch.1 &mdash; Release Show</h4><p>bay area &middot; details incoming</p></div></div>
          <div class="ev-item rv" data-d="1"><span class="ev-date">Monthly</span><div class="ev-info"><h4>Celestial Hotties Night</h4><p>rotating bay area venues</p></div></div>
          <div class="ev-item rv" data-d="2"><span class="ev-date">Ongoing</span><div class="ev-info"><h4>Available for Hire</h4><p>live &middot; session &middot; private events</p></div></div>
        </div>
        <p class="rv" data-d="3" style="margin-top:24px;font-size:.8rem;color:var(--faded)">{ev["booking_text"]} <a href="#contact" style="color:var(--red);text-decoration:none;font-weight:600">{ev["booking_link_text"]}</a>.</p>
        <div class="section-cta rv" data-d="4"><a href="#contact" class="btn-cta btn-cta-dark">book a show</a></div>
        <div class="ev-img rv"><img src="{img(ev["image"])}" alt="Band" style="object-position:center 25%"></div>
      </div>
      <div class="hotties rv-r">
        <h3>{ev["hotties_title"]}</h3>
        <p>{ev["hotties_desc"]}</p>
        <a href="{ev["hotties_link"]}" target="_blank">{ev["hotties_link_text"]}</a>
      </div>
    </div>
  </div>
</section>

<section id="contact">
  <div class="deco deco-ring" style="top:80px;right:60px;opacity:.04"></div>
  <div class="wrap">
    <p class="s-label rv-l">{ct["label"]}</p>
    <h2 class="s-title" data-split>{ct["title"]}</h2>
    <div class="ct-layout">
      <div class="ct-info rv-l">
        <h3>{ct["heading"]}</h3>
        <p>{ct["copy"]}</p>
        <p style="margin-bottom:10px"><strong style="color:var(--cream)">Based in:</strong> {ct["location"]}</p>
        {socials_html(ct["socials"])}
      </div>
      <form class="ct-form rv-r" action="https://formspree.io/f/{ct["formspree_id"]}" method="POST">
        <div class="f-row">
          <div class="f-grp"><label for="name">name</label><input type="text" id="name" name="name" required></div>
          <div class="f-grp"><label for="email">email</label><input type="email" id="email" name="email" required></div>
        </div>
        <div class="f-grp"><label for="subject">interested in...</label>
          <select id="subject" name="subject">
            <option value="studio">studio s</option>
            <option value="teaching">professor of funk</option>
            <option value="session">session musician</option>
            <option value="booking">live booking</option>
            <option value="other">something else</option>
          </select>
        </div>
        <div class="f-grp"><label for="message">message</label><textarea id="message" name="message" rows="4" required></textarea></div>
        <button type="submit" class="btn-send">send it &bull;</button>
      </form>
    </div>
  </div>
</section>

<footer>
  <span class="ft-name">Simon Keyser Petty</span>
  <span>&copy; {s["copyright_year"]}</span>
  <span>{ct["location"].lower()} &middot; <a href="#contact">contact</a></span>
</footer>

<script>
const nb=document.getElementById("nb");window.addEventListener("scroll",()=>nb.classList.toggle("scrolled",window.scrollY>50));
const mb=document.getElementById("mb"),nl=document.getElementById("nl");mb.addEventListener("click",()=>{{mb.classList.toggle("active");nl.classList.toggle("open")}});function cm(){{mb.classList.remove("active");nl.classList.remove("open")}}

/* Reveal on scroll */
const revEls=document.querySelectorAll(".rv,.rv-l,.rv-r,.rv-s,.rv-rot");const revObs=new IntersectionObserver(e=>{{e.forEach(x=>{{if(x.isIntersecting){{x.target.classList.add("vis");revObs.unobserve(x.target)}}}})}},{{threshold:.06,rootMargin:"0px 0px -20px 0px"}});revEls.forEach(e=>revObs.observe(e));

/* Title char split animation */
document.querySelectorAll("[data-split]").forEach(el=>{{const t=el.textContent;el.innerHTML="";let ci=0;for(let i=0;i<t.length;i++){{const s=document.createElement("span");s.className="char";s.textContent=t[i]===" "?"\\u00A0":t[i];if(t[i]!=" "){{s.style.transitionDelay=(ci*.028)+"s";ci++}}el.appendChild(s)}}}});
const tObs=new IntersectionObserver(e=>{{e.forEach(x=>{{if(x.isIntersecting){{x.target.classList.add("anim");tObs.unobserve(x.target)}}}})}},{{threshold:.2}});document.querySelectorAll(".s-title").forEach(t=>tObs.observe(t));

/* Smooth scroll */
document.querySelectorAll('a[href^="#"]').forEach(a=>{{a.addEventListener("click",function(e){{e.preventDefault();const t=document.querySelector(this.getAttribute("href"));if(t)t.scrollIntoView({{behavior:"smooth",block:"start"}})}});}});

/* Deco parallax */
window.addEventListener("scroll",()=>{{const s=window.scrollY;document.querySelectorAll(".deco").forEach((d,i)=>{{const speed=[.02,.015,.025,.018,.022][i%5];const dir=i%2===0?1:-1;d.style.transform=`translateY(${{s*speed*dir}}px)`}})}});

/* Gear toggle */
function toggleGear(){{const el=document.getElementById("gear-full");const btn=document.getElementById("gear-toggle");if(el.style.maxHeight==="0px"||el.style.maxHeight==="0"){{el.style.maxHeight=el.scrollHeight+"px";btn.textContent="collapse \u2191";setTimeout(()=>{{el.querySelectorAll(".rv").forEach(r=>r.classList.add("vis"))}},100)}}else{{el.style.maxHeight="0px";btn.textContent="see the full rig \u2192"}}}}

/* Service card click toggle */
document.querySelectorAll('.svc').forEach(card=>{{card.addEventListener('click',()=>{{card.classList.toggle('clicked')}});}});

/* Class card click toggle */
document.querySelectorAll('.cls').forEach(card=>{{card.addEventListener('click',()=>{{card.classList.toggle('clicked')}});}});

/* Event item click */
document.querySelectorAll('.ev-item').forEach(item=>{{item.addEventListener('click',()=>{{item.classList.toggle('clicked')}});}});

/* Cursor glow on dark sections */
const glow=document.getElementById('cursorGlow');
const darkSections=['music','teaching','videos','contact'];
let glowActive=false;
document.addEventListener('mousemove',(e)=>{{glow.style.left=e.clientX+'px';glow.style.top=e.clientY+'px';const el=document.elementFromPoint(e.clientX,e.clientY);if(el){{const sec=el.closest('section,.hero');if(sec&&(sec.classList.contains('hero')||darkSections.includes(sec.id))){{if(!glowActive){{glow.classList.add('active');glowActive=true}}}}else{{if(glowActive){{glow.classList.remove('active');glowActive=false}}}}}}}});

/* Google Calendar */
const GCAL_ID='{cal["calendar_id"]}';const GCAL_KEY='{cal["api_key"]}';
async function loadShows(){{const container=document.getElementById('live-events');if(!container)return;const now=new Date().toISOString();const url=`https://www.googleapis.com/calendar/v3/calendars/${{encodeURIComponent(GCAL_ID)}}/events?key=${{GCAL_KEY}}&timeMin=${{now}}&maxResults=8&singleEvents=true&orderBy=startTime`;try{{const res=await fetch(url);if(!res.ok)throw new Error('Calendar fetch failed');const data=await res.json();const events=data.items||[];if(events.length===0){{container.innerHTML=`<div class="ev-item rv vis"><span class="ev-date">TBA</span><div class="ev-info"><h4>New shows coming soon</h4><p>follow @simonoto for announcements</p></div></div>`;return}}container.innerHTML=events.map(ev=>{{const start=ev.start.dateTime||ev.start.date;const d=new Date(start);const month=d.toLocaleString('en-US',{{month:'short'}}).toUpperCase();const day=d.getDate();const time=ev.start.dateTime?d.toLocaleString('en-US',{{hour:'numeric',minute:'2-digit',hour12:true}}).toLowerCase():'all day';const location=ev.location||'';return`<div class="ev-item rv vis"><span class="ev-date">${{month}} ${{day}}</span><div class="ev-info"><h4>${{ev.summary||'Untitled Event'}}</h4><p>${{location?location+' \u00b7 ':''}}${{time}}</p></div></div>`}}).join('')}}catch(err){{console.warn('Calendar load failed:',err)}}}}
document.addEventListener('DOMContentLoaded',loadShows);
</script>
</body>
</html>'''
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    size_kb = os.path.getsize(OUTPUT_FILE) // 1024
    print(f"\u2713 Built {OUTPUT_FILE} ({size_kb}KB)")
    if EMBED_IMAGES:
        print("  Images embedded as base64")
    else:
        print("  Images referenced as relative paths (deploy images/ folder alongside)")
    print(f"\nTo edit content: open content.json in any text editor")
    print(f"To rebuild:      python build.py")
    print(f"For deployment:  python build.py --no-embed")

if __name__ == "__main__":
    build()