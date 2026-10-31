# Sources

Status: found (known to exist) · viewed (we opened the item itself) · downloaded (copy in `raw/`) · to-request (offline, must be ordered) · blocked (site refused automated access, try in a browser).

Reuse = licence as stated by the holder. "none stated" = no statement found. "facts only" = the item is research-only; its facts may be cited, its images and text not copied.

IDs come in blocks: S01–S09 the core, S10–S39 maps, S40–S69 texts and inventory, S70–S99 pictures, S100–S129 typology, S130–S159 today's site, S160+ georeferencing, S200+ Round 3 (texts S200–S219, Qichun S220–S239, Western witnesses S240–S259, Qing pictures S260–S279, photographs S280–S299, Yangshi Lei S310–S329, archaeology and scholarship S330–S359, the park's compilations S360–S369, other S380+). A few items got two IDs from workers running in parallel. All IDs stay valid because rows cite them: S43 = S103 = S144 (圆明园戏场探微); S47 = S114 (贾珺, 祀庙祠宇); S57 = S116 = S136 (围墙历史变迁考); S46 = S107 (舍卫城); S41 = S118 (绢本四十景图); S102 = S150 (正大光明勘探报告); S104 = S138 (澹泊宁静, 光明日报); S52 = S111 (北平旧梦 125); S117 = S133 (文源阁 2025); S97 = S34 (数字圆明园); S44 = S123 (长春园 pages).

## Core

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S01 | Plan of the Yuanmingyuan Imperial Garden-Palace, unknown artist, three hanging scrolls, ink and colour on paper, 177 × 253 cm together. Princeton University Art Museum 2022-27 a-c. Provenance per the museum: Manchu official named Pai (Haidian), then Carroll Brown Malone, Bonhams San Francisco 2016, Nicholas Grindley, Princeton 2022. This is Malone's "Official Map" or his tracing of it (Q2) | 1920s per the museum; the state drawn is about Daoguang to Xianfeng (Q2) | Museum: "free access to images of works in the Public Domain", "You are welcome to download this image"; API: no restriction on the object or its 4 images; manifest has no rights field. General terms: non-commercial. Credit: "Image courtesy of the Princeton University Art Museum". No formal licence | downloaded | https://artmuseum.princeton.edu/collections/objects/138657. IIIF 4 images, in `raw/plans/`; stitched as `raw/plans/princeton_mosaic.jpg` by `scripts/mosaic_plan.py`. The base plan of this project |
| S02 | Carroll Brown Malone, History of the Peking Summer Palaces under the Ch'ing Dynasty, Illinois Studies in the Social Sciences XIX, Urbana 1934; reprint Paragon 1966 | 1934 | IA: "Copyright status reviewed by UF staff - Out of copyright". Facts cited | viewed | https://archive.org/details/historyofpekings00malo. Full OCR text. Scenes, measures on the ruins, Official Map App. II pp.231-232 |
| S03 | OpenStreetMap, the park and neighbours, Overpass | fetched 2026-10-31 | ODbL, (c) OpenStreetMap contributors | downloaded | `scripts/fetch_osm.py` → `raw/osm/overpass.json`, `layers/osm_today.geojson`. WGS84 checked against Esri (2.7 m E, 1.8 m N over 54 outlines) |
| S04 | Copernicus DEM GLO-30, tiles N39 and N40 E116 | TanDEM-X 2011-15 | free with source notice | downloaded | `raw/dem/`; clip by `scripts/clip_dem.py`. See `terrain/README.md` |
| S05 | 《日下旧闻考》 Rixia jiuwen kao (Yu Minzhong et al.), juan 80-85, Kanripo KR2k0036, WYG base | 1780s | public domain | viewed | https://github.com/kanripo/KR2k0036 (repo path assumed by the worker; the text came from an earlier fetch), also ctext. 526 quotes in `plan/inventory_texts.csv` checked by script |
| S06 | zh.wikipedia 圆明园, 圆明园四十景, 长春园, 绮春园, 西洋楼 | fetched 2026-10-31 | CC BY-SA | viewed | https://zh.wikipedia.org/wiki/圆明园. Leads, B at best |
| S07 | en.wikipedia Old Summer Palace | fetched 2026-10-31 | CC BY-SA | viewed | https://en.wikipedia.org/wiki/Old_Summer_Palace |
| S08 | 圆明园四十景图 Forty Scenes album, Tangdai and Shen Yuan, 40 leaves, BnF Estampes RESERVE FT 6-B-9, one BnF record per leaf; poems Qianlong, calligraphy Wang Youdun | 1744 | Gallica: free for non-commercial reuse with "Source gallica.bnf.fr / BnF"; Commons PD tags per file. Gallica's licence page itself could not be opened (Cloudflare 403) | viewed on Commons; Gallica blocked | https://gallica.bnf.fr/ark:/12148/btv1b55008362z ; catalogue.bnf.fr/ark:/12148/cb43814226p (leaf 1) |
| S160 | Esri World Imagery tiles, z17-18 | fetched 2026-10-31 | provider's terms; never in git; kept in scratch for checks only | viewed | https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}. Winter image, lakes iced |

## Maps and plans

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S10 | 《圓明園全圖》 2 sheets, Yangshi Lei 样式雷, National Library of China 国家图书馆 | undated in my source; collection mostly Daoguang-Tongzhi | research-only (not stated online) | to-request | named in 卷序, https://book.douban.com/review/10163867/ (reprint of book front matter). three gardens overall; best candidate for layout, state to be read per sheet |
| S11 | 《圓明園大墻尺丈并外圍水道地盤全樣》 1 sheet, NLC; probably the same as 圆明园大墙丈尺及周边园林总平面图, 样式雷排架098-3, ink, light colour, vermilion, red slips, 569×415 mm (identity of the two: assumed) | 1811-1827 per mhymy | site CC BY-NC-SA for its text; plan images belong to holders; image paywalled | viewed (record), image not seen | https://www.mhymy.com/dasl/ysltd/5069.html. outer wall lengths N 528.9丈, E 285丈, W 375丈, S 695.6丈 (about 1692/912/1200/2226 m if 1丈=3.2 m, an assumed value): independent scale check on S01 |
| S12 | NLC river plans: 《圓明園河道全圖》 国图043-0003 (Qianlong middle-late, with Jiaqing ink changes, search snippet); 《長春園内圍河道全圖》 国图064-0001; 《綺春園河道》 国图097-0002; 《圓明園附近河道全圖》 1 sheet | 18th-19th c. | research-only | to-request | https://book.douban.com/review/10163867/. water system, earliest overall plan |
| S13 | 《国家图书馆藏样式雷图档·圆明园卷初编》 十函, ISBN 978-7-5013-5718-5, ¥50,000, contents open with 全图; 续编 covers 九州清晏, 长春园, 万春园. 初编 473 drawings + 61 texts; 续编 656 + 169 | 2016 and later | research-only | to-request | https://www.nlcpress.com/ProductView.aspx?Id=7642. the practical way to all S10-S12; ask a library |
| S14 | 张恩荫, "样式雷"图与圆明园（中）, 圆明园遗址公园 on Sohu | 2017 | none stated | viewed | https://www.sohu.com/a/149543065_660430. reliability ratings of S15-S18; parts 上 and 下 not found |
| S15 | 《实测圆明园长春园万春园遗址形势图》, 北平市政府工务局, 1:2,000, colour, 150×106 cm, surveyed Dec 1933, printed Nov 1936. Copies: three known plus 康睦's gift to the park; NLC holds one | 1933/36 | research-only; no scan found | to-request | https://www.rmzxw.com.cn/c/2021-02-22/2789477.shtml ; https://www.chinaservicesinfo.com/s/202102/24/WS6035b1c7498e7a02c6f693eb/old-summer-palace-map-returned-to-original-site.html. water, hills, foundations; grade B |
| S16 | 金勋 Jin Xun, 100 plans of the gardens, NLC | 1965 | research-only | found | via S14. S14: names about 50% credible; some Jiuzhou Qingyan plans mix three reigns. The c.1930s 复原图 and 北平西郊 map in the brief: nothing found |
| S17 | 何重义 He Chongyi, 《圆明三园总平面图》 | 1979 | research-only | found | via S14. S14: 缺乏年代同一性; names about 70%. Do not use for positions |
| S18 | 《圆明园匾额略节》, 张仲葛 family; published 1983 | late Xianfeng | facts cited | found | via S14. 1044 plaque names just before 1860, so the best name list for the target state; misses 74 places, 86 plaques. Pass to inventory worker |
| S19 | G. Bouillard, Carte des environs de Peking, 1:25,000, 20 sheets 37×51 cm, publ. A. Nachbaur per UZH; HKUST G7824.P4 B6 1923, DOI 10.14711/spcol/b563234. E116°03'-116°48', N40°05'-39°45'. Full scan about 12200×9000 px, about 1 px/m | 1923 | HKUST: CC BY-NC-ND 4.0 ("Most digital materials"), so research-only; 1923 map itself old | viewed at 700 px; downloaded previews | https://digitalcollections.hkust.edu.hk/Detail/objects/b563234 ; terms https://digitalcollections.hkust.edu.hk/About/terms_of_use. site lies across HKUST Map 2 lower right, Map 3 lower left, with Map 7 upper left to its south (read from previews; exact fit to be georeferenced). Walls, lakes, roads, villages, contours before urbanisation. Georeferencing bridge. IIIF size requests answer "Key cannot be empty", and the terms route high resolution through a Request Form, so I did not assemble viewer tiles. |
| S20 | GSGS 3789 / AMS Eastern China 1:50,000, Peking, sheet 16/2200, 3rd ed. AMS 3, 1944, printed 1945 | 1926/1944 | PCL FAQ: most maps "are in the public domain ... No permissions are needed" | downloaded | https://maps.lib.utexas.edu/maps/ams/eastern_china/txu-pclmaps-oclc-6637182-peking.jpg (also Princeton ark:/88435/9019s4357). north neat line 40°00': shows Haidian, Wanshoushan, Kunming Hu, Yenching, Tsinghua, not Yuanming Yuan. Free tie points for landscape |
| S21 | GSGS 3789 sheet 16/2220, the sheet north of S20 (from S20's index) | 1926+ | PD if AMS print | to-request; not at PCL, Yale or Princeton so far | none. the free survey that would show the gardens |
| S22 | Plan des environs du Palais d'été, after Capt. Bouvier, Le Tour du monde 10, p.112 | 1864, 1860 campaign | Commons: Public domain | downloaded | https://commons.wikimedia.org/wiki/File:Le_Tour_du_monde-10-p112.jpg. schematic; only an 1860 witness of the enceinte, the gate and Hai-tien. Credit, not positions |
| S23 | Malone 1934 plates (part of S02): p.52 sketch map of three gardens, p.72 and p.99 portions of the Official Map, p.140 Foreign Buildings (not viewed), p.16 region. Book page = leaf-3 near these pages | 1934 | IA: "Copyright status reviewed by UF staff - Out of copyright"; treated research-only until checked | downloaded pp.52, 72, 99 at 2400 px | https://archive.org/details/historyofpekings00malo. only images of the likely ORIGINAL with flap and tints |
| S24 | Peking, Kgl. Preuss. Landes-Aufnahme, 1:17,500, survey 1900/01, 75×64 cm | 1903 | Leventhal: "No known copyright restrictions. No known restrictions on use." | viewed (record) | https://collections.leventhalmap.org/search/commonwealth:9s161h74w. GeoTIFF offered; city-centred, sheet size suggests it stops short of the gardens (assumed from scale, not opened) |
| S25 | Peking und Umgebung, Prussian Army 1907; GSGS 2417 "Peking and Environs" 1909, based on it | 1907/09 | PD likely, unchecked | found (dealers) | https://www.themaphouse.com/artworks/categories/32/264613-prussian-army-peking-und-umgebung-1907. possibly the earliest survey of the gardens; scale unknown; try NLS, Staatsbibliothek |
| S26 | 實測京師四郊地圖, ROC Interior Ministry, about 1:36,200 | 1915 | none seen | found | https://www.geographicus.com/P/AntiqueMap/BeijingSuburbs-roc-1915 (403); SOAS CWM.LMS.15.14.048, 1:36,000, maybe the same. reaches NW to Yangtai Shan per snippet |
| S27 | LoC 2006626568, Beijing and vicinity / Beijing cheng jiao tu | 1886 per snippet | LoC normally none; unchecked | blocked | https://www.loc.gov/item/2006626568. names the Yuanming site |
| S28 | LoC 2006626637, [Beijing Yi he yuan he ba qi bing ying], ms., 97×172 cm | 1888 per snippet | unchecked | blocked | https://www.loc.gov/item/2006626637/. post-1860 manuscript of the area, banner camps |
| S29 | LoC, Pekin kinbo zu 北京近傍図, Japanese | 1900 per snippet | unchecked | blocked | LoC search; no item number. early environs survey |
| S30 | 最詳北平四郊圖, about 1:44,400 | 1937 | unchecked | found | https://www.geographicus.com/P/AntiqueMap/BeijingSuburbs-baimeichu-1937_d. 1930s suburbs |
| S31 | Environs de Peking, Japan Tourist Bureau, about 1:25,000 per snippet, Harvard g7824 b4 1920 j3 | c.1920 | unchecked | blocked | https://hgl.harvard.edu/catalog/harvard-g7824-b4-1920-j3. maybe a Bouillard derivative |
| S32 | USGS Declassified Satellite Imagery 1 (CORONA), DOI 10.5066/F78P5XZM. "Sources/Usage: Public Domain." KH-4A 8/1963-9/1969 best 9 ft; KH-4B 9/1967-5/1972 best 6 ft. | 1960-72 | Public Domain | to-request | http://www.usgs.gov/centers/eros/science/usgs-eros-archive-declassified-data-declassified-satellite-imagery-1. last look before the 1970s-80s changes. No frame ID obtained: M2M 403 without login, EarthExplorer needs an account, no paper with a Beijing frame found. CAST Corona Atlas: I tested all 2214 footprints from https://corona.cast.uark.edu/corona/get_raster_names on the site envelope: 0 hits; nearest 1108-1054Aft, Dec 08 1969, ends 39.81 N. |
| S33 | UCLA East Asian Archaeology Corona Collection, 204 images of China | 1960s-70s | unread | found | https://calisphere.org/collections/28278/. Beijing coverage unconfirmed (page returned 202, empty) |
| S34 | 数字圆明园, 清华 郭黛姮, 贺艳 team; used 1933, 1965 and 2002 topographic maps | 2009+ | research-only, cite only | found | https://www.tsinghua.edu.cn/info/1366/81418.htm. cross-check of facts |
| S35 | 《圆明园遗址公园规划》, adopted 2000 per press | 2000 | research-only | found (search snippet, exact URL not pinned); plan drawing not found | none. today's park zones; ask the site worker |
| S36 | Gisbert Combaz, Les palais impériaux de la Chine, Annales Soc. d'Archéologie de Bruxelles, Vromant, 31 plates | 1909 | author's death date not checked | found (bookseller snippet on livre-rare-book.com, exact listing not pinned); IA none | none. whether it plans Yuanming Yuan: unconfirmed |
| S37 | Maurice Adam, Yuen Ming Yuen: L'oeuvre architecturale des anciens jésuites au XVIIIe siècle, Peking 1936; reviewed JAOS 57(1):126, 1937 | 1936 | unknown | found; no scan found; Gallica SRU 403 | https://dc2.philarchive.org/rec/MALYMY. Xiyang Lou plans |
| S38 | Hope Danby, The Garden of Perfect Brightness, 1950 | 1950 | research-only | to-request; IA none | none. plan, secondary |
| S39 | Osvald Siren, Gardens of China, 1949 | 1949 | IA borrow only | to-request | https://archive.org/details/bwb_S0-EFL-374. plans not viewed |

## Texts and inventory

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S40 | 御制圆明园四十景诗 / 图咏 | 1744+ | public domain (pre-1900) | found; prose prefaces read inside S05 | poems |
| S41 | 《圆明园四十景》图的价值, 清代皇家园林研究中心 (中国人民大学清史研究所), author given as 皇家园林, 2020-09-25 | 2020 | none stated: facts only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/jzys/8eef05885c3e4279ae0132f1a37a13c9.htm. album vs plans vs excavation: what changed, by scene |
| S42 | 梦回圆明园 mhymy.com: 档案史料 reports (11301, 11446, 11467, 11480, 11559, 11828, 12205, 12324, 12600, 12613, 12739) and scene list /ymss/jqjs/ymy | 2022-23 posts | site: CC BY-NC-SA notice on texts it republishes; facts only | viewed (free part only, rest paywalled); site refused me today (TLS EOF), used earlier fetch in palace_r1_site/raw | https://www.mhymy.com/dasl/12600.html etc.. dimensions, dates |
| S43 | 圆明园戏场探微, 圆明园遗址公园 site | 2021 | none stated: facts only | viewed (earlier fetch) | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483509.html. theatres, dated additions, archive citations |
| S44 | 澹怀堂, 圆明园遗址公园 site | 2011-18 | site: all rights reserved | viewed (earlier fetch); site timed out today | http://www.yuanmingyuanpark.cn/cgll/zyjd/ccy/201101/t20110105_231501.html. CC01 |
| S45 | 郭黛姮 lecture 對圓明園古建筑的再認識, 人民网 | 2020 | none stated | viewed | http://culture.people.com.cn/BIG5/n1/2020/1107/c1013-31922261.html. 1745 Changchun, 文源阁 |
| S46 | 仅存于图纸上的圆明园舍卫城, 北京日报 | 2020-01-09 | none stated | viewed | https://view.inews.qq.com/k/20200108A0M0Q400. 舍卫城 dig, fate by photos |
| S47 | 贾珺 圆明三园中的祀庙祠宇建筑探析, 故宫博物院院刊 2012 no.3 | 2012 | none stated | downloaded by earlier worker (palace_r1_typo/dl_jia/jia.pdf, stay in scratch or raw) | https://www.dpm.org.cn/Uploads/File/2018/06/15/u5b23730ae0e5a.pdf. 33 shrines, dates |
| S48 | Blog 游客小余, 207 圆明园（长春园之单独景点） | 2017 | none: lead only | viewed | sina blog, see below. CC details, lead |
| S49 | Blog yaffin, 【圆明园】系列15 长春园 绮春园 遗址现状 | c. 2011 | none: lead only | viewed | sina blog, see below. Changchun and Qichun chronology, lead: seems to copy park or 张恩荫 texts, unverified |
| S50 | Blog 双飞燕, 系列06 四十景现状 之一 |  | none: lead only | viewed | sina blog, see below. 慎德堂 1830 variant |
| S51 | Blog yaffin, 系列11 四十景现状 之六 (31-35) |  | none: lead only | viewed | sina blog, see below. 观澜堂, 别有洞天 |
| S52 | Blog 北平旧梦, 老北京的记忆（125）圆明园涵虚朗鉴与接秀山房遗址 |  | none: lead only | viewed | sina blog, see below. 观澜堂 size |
| S54 | 北京必游景点推荐 圆明园, 北京旅游网 | 2018-06-07 | none stated | viewed | https://www.visitbeijing.com.cn/article/47QkVhww6K6. variant dates; tourist text |
| S55 | Bonhams HK, 4 June 2015, lot 57 footnote, citing 何燕 紫禁城 2012-01 | 2015 | none stated | viewed | https://www.bonhams.com/auctions/22882/lot/57. 清晖阁 demolition |
| S56 | 圆明园"西洋楼"与中国近代建筑史, in 三十年雁迹泥痕 (1985-2014), Tsinghua UP sample chapter; talk of 1985-11-29; author not on the pages I read | 1985/2014 | publisher sample | viewed (earlier fetch) | http://www.tup.tsinghua.edu.cn/upload/books/yz/061622-01.pdf. builders, 1745-59, engravings 1786 |
| S57 | 圆明园围墙历史变迁考, 圆明园遗址公园 site | 2021 | none stated | viewed (earlier fetch) | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483376.html. modern rebuilds |
| S58 | 嘉庆 御制绮春园三十景诗 and 绮春园记 (in 仁宗御制诗文) | c. 1805 | public domain | found (cited by S06, S49; not opened) | to-request. QC scene list at source |
| S59 | 张恩荫 article on the start date (2005, cited by S06) | 2005 |  | found | to-request. 1707 |
| S60 | 中国第一历史档案馆 编 《圆明园》(清代档案史料) 上海古籍 1991, cited by S47 | 1991 | archive book | to-request | 1873 survey p.1119, dated orders |
| S61 | 郭黛姮《远逝的辉煌》 (assumed from memory, not verified online today) | c. 2009 | book | to-request | layouts |
| S62 | 《圆明园》丛刊, 中国圆明园学会 (cited by S47; 圆明园匾额略节 in vol.2) | 1981+ |  | to-request | plaques of Xianfeng date |

## Pictures

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S70 | Wikimedia Commons, categories Old Summer Palace, Yuanmingyuan, Forty Scenes, engravings | - | per file | viewed | commons.wikimedia.org/wiki/Category:Old_Summer_Palace. hub |
| S71 | 圆明园铜版画册, Palace Museum 228650, 20 leaves, 50.5 x 87.5 cm | 清 | no statement in page text; Commons PD-Art | PD-old-100 | viewed. dpm.org.cn/collection/paint/228650.html | plates |
| S72 | Getty Research Institute 86-B26695 | 1783-86 | (c) Getty Trust, All rights reserved (MIT DOME, snippet) | found | getty.edu/art/exhibitions/china_paper/. second set, sequence |
| S73 | Chester Beatty Library C 1608, on Commons | 1781/87 | Commons PD-Art | viewed | Commons file. sharp plate 1 |
| S74 | V&A O398692 etc.; British Museum A_1924-0523-0-16; Honolulu 13076-78 | - | not read | found | collections.vam.ac.uk/item/O398692. other holders |
| S75 | MIT Visualizing Cultures, Garden of Perfect Brightness (Lillian Li) | 2012 | CC BY-NC-SA footer | viewed | visualizingcultures.mit.edu/garden_perfect_brightness/. text, low-res set |
| S76 | Différents palais et temples, BnF cb403581603, woodcuts after Sun Hu, Shen Yuan | 1745 | Gallica rule; Commons PD | viewed on Commons | Gallica btv1b10520496k. line version |
| S77 | Haitien. Maison de Plaisance, BnF cb43831905b, 40 gouaches, ex Bertin | 1750-92 | same | viewed on Commons | catalogue.bnf.fr/ark:/12148/cb43831905b. colour copy |
| S78 | Vues de l'une des maisons, BnF PET FOL-OE-18, 19 drawings | 1794 | same | viewed on Commons | Gallica btv1b10501744g. Xiyang Lou copy |
| S79 | Le Rouge, Jardins anglo-chinois, cahiers XV-XVI | 1786 | Commons PD | viewed | Commons. reception |
| S80 | Le Tour du monde vol. 10 | 1864 | Commons PD | viewed | hathitrust mdp.39015080000451. reception, plan |
| S81 | Album of photographs of Peking and its environs, Cornell catalog 2527150 (Afong per Commons) | c.1879 | Commons PD-old-70-expired | viewed on Commons, Cornell not opened | newcatalog.library.cornell.edu/catalog/2527150. surviving halls |
| S82 | Thomson, Through China with a Camera | 1899 | Commons PD | viewed on Commons | archive.org/details/throughchinawith00thomrich. check captions. Wellcome API query: 0 hits |
| S83 | Mumm, Ein Tagebuch in Bildern | 1902 | Commons PD | viewed on Commons | dsr.nii.ac.jp/toyobunko/La-161/V-1/. ruins 1901 |
| S84 | zeno.org Fotografien, Child PHO01298 | 1877-78 | PD-Art-Zeno | viewed on Commons | zeno.org. ruin |
| S85 | Historical Photographs of China, Bristol | - | CC BY-NC-ND 4.0, research with provenance | viewed; search 429 | hpcbristol.net/about. Child, Morrison, Moore. Ask hums-chinaphotos@bristol.ac.uk |
| S86 | Östasiatiska museet, Sirén and Andersson, K-samsök | 1922 etc. | per record: CC0, PDM or BY-NC-ND | viewed | kulturarvsdata.se/SMVK-OM/Bildarkiv/199644. best captioned ruin set, 88 hits, 40ish on this garden |
| S87 | Rijksmuseum | c.1892 | CC0 | viewed on Commons | Commons. Rijks page |
| S88 | Bundesarchiv Bild 137-000605 | 1900 | CC BY-SA 3.0 de | viewed on Commons | Commons. 正觉寺 |
| S89 | Ohlmer photographs (Commons copies) | 1873 | Commons PD; no holder | viewed | hpchina.blogs.bristol.ac.uk/?p=5504. dating, 12 negatives |
| S90 | Régine Thiriez, Barbarian Lens | 1998 in the brief; a search result says 1994 | book | to-request | muse.jhu.edu/article/47549 (review). attribution, positions |
| S91 | C. F. Moore fonds, Royal BC Museum MS-3171 (blog: visualisingchina.net 2022-05-15) | c.1875-1880s | not read | found; blog viewed | search-bcarchives.royalbcmuseum.bc.ca/c-f-moore-fonds. 12 views, re-attributions |
| S92 | Hedda Morrison, Harvard-Yenching | 1933-46 | all rights reserved, written permission | found | hpcbristol.net/visual/Hv20-060. relief detail |
| S93 | Sidney Gamble, Duke | 1917-32 | not read | blocked (bot check) | repository.duke.edu/dc/gamble. unsearched |
| S94 | Passet, Albert Kahn | 1912-13 | not read | found: Yiheyuan, no Yuanming Yuan item seen | fca.huma-num.fr/s/fca/item/23. probably nothing |
| S95 | Beato, National Gallery of Art | 1860 | CC0 | viewed on Commons | purl.org/nga/collection/artobject/163388. not this garden |
| S96 | Yongzheng twelve months, Palace Museum digicol | Yongzheng | Commons PD-Art | viewed on Commons | digicol.dpm.org.cn. garden life |
| S97 | 数字圆明园, Tsinghua | 2009- | none; research-only | found | tsinghua.edu.cn/en/info/1255/9531.htm. facts only, B |
| S98 | 御製圓明園圖詠, Commons SSID-13617936, 150 pp PDF: colophon on PDF p.2 reads 光緒十三年七月天津石印書屋敬謹摹勒上石. Same 1887 edition as S260, but this scan has the text only, no picture spreads | 1887 | Commons LicenseShortName: Public domain | viewed | https://commons.wikimedia.org/wiki/File:SSID-13617936_%E5%BE%A1%E8%A3%BD%E5%9C%93%E6%98%8E%E5%9C%92%E5%9C%96%E8%A9%A0.pdf. Update of the existing S98 row: edition now read. Pictures are in S260. |
| S99 | 院本十二月令图 | - | - | to-request | none found. - |

## Typology and dimensions

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S100 | 《工程做法》, 允礼等撰, 北大 scan via CADAL, Internet Archive | 1734 | PD by age | viewed (page images; OCR junk) | https://archive.org/details/02090256.cn and https://archive.org/details/02090263.cn (n76). primary rule, type list |
| S101 | 曲阜三孔古建, 《中国营造技术知识点——清代建筑的通则》, Sohu | 2020 | unclear, research-only | viewed | https://www.sohu.com/a/390219687_100017881. Qing rule summary |
| S102 | 《正大光明区域考古勘探报告》, 梦回圆明园 档案 page, free part only | n.d. | unclear, research-only | viewed in part (rest paywalled) | https://www.mhymy.com/dasl/12324.html. 大宫门 台基, 影壁 |
| S103 | 黄赛丰, 《圆明园戏场探微》, 圆明园官网 | 2021 | site reserves rights | viewed | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483509.html. stages, towers |
| S104 | 李韵, 王笑妃, 《圆明园澹泊宁静遗址发掘获重要成果》, 光明日报 via 中新网 | 2022 | research-only | viewed | https://www.chinanews.com.cn/cul/2022/11-14/9893900.shtml. 田字房 excavated |
| S105 | 杨菁 等, 《圆明园文源阁》, 《圆明园研究》63 | 2022 | site reserves rights | viewed | http://www.yuanmingyuanpark.cn/xs/ktsb/202201/t20220128_4510628.html. chi = 0.32 m, 文源阁 丈尺册 |
| S106 | 单志刚, 《圆明园中的正大光明殿》, 人大清史所 site | 2022 | research-only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/lswh/7dca16cf3b144adc892b1d0b14d24e60.htm. 正大光明 column |
| S107 | 《仅存于图纸上的圆明园舍卫城到底什么样》, 腾讯新闻 | 2020 | research-only | viewed | https://view.inews.qq.com/k/20200108A0M0Q400. 舍卫城 墩台 |
| S108 | Gao Ming et al., Digital restoration ... Xieqiqu, ISPRS Annals II-5/W3 | 2015 | per publisher, check before reuse | viewed | https://doi.org/10.5194/isprsannals-II-5-W3-75-2015. 谐奇趣 form, method |
| S109 | 刘阳, 《圆明园的故事》 excerpt, 澎湃 | 2017 | research-only | viewed | https://www.thepaper.cn/newsDetail_forward_1750908. Xiyang Lou facts |
| S110 | 人民网, 海晏堂蓄水楼加固 | 2016 | research-only | viewed | http://house.people.com.cn/n1/2016/0728/c164220-28590471.html. core height, casing |
| S111 | 北平旧梦, 老北京的记忆（125）, blog quoting 《圆明园百景图志》 | 2017 | research-only | viewed | https://blog.sina.com.cn/s/blog_88741e0d0102x6gc.html. 丈尺 of many halls |
| S112 | 北平旧梦, 老北京的记忆（81）, blog quoting the 宫门区 report | n.d. | research-only | viewed | https://blog.sina.com.cn/s/blog_88741e0d0102w60j.html. 澹怀堂, 宫门 |
| S113 | 《万字房的"前世"与"重生"》, 梦回圆明园 | 2023 rev. | research-only | viewed | https://www.mhymy.com/xsjl/14213.html. 万字房 丈尺 |
| S114 | 贾珺, 《圆明三园中的祀庙祠宇建筑探析》, PDF at 故宫博物院 site | n.d. | research-only | viewed | https://www.dpm.org.cn/Uploads/File/2018/06/15/u5b23730ae0e5a.pdf. 土地庙, 吕祖亭 |
| S115 | Article on 买卖街, 人大清史所 site | 2021 post | research-only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/hwyj/4115411323ba4429a9ecc9ae5b2bc2e5.htm. shop sizes |
| S116 | 《圆明园围墙历史变迁考》, 圆明园官网 | 2021 | site reserves rights | viewed | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483376.html. wall |
| S117 | 《圆明园文源阁遗址考古成果发布》, 新华网 | 2025 | research-only | viewed | http://www.news.cn/local/20250113/42158ce447b64aab8b6590fd52fddf3c/c.html. 文源阁 dig, 虎皮石 |
| S118 | Article on the 绢本四十景图, 人大清史所 site; author not shown | 2020 post | research-only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/jzys/8eef05885c3e4279ae0132f1a37a13c9.htm. roof and plan variety |
| S119 | 《现存几张正大光明殿图像述评（连载·二）》, 中国圆明园学会 blog | n.d. | research-only | viewed | https://blog.sina.com.cn/s/blog_50feaf600100dc69.html. 正大光明 images, 月台 |
| S120 | Long Corridor text, Visit Beijing | n.d. | research-only | viewed | https://www.visitbeijing.com.cn/article/4JXy25o2h1A. gallery comparable |
| S121 | 畅音阁 texts, 本地宝 and Visit Beijing | n.d. | research-only | viewed | https://m.bendibao.com/show683011.html ; https://www.visitbeijing.com.cn/article/47QtXfWkDiW. tower comparable, height and tile |
| S122 | yaffin, 【圆明园】系列09, blog | n.d. | research-only | viewed | https://blog.sina.com.cn/s/blog_65fec3ab0100sv4p.html. 安佑宫, 月地云居 forms |
| S123 | 长春园 page, 圆明园官网 | 2011 | site reserves rights | viewed | http://www.yuanmingyuanpark.cn/cgll/zyjd/ccy/201101/t20110105_231501.html. 长春园牌楼门 column |
| S125 | 《关于〈工程做法〉若干问题的思考》, 《建筑史学刊》 2026 | 2026 | research-only | viewed abstract only | https://www.jgcm.ac.cn/jah/article/doi/10.12329/20969368.2026.02015. warning on texts |
| S126 | Paper on 工程做法则例, 名古屋工業大学 repository (year from the filename) | 2002 | research-only | found (503 on fetch) | https://nitech.repo.nii.ac.jp/record/2086/files/bnit2002_185.pdf. 74 juan, 27 types |
| S127 | 梁思成, 《清式营造则例》; 《清工部工程做法则例图解》 | 1934; later | book | to-request | rule source |
| S128 | 郭黛姮, lecture text 《重返圆明园》, Tsinghua UP sample; Tsinghua news on her team | 2020 | research-only | first viewed, second found | https://www.tup.com.cn/upload/books/yz/089340-01.pdf ; https://www.tsinghua.edu.cn/info/1366/81418.htm. 谐奇趣 glazed tile, 内工则例 used |
| S129 | 郭黛姮, 《〈圆明园内工则例〉评述》, in a volume on 清代则例 (contents list only) | n.d. | book | found | https://pre.iudicium.de/assets/content/programm/isbn-978-3-89129-405-5/iudicium-9783891294055-inhalt-moll-murata-chinese-handicraft-regulations.pdf. 内工则例 lead |

## Today's site, archaeology and terrain

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S130 | 南方都市报 via 中新网, 圆明园的前世今生 (4) | 2010 | facts only | viewed | https://www.chinanews.com.cn/cul/2010/10-13/2583933.shtml. 1983-1993 park history |
| S131 | 北京日报 via 中国日报网, 国家文物局 reply | 2020 | facts only | viewed | https://cn.chinadaily.com.cn/a/202011/11/WS5fab3b1aa3101e7ce972ed3f.html. 十三五 excavations |
| S132 | 中新网 via 中国日报网 大宫门 (2019-01-29); 新京报 via 中新网 紫碧山房 (2017-12-15) | 2017, 2019 | facts only | viewed | https://cn.chinadaily.com.cn/a/201901/29/WS5c4fad50a31010568bdc713a.html ; https://www.chinanews.com.cn/sh/2017/12-15/8400775.shtml. 大宫门 finds, 紫碧山房 finds |
| S133 | 张利芳, 人民日报海外版 via 新华网, 文源阁 | 2025 | facts only | viewed | https://www.news.cn/local/20250113/42158ce447b64aab8b6590fd52fddf3c/c.html. 文源阁 |
| S134 | 新华网 2024-09-23; 北京晚报 via visitbeijing 2024-12-08; 总台 via 凤凰网 | 2024 | facts only | viewed | https://www.news.cn/culture/20240923/b26ae171b28e4738bcd55628a67a8a7d/c.html ; https://www.visitbeijing.com.cn/article/4KZpPJfexIh ; https://news.ifeng.com/c/8eTlzYasshZ. 文源阁 area, culverts |
| S135 | 中华网, 圆明园京西稻插秧 | 2026 | facts only | viewed | https://m.tech.china.com/hea/articles/20260629/202606291904449.html. paddy at 多稼如云 today |
| S136 | 圆明园管理处, 圆明园围墙历史变迁考 | 2021 | site copyright, facts only | viewed | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483376.html. walls |
| S137 | 中新网 徐婧, 澹泊宁静 | 2022 | facts only | viewed | https://www.chinanews.com.cn/cul/2022/11-04/9887558.shtml. 田字房 |
| S138 | 光明日报 via 中新网, 澹泊宁静 | 2022 | facts only | viewed | https://www.chinanews.com.cn/cul/2022/11-14/9893900.shtml. 田字房, paddy |
| S139 | 中国日报网, 圆明园遗址考古有重大发现 | 2020 | facts only | viewed | https://cn.chinadaily.com.cn/a/202012/16/WS5fd95d4aa3101e7ce9735684.html. 澹泊宁静 scene size |
| S140 | 华西都市报 via 中证网, 揭秘圆明园考古 | 2017 | facts only | viewed | https://cs.com.cn/ssgs/gssc/201707/t20170710_5365575.html. campaigns, 如园 |
| S141 | 浙江在线, 考古推进至大水法 | 2016 | facts only | viewed | https://china.zjol.com.cn/gnxw/201606/t20160612_1619014.shtml. 养雀笼, 大水法 |
| S142 | 京华时报 via 浙江在线, 长春园宫门 | 2016 | facts only | viewed | https://china.zjol.com.cn/gnxw/201610/t20161019_2006451.shtml. entrances, 86 remains |
| S143 | 靳枫毅等, 北京圆明园含经堂遗址2001~2002年度发掘简报, 考古 2004(2): 41-65 | 2004 | research-only | found (abstract); to-request | https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_cass_nssd_9325303. 含经堂 |
| S144 | 黄赛丰, 圆明园戏场探微, 管理处 | 2021 | site copyright, facts only | viewed | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483509.html. stage sizes; 五园 note |
| S145 | 陈徒手, 1971年圆明园告急之后, 人文中国 | n.d. | facts only | viewed | https://humanitieschina.substack.com/p/1971. destruction and removals 1956-2006 |
| S146 | 景观中国, 修复斥资4.6亿 (宗天亮) | c. 2005 | facts only | viewed | http://www.landscape.cn/news/8596.html. state of hills and water vs 1933 map |
| S147 | 新浪, 圆明园2008年前建成遗址公园 | 2005 | facts only | viewed | https://news.sina.com.cn/c/2005-05-25/02565978324s.shtml. 331 ha, earth moved |
| S148 | 北京青年报 via 雅昌 2013; 徐百柯 via 爱思想 2005; 新浪财经 2005 | 2005, 2013 | facts only | viewed | https://m-news.artron.net/20130713/n476712.html ; https://www.aisixiang.com/data/6296.html ; https://finance.sina.com.cn/g/20050811/1023259704.shtml. NW works, seepage membrane |
| S149 | 西洋楼区域考古勘探报告, mhymy | n.d. | research-only | viewed (free part) | https://www.mhymy.com/dasl/12205.html. 西洋楼 size |
| S150 | 正大光明区域考古勘探报告, mhymy | n.d. | research-only | viewed (free part) | https://www.mhymy.com/dasl/12324.html. 正大光明, 大宫门 |
| S151 | 九洲清晏区域考古勘探报告, mhymy | n.d. | research-only | viewed (free part) | https://www.mhymy.com/dasl/12600.html. 九洲清晏 |
| S152 | 上下天光区域考古勘探报告, mhymy | n.d. | research-only | viewed (free part) | https://www.mhymy.com/dasl/12739.html. 上下天光 |
| S153 | 北京市文物研究所, 远瀛观遗址考古发掘简报, mhymy | after 2016 | research-only | viewed (abstract) | https://www.mhymy.com/dasl/12613.html. 远瀛观 |
| S154 | 北京市文物研究所, 大宫门区域考古发掘简报, mhymy; 北京市文物局 2016 request | n.d. | research-only | found | https://www.mhymy.com/dasl/12331.html ; https://wwj.beijing.gov.cn/eportal/immovableDir/bjww/resource/cms/2020/04/2020041521034167415.doc. wishlist |
| S155 | 北京市文物研究所 surveys 2007-2009, mhymy ids 11467, 11480, 11446, 11301, 11419, 11559, 11669 | 2007-09 | research-only | viewed (free parts) | https://www.mhymy.com/dasl/11467.html (same pattern). 绮春园, 曲院风荷 |
| S156 | 圆明园藻园遗址考古发掘报告, mhymy | after 1994 | research-only | viewed (free part) | https://www.mhymy.com/dasl/11828.html. 藻园 |
| S157 | Attiret, letter of 1 Nov 1743, Spence transl. 1752, Bard College transcription | 1743 | public domain | viewed | https://faculty.bard.edu/~louis/gardens/attiretaccount.html. hills "from 20 to 60 Foot high" |
| S158 | Hawker et al., FABDEM, Environ. Res. Lett. 2022; MERIT-Urban Beijing, Bristol | 2022 | CC BY-NC-SA 4.0 (as stated on the catalogue page, not on Bristol's); Non-Commercial Government Licence | found | https://gee-community-catalog.org/projects/fabdem/ ; https://data.bris.ac.uk/data/dataset/bc11e55dfe41088aff9dfec1d888ef2b. better DEM options |
| S159 | Copernicus DEM collection page; Product Handbook i5.0 (downloaded to scratch, unread: no PDF tool) | 2024 | free, source notice | viewed (page) | https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM. accuracy, datum |

## Round 3: Qing and Republican texts

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S200 | 世宗憲皇帝御製文集 (胤禛), WYG Siku text, Kanripo KR4f0002; includes 雍邸集 and 四宜堂集 poems | 1730s (printed under Qianlong) | public domain text; Kanripo transcription | downloaded | https://github.com/kanripo/KR4f0002. full repo fetched to scratch |
| S201 | 御製詩集 (弘曆), 初集 to 餘集, WYG Siku text, Kanripo KR4f0005 | 1736-1799 | public domain text; Kanripo transcription | downloaded | https://github.com/kanripo/KR4f0005. 37,700 poem entries parsed. Locators are Kanripo file numbers (continuous), not the printed juan of each 集. |
| S202 | 吳振棫 養吉齋叢錄, 校點 text as held in the 殆知閣 corpus; only 卷一 to 卷十七 are in this copy, simplified characters | author active to 1860s; printed 1890s | public domain text | viewed | https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/%E5%8F%B2%E8%97%8F/%E5%BF%97%E5%AD%98%E8%AE%B0%E5%BD%95/%E5%85%BB%E5%90%89%E6%96%8B%E4%B8%9B%E5%BD%95.txt. also https://daizhige.org/史藏/志存记录/养吉斋丛录.html. 卷十八 (the garden chapter) is missing from it. Bracketed editor notes such as [一] are in the copy. |
| S203 | 王闓運 圓明園詞 with 徐樹鈞 序 (dated 同治十年立秋 1871), simplified copy posted on Douban group 王闿运; no 自注 in this copy; second copy of the poem on Sina blog 安立志 | 1871 | public domain text; the copies themselves carry no licence | viewed | https://www.douban.com/group/topic/46378693/. http://blog.sina.com.cn/s/blog_413d9e3f0100yluh.html agrees on the poem. Not checked against a printed edition. |
| S204 | 清史稿 卷二十 文宗本紀, zh.wikisource | 1927 | public domain text (Wikisource) | viewed | https://zh.wikisource.org/wiki/清史稿/卷20 |
| S205 | 昭槤 嘯亭雜錄 and 嘯亭續錄, zh.wikisource | early 19th c. | public domain text (Wikisource) | viewed | https://zh.wikisource.org/wiki/嘯亭雜錄. 雜錄 卷一 to 十 and 續錄 卷一 to 五 fetched and searched. |
| S206 | 張恩蔭 清代文人筆記之圓明園文詞校正, 清代皇家園林研究中心 (中國人民大學清史研究所), posted 2015-08-20 | 2015 | none stated: facts only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/wxda/263f0d184c2c4e73859f209f423b112b.htm. lists errors in 養吉齋叢錄 卷十八 and other notebooks |
| S207 | 清實錄 文宗實錄 (咸豐朝) | compiled 1860s, on 1850-61 | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/别史/清实录咸丰朝实录.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S208 | 清實錄 宣宗實錄 (道光朝) | compiled 1850s, on 1821-50 | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/别史/清实录道光朝实录.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S209 | 清實錄 穆宗實錄 (同治朝) | compiled later 19th c., on 1862-74 | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/别史/清实录同治朝实录.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S210 | 方濬師 蕉軒隨錄, with 玉明 侍游御園記 | late 19th c.; the 記 is on 1856 | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/志存记录/蕉轩随录.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S211 | 姚元之 竹葉亭雜記 | early 19th c. | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/志存记录/竹叶亭杂记.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S212 | 趙慎畛 榆巢雜識 | early 19th c. | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/志存记录/榆巢杂识.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S213 | 趙翼 檐曝雜記 | c. 1800, on the Qianlong years | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/志存记录/檐曝杂记.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S214 | 徐珂 清稗類鈔 | 1917 | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/子藏/类书/清稗类钞.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S215 | 枝巢子 清宮詞 with prose notes | Republic period | author and date to be checked: treated as research-only; summary only | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/诗藏/词集/清宫词.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |
| S216 | 陳康祺 郎潛紀聞初筆 | late 19th c. | public domain text; corpus copy carries no licence | viewed | https://github.com/garychowcmu/daizhigev20/blob/master/史藏/志存记录/郎潜纪闻初笔.txt. 殆知閣 corpus on GitHub (garychowcmu/daizhigev20), simplified characters, typed copy with some garbled marks; not checked against a printed edition |

## Round 3: Qichun Yuan

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S220 | 清代绮春园沿革辨析, 清代皇家园林研究中心 (中国人民大学清史研究所), author on page only 皇家园林, posted 2020-11-17 | 2020 | none stated: facts only (page: 感谢作者授权，转发请联系作者) | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/ylfj/00baad8cc3da4c6a901378da7919d9a8.htm. Quotes 嘉庆 绮春园记, 题含淳堂, 题清夏斋, 含辉楼远望; 内务府 repairs 1771-1795; 同治 rename edict 1873. Fetched copy palace_r3_tmp_qichun/iqh_qc.html.txt |
| S221 | 藏传佛教与圆明园正觉寺, 圆明园管理处文史科 staff, reprinted from 《圆明园研究》第5期 on the 清代皇家园林研究中心 site, posted 2021-05-25 | 2021 | none stated: facts only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/lswh/f8d06436b9d444f98d64cdd88753acef.htm. Name of the author is not on the page. Rests on 金勋 《成府村志》稿 (unpublished), 《圆明园》上海古籍 1991, 《圆明园百景图志》稿 |
| S222 | 圆明园买卖街钩沉, reprinted from 《圆明园研究》第14期 on the 清代皇家园林研究中心 site, posted 2021-05-18 | 2021 | none stated: facts only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/hwyj/4115411323ba4429a9ecc9ae5b2bc2e5.htm. Author not named on page. 同乐园 and 含经堂 streets, 铺面房 则例, 含经堂 excavation numbers |
| S223 | (清) 吳振棫 《養吉齋叢錄》, scanned string-bound copy in 6 volumes with 《養吉齋餘錄》 in 2, archive.org 02096504.cn to 02096511.cn; 卷十八 is in 02096508.cn (養吉齋叢錄(五)) | Qing | Qing text, public domain; scan on archive.org, no licence stated on the item metadata | viewed | https://archive.org/details/02096508.cn/page/n52. Read by eye from page images n51-n54; OCR on the item is unusable. Leaf number 四 read from the margin. Local pages in palace_r3_tmp_qichun/ia_img/. |
| S224 | 张宝章 《圆明三园与圆明五园》, 《圆明园研究》第32期, 圆明园遗址公园 site | 2015 post | none stated: facts only | viewed | https://www.yuanmingyuanpark.cn/ymyyj/yj032/201504/t20150420_693218.html. Fetched once to palace_r3_tmp_qichun/park_3y.html.txt; host later timed out |
| S225 | 徐珂 《清稗類鈔》 宮苑類, zh.wikisource | 1917 | public domain | viewed | https://zh.wikisource.org/wiki/清稗類鈔/005 |
| S226 | 《清史稿》 卷118 職官志五, zh.wikisource | 1928 | public domain | viewed | https://zh.wikisource.org/wiki/清史稿/卷118. 綺春園 staff: 七品 from 乾隆三十九年; 道光二年 暢春園 staff moved to 綺春園, 郎中 renamed; 咸豐十年 abolished |
| S227 | 圆明园遗址公园 site, 景点 pages for 绮春园, /cgll/zyjd/qcy/ (t20110105_231481 涵秋馆?, 231483, 231485 敷春堂, 231486 宫门) | 2011 posts | none stated: facts only | viewed | https://www.yuanmingyuanpark.cn/cgll/zyjd/qcy/201101/t20110105_231485.html. Only 231481 (涵秋馆) could be read; 231485, 231486 timed out, rows from them stay status snippet. Site footer forbids reuse. Text may come from 《圆明园百景图志》. |
| S228 | 任敏, 圆明园正觉寺复建开放：历经两劫 幸免于难, 北京日报 via 中新网, 2011-07-07 | 2011 | none stated: facts only, photos research-only | viewed | https://www.chinanews.com/cul/2011/07-07/3163991.shtml. Prints a picture captioned 史料中记载的正觉寺全景图, source not given |
| S229 | “时空记忆”——乾隆本人造像老照片首次发现暨圆明园365张老照片发布会, 圆明园遗址公园 news, 2021 | 2021 | none stated: research-only | viewed | https://www.yuanmingyuanpark.cn/xw/202102/t20210225_4454127.html. 文殊 photograph: given as 1920 and 1920年代 on the same page. Donated by 刘阳 as a digital file to the park archive |

## Round 3: Western witnesses and descriptions

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S240 | Garnet Wolseley, Narrative of the War with China in 1860, London: Longman, 1862 | 1862 | IA item carries no status field; published 1862, author d.1913: public domain by age | viewed | https://archive.org/details/narrativeofwarwi00wols. Ch. VIII and XI, pp.215-280: fullest description of gate, hall and burning. |
| S241 | Robert Swinhoe, Narrative of the North China Campaign of 1860, London: Smith, Elder, 1861 | 1861 | IA item carries no status field; published 1861, author d.1877: public domain by age | viewed | https://archive.org/details/narrativeofnorth00swin. pp.293-300 entry of 7 October; p.331 outhouse. |
| S242 | R. J. L. M'Ghee, How We Got to Pekin: A Narrative of the Campaign in China of 1860, London: Bentley, 1862 | 1862 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/howwegotintopek01ghegoog. Ch. XII pp.201-216 and pp.284-289. Spelling Ewen-ming-Ewen. |
| S243 | Hope Grant and Henry Knollys, Incidents in the China War of 1860, Edinburgh: Blackwood, 1875 | 1875 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/incidentsinchina00granrich. Grant's journal. |
| S244 | Henry Brougham Loch, Personal Narrative of Occurrences during Lord Elgin's Second Embassy to China, 1860, London: Murray, 1869 | 1869 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/personalnarrativ00lochrich. Ch. XV pp.268-274. Parts seem to describe 清漪园, not 圆明园. |
| S245 | Paul Varin, Expédition de Chine, Paris: Michel Lévy, 1862 | 1862 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/expditiondechin00paulgoog. pp.227-246. Fullest French account of the sequence of courts. |
| S246 | Comte d'Hérisson (Maurice d'Irisson), Journal d'un interprète en Chine, Paris: Ollendorff, 1886 | 1886 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/journalduninter00irigoog. Malone p.185 n.: most fascinating and least reliable account; Cordier doubts him. Use with care. |
| S247 | Armand Lucy, Souvenirs de voyage: lettres intimes sur la campagne de Chine en 1860, J. Barile, 1861 | 1861 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/souvenirsdevoya00lucygoog. Letters of October 1860. |
| S248 | Alphonse Favier, Péking: histoire et description, Péking: Imprimerie des Lazaristes au Pé-T'ang, 1897 | 1897 | IA item carries no status field; published 1897, author d.1905: public domain by age | viewed | https://archive.org/details/pkinghistoireetd00favi. pp.255-262 on 1860. Plates of the ruins (ruines côté sud, côté nord; façade principale du palais européen) are pre-1900 and may help the picture workers; not catalogued by me. |
| S249 | E. Bretschneider, Archaeological and Historical Researches of Peking and Its Environs, Trübner & Co., 1876 | 1876 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/archaeologicala00bretgoog. Searched: mentions the summer palaces only in passing, as a road and water source. Nothing per compound. |
| S250 | Stephen W. Bushell, Chinese Art, vol. II, London: H.M. Stationery Office, 1905 | 1905 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/chineseart02bush. Enamels with V&A numbers from the Summer Palace; glazed figures from temple walls. |
| S251 | John Barrow, Travels in China, London: Cadell and Davies, 1804 | 1804 | IA: Public Domain Mark 1.0 (Wellcome copy) | viewed | https://archive.org/details/b22012928. pp.105-125: lodging, hall of audience with dimensions. |
| S252 | A. E. van Braam Houckgeest, An Authentic Account of the Embassy of the Dutch East-India Company, vol. II, London: Phillips, 1798 | 1798 | IA item carries no status field; published 1798: public domain by age | viewed | https://archive.org/details/authenticaccount02vanb. Fetched; I quote it only through S02 pp.167-170, which gives the page refs. |
| S253 | D. F. Rennie, The British Arms in North China and Japan, London: Murray, 1864 | 1864 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/britisharmsinnor00rennrich. Peking diary 1861-62; a note on restoration orders. |
| S254 | George Allgood, China War 1860: Letters and Journal, London: Longmans, 1901 | 1901 | IA item carries no status field; author d.1907: public domain by age | viewed | https://archive.org/details/cu31924023143930. p.85 and journal entries. |
| S255 | Theodore Walrond (ed.), Letters and Journals of James, Eighth Earl of Elgin, London: Murray, 1872 | 1872 | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/lettersandjourn00stangoog. Fetched; pp.361-367 per S02 p.183, p.189. |
| S256 | Demetrius C. Boulger, The Life of Gordon, London: Unwin, [1911] edition | 1911 ed. | IA: NOT_IN_COPYRIGHT | viewed | https://archive.org/details/lifeofgordonmajo00bouluoft. Gordon's letter on p.46. |
| S257 | Lettres édifiantes et curieuses, nouvelle édition, Mémoires de la Chine, vol. XXIV, Paris: J. G. Merigot le jeune: notice on Father Benoist, written 1775 | 1780 per IA, 1781 per S02 p.139 | published c. 1780: public domain by age; the IA item carries no status field; IA title says Mémoires du levant, the scanned title page Mémoires de la Chine | viewed | https://archive.org/details/lettresdifiantes24jesu_0. pp.401 ff. per S02 p.139; I read pp.413-420. |
| S258 | [Louis-François] Delatour, Essais sur l'architecture des Chinois, sur leurs jardins, leurs principes de médecine, et leurs moeurs et usages, Paris: Clousier, 1803 | 1803 | IA rights field: Licence ouverte / Open licence Etalab (BIU Santé copy 40644) | viewed | https://archive.org/details/BIUSante_40644. pp.158-208: Bourgeois' letter of October 1786, notes on the twenty plates, six paintings of the garden. Also a PDF at numerabilis.u-paris.fr/ressources/pdf/medica/bibnum/40644/40644.pdf (not opened). |
| S259 | A. B. Freeman-Mitford, The Attaché at Peking, London: Macmillan, 1900 (letters of 1865) | 1900 | IA item carries no status field; author d.1916: public domain by age | viewed | https://archive.org/details/attachatpeking00rede. pp.111-115 are on 万寿山 by his own statement; not tied to our objects. |

## Round 3: Qing pictures

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S260 | 清高宗 Qianlong, 御製圓明園圖詠 2 卷 2 冊, 石印本, 天津石印書屋, 光緒13年 [1887]. National Library of China 地756.11/843, via 中華古籍資源庫; Commons files NLC403-312001107375-14035 (卷一, 95 pp) and -14034 (卷二, 70 pp) | 1887 | Commons: Public domain (scan of a PD original, Public Domain Mark 1.0) | downloaded | https://commons.wikimedia.org/wiki/File:NLC403-312001107375-14035_%E7%A6%A6%E5%88%B6%E5%9C%93%E6%98%8E%E5%9C%92%E5%9C%96%E8%A9%A0_%E5%8D%B7%E4%B8%80.pdf. Complete: 40 picture spreads, each with printed scene title, then preface, poem and commentary. Prefaces of Yongzheng and Qianlong in red. Some JPX streams are slightly damaged (black patch bottom right); the images decode. |
| S261 | Hong Kong Palace Museum, The Hong Kong Jockey Club Series: Yuan Ming Yuan: Art and Culture of an Imperial Garden-Palace, exhibition page, 2024 | 2024 | Copyright © Hong Kong Palace Museum; images © The Palace Museum. Research-only, link card | viewed | https://www.hkpm.org.hk/en/exhibition/the-hong-kong-jockey-club-series-yuan-ming-yuan-art-and-culture-of-an-imperial-garden-palace. Names the place shown in several court paintings; loans from The Palace Museum, Beijing. |
| S262 | Yuanming Yuan in Paintings, Asian Art Newspaper (review of the Hong Kong Palace Museum exhibition, until 12 August 2024) | 2024 | Research-only, summary only | viewed | https://asianartnewspaper.com/yuanming-yuan-in-paintings/. Author not recorded; ties Zhang Tingyan's scroll to the western part of 九洲清晏 and reports the debate on the Twelve Months. |
| S263 | The Garden of Perfect Brightness 1: The Yuanmingyuan as Imperial Paradise (1700-1860), MIT Visualizing Cultures, essay section Paradise on Earth |  | MIT Visualizing Cultures site terms, not checked on this page; treat as research-only; images belong to holders | viewed | https://visualizingcultures.mit.edu/garden_perfect_brightness/ymy1_essay02.html. Author not on the pages fetched. Says the Twelve Months are not literally set in the garden. |
| S264 | 劉盈秀 Lau Ying Shiu, 雍正十二月行樂圖研究, 碩士論文, 國立臺灣師範大學 美術學系, 2003, 指導教授 沈以正 | 2003 | Research-only | viewed | https://www.airitilibrary.com/Article/Detail/U0021-2603200719133932. Record and abstract only. Full text not seen: abstract says the location is examined by comparing texts and surviving imperial garden paintings. |
| S265 | Hand-drawn Map of the Yuanmingyuan Imperial Garden-Palace, 1920s, acquisitions page, P. Y. and Kinmay W. Tang Center for East Asian Art, Princeton |  | facts cited | viewed | https://tang.princeton.edu/art-acquisitions/unknown-artist-hand-drawn-map-yuanmingyuan-imperial-garden-palace. Gives 117.2 x 245 cm overall and acquired 2021; the museum gives each scroll 177 cm high and purchase 2022. |
| S266 | Illustrated London News, 27 April 1861, p.390, A portion of the Emperor of China's Summer Palace, near Pekin; record at Hong Kong Baptist University Library Art Collections, iln-070 | 1861 | HKBU page: © 2022. All Rights Reserved; research-only, link card | viewed | https://bcc.lib.hkbu.edu.hk/artcollection/iln-070/. Page number from MIT Visualizing Cultures. |
| S267 | British Museum 1938,0113.0.1, 凯宴成功诸将士于正大光明殿 (print, c. 1830), from 平定回疆得胜图 | c.1830 | not read on the holder's page | found | https://www.britishmuseum.org/collection/object/A_1938-0113-0-1. Search snippet only. |

## Round 3: photographs

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S280 | Slovenski etnografski muzej, Skuškova zbirka: album of 449 photographs of Peking bought by Ivan Skušek ml. in Peking (1914-1920), on the portal East Asian Collections in Slovenia (VAZ) | before 1920 | CC BY-SA 4.0 (holder page, each item) | downloaded | https://vazcollections.si/predmeti/fotografija-rusevine-paviljona-dashuifa-v-stari-poletni-palaci/. Found through the Europeana API (dataset 525). Items RF0929-RF0958 are the Old Summer Palace; RF0906-RF0928 are Yiheyuan. Photographer anonymous (Wikidata Q4233718 on the record). Album inventory captions are in German. |
| S281 | Wellcome Collection, John Thomson glass negatives and prints (1868-72), works dzt7nw9c, ecspz5j9 etc.; Beato print azx9ygmj | 1860-1872; prints 1981 | Public Domain Mark 1.0 on the images read through the API | viewed | https://wellcomecollection.org/works/ecspz5j9. Corrects the Thomson captions: his "Yuen Ming Yuen" terrace is Longevity Hill, Qingyi Yuan. |
| S282 | Canadian Centre for Architecture, Felice Beato, view of the Belvedere of the God of Literature, Garden of the Clear Ripples, PH1986:0132 | 1860 | not read | viewed | https://www.cca.qc.ca/en/search/details/collection/object/362660. States that the published "Yuan Ming Yuan" title is inaccurate; the garden shown is Qingyi Yuan. |
| S283 | Duke University, exhibit item from 滿蒙印画輯 Manmō inga shū, "Ruins of old Summer Palace 圆明园废墟" | 1927 | Rights field names only "Rubenstein Rare Book & Manuscript Library, Duke University" | viewed | https://exhibits.library.duke.edu/exhibits/show/easia/item/11911. Exhibit page opens; repository.duke.edu is behind a bot check. |
| S284 | Osvald Sirén, The Imperial Palaces of Peking, 3 vols, G. van Oest, 1926: 274 collotype plates; Yuanmingyuan plates about 205-216 per the Östasiatiska records | 1926 | book; printed captions not read | to-request | https://www.bonhams.com/auction/30893/lot/69/siren-osvald-the-imperial-palaces-of-peking-3-vol-paris-and-brussels-g-van-oest-1926. No online copy found in one search. The printed captions would settle several ties below. |

## Round 3: Yangshi Lei

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S310 | 梦回圆明园 mhymy.com, 档案史料 > 样式雷图档 /dasl/ysltd/: per-drawing records (图名, 图幅, 款式, 图纸性质, 绘制年代, 收藏机构, 排架编码) with a description, for drawings held by NLC 国家图书馆善本部, 故宫博物院图书馆, 清华大学建筑学院 | 2020s | text: CC BY-NC-SA 4.0 per page footer, so research-only under project rules; images belong to holders; part of each record behind a ¥1 payment or WeChat mini-program | viewed | https://www.mhymy.com/dasl/ysltd. Live pages drop this server's connection (robots.txt answers). Read: 2 Wayback copies (5109, 2455), other records only through search-engine extracts, marked status snippet. Catalogue fields not checked against holders' own catalogues. |
| S311 | 白鸿叶, 《国家图书馆藏圆明园样式雷图档述略》, 《北京科技大学学报(社会科学版)》 2016 no.5, pp.37-41 | 2016 | research-only | found | . Only known from reference lists; the paper dedicated to this topic, text not reached. |
| S312 | 《圆明园戏场探微》, on 梦回圆明园; author not seen | n.d. | research-only; site text CC BY-NC-SA | found | https://www.mhymy.com/xsjl/9991.html. Read through search extracts only. Theatres, cites NLC Yangshi Lei sheets. |
| S313 | 《再现·圆明园——九洲清晏（中）》, on 梦回圆明园; author not seen | n.d. | research-only | found | https://www.mhymy.com/xsjl/qklw/9484.html. Search extract only. |
| S314 | 《圆明园正觉寺建筑研究》, on 梦回圆明园 | n.d. | research-only | found | https://www.mhymy.com/xsjl/10588.html. Search extract only. Remains, drawings and 成府村志 for 正觉寺. |
| S315 | 《圆明园正觉寺天王殿考古发掘报告》, on 梦回圆明园 | n.d. | research-only | found | https://www.mhymy.com/dasl/11258.html. Title and search extract only. |
| S316 | 《圆明园长春园宫门区遗址发掘报告》, on 梦回圆明园 | excavated 2001-04 | research-only | found | https://www.mhymy.com/xsjl/9970.html. Search extract only. |
| S317 | 《圆明园 1707-1850 修建过程》, chronology on 梦回圆明园, citing 活计档, 奏销档, 《圆明园估单文件》 | n.d. | research-only | found | https://www.mhymy.com/dasl/2278.html. Search extract only. |
| S318 | 《中国人民大学图书馆藏样式雷建筑图档述略》, 《故宫博物院院刊》 2022 no.7 | 2022 | research-only | viewed | https://www.dpm.org.cn/journal/257905.html. PDF downloaded to tmp; its text layer is unreadable (no Unicode map), 圆明园 not found by machine. Holders survey. |
| S319 | 何蓓洁, 《清代样式雷世家及其建筑图档研究90年》, jgcm.ac.cn | 2020 | research-only | viewed | https://www.jgcm.ac.cn/jah/article/doi/10.12329/20969368.2020.01014. Abstract only. |
| S320 | Palace Museum journal PDF with fig. 7 of pre-1860 plans at 故宫博物院 (安澜园, 方壶胜境, 舍卫城, 同乐园 and others) repaired under Lei Jiaxi, Lei Jiarui, Lei Jingxiu; author and title not read | n.d. | research-only | blocked | https://www.dpm.org.cn/Uploads/File/pdf/33/1d/3f/331d3fd4dc1f9a8921e6b41614ab5374.pdf. PDF flags forbid text extraction, so not extracted; read by a person it should list Palace Museum sheets for these compounds. |
| S321 | 故宫博物院 site articles 《圆明园与样式雷》 and 《样式雷的“天地一家春”》 in a password-prompting PDF viewer | n.d. | research-only | blocked | https://www.dpm.org.cn/building/talk/250827.html ; http://www.dpm.org.cn/explode/others/210399.html. Viewer asks for a password from this server; not attempted. |
| S322 | National Palace Museum Taipei, online exhibition on the Lei family, mentions drawings at National Taiwan University Library | 2023 | Copyright National Palace Museum, all rights reserved | viewed | https://theme.npm.edu.tw/exh112/QingArchitectural/en/page-3.html. No Yuanming Yuan sheet named on the page read. |
| S323 | 梦回圆明园 forum thread 文源阁样式雷草图 quoting an NLC note | n.d. | research-only | found | https://bbs.mhymy.com/forum.php?mod=viewthread&tid=2358. Search extract only. |
| S324 | 《样式雷图上的春熙院》, on 梦回圆明园 | n.d. | research-only | found | https://www.mhymy.com/xsjl/6240.html. Search extract only. |
| S325 | 《圆明园研究的相关文献资料大全》, bibliography on 梦回圆明园 | n.d. | research-only | found | https://www.mhymy.com/xsjl/2272.html. Lists 《国立北平图书馆馆刊》 圆明园专号, 张恩荫 etc. |
| S326 | 澎湃新闻 report on an exhibition of Palace Museum 烫样, including 九洲清晏殿 and 万方安和殿 | n.d. | research-only | found | https://m.thepaper.cn/detail/31695388. Search extract only; the only source found for the Tongzhi date of these two models. |
| S327 | 中国第五项世界记忆遗产“样式雷”首现国图, report on the National Library exhibition, on ihchina.cn | 2007 | research-only | viewed | https://www.ihchina.cn/news_other_details/17719.html. Names 圆明园内文源阁图样, 圆明园来水河道全图, and the Palace Museum's 万方安和 and 廓然大公 烫样. |
| S328 | Report on the National Museum's conservation of the 同乐园 model, reprinted on 梦回圆明园; also xinhuanet | 2023 | research-only | found | https://www.mhymy.com/xwzx/ssrd/13512.html ; https://www.xinhuanet.com/shuhua/20230517/853c8d5fecc64755ade73189babb5a70/c.html. Search extract only. |
| S329 | 8代人修了半个北京城，“样式雷”给今天留下什么, 中国青年报 via 中新网 | 2024 | research-only | viewed | https://www.chinanews.com/cul/2024/04-26/10206346.shtml. NLC catalogued all Yangshi Lei items 2007-09, 14,396 records; digital resource database due complete by end 2024. |

## Round 3: archaeology and scholarship

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S330 | 上海《文汇报》记者李扬, “公众考古”圆明园 (文汇报 汇生活 page) | 2017 | none stated, facts only | viewed | https://dream-video.whb.cn/zhuzhan/wan/20170507/91188.html. public archaeology report; page body mostly a lead |
| S331 | 新京报 倪伟 via 中新网, 北京 2017 年考古 news with 如园 and 紫碧山房 passages | 2017 | none stated, facts only | viewed | https://www.chinanews.com.cn/sh/2017/12-15/8400775.shtml. same page as the second half of S132; cited for 如园 finds |
| S332 | 北京日报 客户端, 仅存于图纸上的圆明园舍卫城到底什么样, full body re-read | 2020 | none stated, facts only | viewed | https://view.inews.qq.com/k/20200108A0M0Q400. duplicate of S46/S107; kept only as a pointer, use S46 for citations |
| S333 | 《北京旅游网》 记者稿, 圆明园：多维活态重现 | n.d. | none stated, facts only | viewed | https://www.visitbeijing.com.cn/article/49Nly85Lvzb. 含经堂 2001-03 approval; 地天母 bronze; 2014 象首; 郭黛姮 team 108 scenes digitised |
| S334 | 央视新闻 via 凤凰网, 圆明园启动大规模修复文物项目 瓷器碎片高达10万片 | 2019 | none stated, facts only | viewed | https://news.ifeng.com/c/7ma60W4GZjB. 修复1860 project; 坦坦荡荡 绣墩; 思永斋 tiles |
| S335 | 宋广波, 圆明园漫记, 爱思想 | n.d. | none stated, lead only | viewed | https://www.aisixiang.com/data/141347.html. walker's essay, says 万方安和 and 金鱼池 bases were dug in 2004; lead only |
| S336 | 中国社会科学网, “圆明・交融”成果展揭秘圆明园之美 | 2024 | none stated, facts only | viewed | https://www.cssn.cn/ysx/ysx_ysqs/202412/t20241226_5827292.shtml. exhibition of the 圆明园研究高校联盟; 如园, 海晏堂, 澹泊宁静 sections |
| S337 | 中国人民大学清史研究所 清代皇家园林研究中心, 学术综览 (xstl, lswh, jzys, ylfj, wxda, hwyj): reposted articles, 397 listed, 121 fetched | 2013-2024 posts | none stated, research-only: own-words summaries | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/jzys/index.htm. each row links its own article; 作者 field usually only 皇家园林, so the real author is often unnamed |
| S338 | 圆明园研究 journal, 圆明园遗址公园 site xs/ktsb (99 issues listed) and xs/yjbg (17 reports) | to 2026 | site reserves rights: own-words summaries | viewed | https://www.yuanmingyuanpark.cn/xs/ktsb/. 15 pages fetched before the host stopped answering; rest listed only, see notes file for the URLs |
| S339 | Blog 北平旧梦, 老北京的记忆 (64), (78), (79), (90), posts on 绮春园 quoting 《圆明园百景图志》 | 2012-2016 | research-only | viewed | https://blog.sina.com.cn/s/articlelist_2289311245_0_1.html. 7 圆明园 posts on the blog's 3 list pages: 64, 78, 79, 81, 90, 125, 133; no others listed |
| S340 | 梦回圆明园 mhymy.com, 景区介绍 scene pages (圆明园事务总管), first page of cards read in an earlier fetch, others seen through a search index | 2020-22 posts | research-only; site says CC BY-NC-SA on some, unclear | found | https://www.mhymy.com/ymss/jqjs/ymy. host refuses TLS from this server today; rows from search-index text are status snippet |
| S341 | 贺艳 (清华大学), 《再现·圆明园》 series, 紫禁城 2011-2012, reposted at mhymy qklw | 2011-12 | research-only | found | https://www.mhymy.com/xsjl/qklw/9456.html. 正大光明 9456, 勤政亲贤 9476, 九洲清晏 (中) 9484, (下) 9486, 上下天光 9505, 杏花春馆 9548, 坦坦荡荡 9571. 紫禁城 itself is the primary; to-request |
| S342 | Tsinghua news set on 数字圆明园: 2010 China Daily, 《“再造”一个圆明园》, 《虚拟现实带您走进“万园之园”》, 人文清华 2020 | 2010-2020 | research-only | viewed | https://www.tsinghua.edu.cn/info/1182/39662.htm. re-relic.com answers with a Cloudflare challenge: not tried further |
| S343 | Geremie R. Barmé, The Garden of Perfect Brightness, A Life in Ruins, East Asian History 11 (1996), 111-158 | 1996 | research-only | found | https://faculty.bard.edu/~louis/gardens/bibliochinaalpha.htm. citation via Bard bibliography and MIT reading list |
| S344 | Young-tsu Wong 汪荣祖, A Paradise Lost: The Imperial Garden Yuanming Yuan, University of Hawai'i Press 2001; Springer China Academic Library 2016 | 2001 | research-only | found | https://www.degruyterbrill.com/document/doi/10.1515/9780824863876/html. to-request |
| S345 | Erik Ringmar, Liberal Barbarism: The European Destruction of the Palace of the Emperor of China, Palgrave Macmillan 2013 | 2013 | research-only | found | https://link.springer.com/978-1-137-26890-7. link is bot-checked here; book exists per several catalogues |
| S346 | Che Bing Chiu 邱治平, Yuanming yuan: le jardin de la clarté parfaite, Besançon 2000; Droiture et Clarté, Studies in the History of Gardens 19 (1999), 364-375; Un grand jardin impérial chinois, Extrême-Orient Extrême-Occident 22 (2000), 17-50 | 1999-2000 | research-only | found | https://faculty.bard.edu/~louis/gardens/bibliochinaalpha.htm. to-request. Droiture et Clarté is on 正大光明 |
| S347 | Greg M. Thomas, The Looting of Yuanming and the Translation of Chinese Art in Europe, Nineteenth-Century Art Worldwide 7(2), 2008 | 2008 | research-only | found | . the brief's Versailles article by Thomas was not found; this citation was seen in search results only, no article URL verified |
| S348 | 贾贯峰 (圆明园博物馆), 圆明三园进出水口探析, 中国园林 2024, 40(4): 129-133, DOI 10.19775/j.cla.2024.04.0129 | 2024 | research-only | found | https://search.napstic.cn/literature/periodical/010zgyl202404020. record read directly; the abstract was seen through search text |
| S349 | 圆明园水利文物遗迹研究, mhymy xsjl 6277 | n.d. | research-only | found | https://www.mhymy.com/xsjl/6277.html. search-index text only |
| S350 | 圆明园 1707-1850 修建过程, mhymy dasl 2278 (chronology) | n.d. | research-only | found | https://www.mhymy.com/dasl/2278.html. search-index text only |
| S351 | 京报网, 3D技术复现“万园之园” | 2025 | none stated, facts only | viewed | https://news.bjd.com.cn/2025/05/21/11171051.shtml. 北京大学 考古文博学院 stone scanning, over 10 sites dug since the 1990s |
| S352 | Louise Tythacott, The 'Summer Palace' Diaspora, SOAS research project | n.d. | research-only | viewed | https://www.soas.ac.uk/research/summer-palace-diaspora. objects from the garden in British and French museums |
| S353 | Bibliography on Gardens in China: Sources in Western Languages, Bard College faculty page | n.d. | link only | viewed | https://faculty.bard.edu/~louis/gardens/bibliochinaalpha.htm. 23 entries on the garden, for finding western works |
| S354 | Key issues for AR-based digital reconstruction of Yuanmingyuan Garden, Beijing Institute of Technology research record | n.d. | research-only | viewed | https://pure.bit.edu.cn/en/publications/key-issues-for-ar-based-digital-reconstruction-of-yuanmingyuan-ga. abstract |
| S355 | Yan Chen, Constructive analysis and digital 3D reconstruction of the Yuanmingyuan Ruins: Wanfanganhe Pavilion (China), Virtual Archaeology Review, 2022 | 2022 | to check on the journal page | found | https://polipapers.upv.es/index.php/var/article/view/16523. timed out; RiuNet mirror bot-checks. Earlier worker also failed (dl_var_wf empty) |
| S356 | Blog yaffin, 【圆明园】系列 02, 08, 09, 11, 13, 14, 15; 系列06 reposted by 双飞燕; site status table of about 2011 | c. 2011 | research-only, lead only | viewed | http://blog.sina.com.cn/s/articlelist_1711195051_0_1.html. unverified compilations. 系列 03-05, 07, 10, 12 not on the list pages |
| S357 | 端木泓, 圆明园新证一万方安和考 (abstract page of a PDF |  | research-only | viewed | . palace_r1_typo/dl_dumu_wf; journal and URL not recorded, so unknown here |

## Round 3: the park's compilations

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S360 | 圆明园管理处 (attachment on the park's site), 圆明园百景史事分景汇编: dated records and imperial poems scene by scene, compiled from the Veritable Records and the emperors' collected poems, 309 pp. PDF | PDF made 2016-09-05; posted 2020-07-30 | research-only for the compilation and its captions; the Qing poems and records it reprints are public domain | downloaded | https://www.yuanmingyuanpark.cn/xs/yjbg/202007/P020200730387572832602.pdf. Landing page https://www.yuanmingyuanpark.cn/xs/yjbg/202007/t20200730_4416788.html . Local copy /opt/data/cache/scratch/palace_r3_tmp_park/pdf/baijing.pdf (into research/raw if kept, never commit). Text extracted with pypdf; all 1,800 items parsed in palace_r3_tmp_park/pdf/sections.json. Poems are the compiler's transcription, not collated with 御制诗集; the year is the compiler's. Compiler's caption slips exist, e.g. 慎德堂 items 4-7 say 道光帝 under 咸丰 years. |
| S361 | 何瑜 (cover name; 编著 as on the volumes), 圆明园五朝御制诗文集注, vols 2-4 of the first four volumes, PDF on the park's site: the imperial poems and essays of five reigns by scene, with editor's intro per scene and notes; text from 故宫珍本丛刊 (海南出版社 2000) | posted 2020-08-03 | research-only for editors' intros and notes; the Qing poems and essays are public domain | downloaded | https://www.yuanmingyuanpark.cn/xs/yjbg/202008/t20200803_4417144.html. v4 https://www.yuanmingyuanpark.cn/xs/yjbg/202008/P020200803382796786124.pdf ; v3 .../P020200803382569071850.pdf ; v2 .../P020200803382343267004.pdf ; v1 .../P020200803381209502723.pdf timed out, retry. Local /opt/data/cache/scratch/palace_r3_tmp_park/pdf_jz/. Answers S58: holds 绮春园三十景 (嘉庆十年, v4 pp.175-184) and 绮春园记. Plan 10-12 volumes; four released. Refs like (3-120) are the edition's vol-page of the source collection. |
| S362 | 周秋彤 (北京大学考古文博学院), 如园延清堂建筑复原研究, 圆明园 site, 研究报告 | 2024-03-28 | research-only | viewed | https://www.yuanmingyuanpark.cn/xs/yjbg/202403/t20240328_4646527.html. Full article on the page, 24 images, none kept. Uses the 2016-17 dig and 样式雷 drawings. |

## Round 3: other

| ID | Source | Year | Reuse | Status | Link / note |
|---|---|---|---|---|---|
| S380 | 绮春园是圆明园三园中最小的，也是现在修复最好的, 传统文化天天见, 腾讯新闻, 2020-04-07 | 2020 | none stated: lead only, research-only | viewed | https://news.qq.com/rain/a/20200407A0NJ1F00. Fetched copy palace_r3_tmp_qichun/qq_qc.html. Only source on disk naming 集禧堂. |
| S381 | 北平旧梦, 老北京的记忆（133）：圆明园别有洞天遗址, sina blog 2018-02-22, draws on 《圆明园百景图志》 like S111 | 2018 | research-only, lead | viewed | https://blog.sina.com.cn/s/blog_88741e0d0102xbym.html. Hall by hall text with 咸丰 匾额略节 list for 别有洞天. |
| S382 | zh.wikipedia, 奕訢 | fetched 2026-10-31 | CC BY-SA: lead only | viewed | https://zh.wikipedia.org/wiki/奕訢. infobox: 號 太岳、樂道堂主人 |
