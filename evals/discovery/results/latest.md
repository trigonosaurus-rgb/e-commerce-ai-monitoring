# Discovery agent — cross-market eval

10 cases · cases with ≥1 correct match: 8/10 · proposals: 26 correct, 0 wrong, 0 unlabeled · precision 100%
Tavily credits spent this run: 56 · LLM $0.035 · 9 min

| Case | Market | Read as | Proposed | ✓ | ✗ | ? | Credits | LLM $ |
|---|---|---|---|---|---|---|---|---|
| us-lodge-skillet | US | Lodge 10.25" Cast Iron Skillet - L8SK3 · 24.90 USD | 3 | 3 | 0 | 0 | 2 | 0.003 |
| us-hoka-clifton | US | HOKA Clifton 10 · 104.88 USD | 5 | 5 | 0 | 0 | 2 | 0.002 |
| us-fellow-kettle | US | Fellow Stagg EKG · 165.00 USD | 4 | 4 | 0 | 0 | 5 | 0.002 |
| uk-ninja-airfryer | UK | Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · 99.00 GBP | 3 | 3 | 0 | 0 | 11 | 0.008 |
| uk-helen-round-towel | UK | Winter Fox Linen Tea Towel · 18.00 GBP | 2 | 2 | 0 | 0 | 2 | 0.001 |
| uk-lakeland-tin | UK | Lakeland Brownie Traybake Tin · 9.99 GBP | 0 | 0 | 0 | 0 | 10 | 0.003 |
| fr-seb-pressure-cooker | France | Autocuiseur SEB ClipsoMinut Gourmande 7.5L · 126.10 EUR | 4 | 4 | 0 | 0 | 2 | 0.003 |
| fr-ordinary-serum | France | THE ORDINARY Niacinamide 10% + Zinc 1% · 5.69 EUR | 3 | 3 | 0 | 0 | 8 | 0.004 |
| nl-philips-airfryer | Netherlands | Philips Airfryer L HD9252/70 · 99.00 EUR | 0 | 0 | 0 | 0 | 8 | 0.004 |
| pl-logitech-mouse | Poland | Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · 319.99 P | 2 | 2 | 0 | 0 | 6 | 0.005 |

## us-lodge-skillet — Kitchen, branded, UPC on the page

- Page: https://www.abt.com/Lodge-10.25-Cast-Iron-Skillet-L8SK3/p/81755.html
- Read: Lodge 10.25" Cast Iron Skillet - L8SK3 · brand Lodge · GTIN 0075536300801 · MPN L8SK3 · 24.90 USD · market united states
- Status: completed
- Attempts: 1 · queries: Lodge L8SK3 10.25 cast iron skillet; Lodge 10.25 inch seasoned cast iron skillet L8SK3; 0075536300801
- Market research: 10.25 inch cast iron skillet buy
- Stores searched for the product: whisknyc.com, mastgeneralstore.com, lehmans.com, larderandvine.com, homedepot.com, costco.com, shop.metropolitan-market.com, target.com, shop.harmonsgrocery.com, lodgecastiron.com, kohls.com, macys.com, surlatable.com, williams-sonoma.com, acehardware.com
- Sites skipped: lodgecookware.com.au (other_market: A shop for another country (AU).); amazon.com (marketplace: Marketplace listings include Lodge cookware.); youtube.com (media_or_review: Video review platform, not a product shop.); fieldcompany.com (brand_shop: Own-brand cast iron shop; does not sell Lodge.); logotech.com (other_market: Promotional products and branded gift sets, not a cookware retailer.); walmart.com (marketplace: Marketplace offers the Lodge skillet.); reddit.com (media_or_review: Discussion forum, not a product shop.)
- Screened 20 pages, kept 7
- ✓ **rainsofojai.com** 46.00 USD (conf. 0.99) — Same EAN/GTIN code on both pages. <https://rainsofojai.com/10-25-cast-iron-skillet-l8sk3-lodge>
- ✓ **shop.harmonsgrocery.com** 39.99 USD (conf. 0.94) — Both listings identify Lodge’s 10.25-inch cast-iron skillet, with no variant or edition difference indicated. <https://shop.harmonsgrocery.com/store/harmons/products/169296-lodge-cast-iron-10-25-cast-iron-skillet-1-ea>
- ✓ **bar-b-que.com** 29.99 USD (conf. 0.9) — Same manufacturer part number (L8SK3). <https://www.bar-b-que.com/lodge-l8sk3-logic-cast-iron-skillet-10-31-in>
- rejected at verify: homedepot.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: acehardware.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: target.com — No price found on the page.
- rejected at verify: katom.com — This doesn't look like a single product page.

## us-hoka-clifton — Running shoes: sizes and colourways, no codes on the page

- Page: https://www.runningwarehouse.com/HOKA_Clifton_10/descpage-H10CM15.html
- Read: HOKA Clifton 10 · brand HOKA · GTIN None · MPN None · 104.88 USD · market united states
- Status: completed
- Attempts: 1 · queries: HOKA Clifton 10 men's shoes; HOKA Clifton 10 Raw Linen Stone men's
- Market research: men's running shoes shop
- Stores searched for the product: shoecarnival.com, dickssportinggoods.com, zappos.com, marathonsports.com, steepandcheap.com, fit2run.com, therunhouse.com, finishline.com, roadrunnersports.com, fleetfeet.com, rei.com, backcountry.com, nordstrom.com, holabirdsports.com
- Sites skipped: newbalance.com (brand_shop: New Balance’s own-brand store.); adidas.com (brand_shop: Adidas’s own-brand store.); asics.com (brand_shop: ASICS’s own-brand store.); nike.com (brand_shop: Nike’s own-brand store.); brooksrunning.com (brand_shop: Brooks’s own-brand store.); on.com (brand_shop: On’s own-brand store.); saucony.com (brand_shop: Saucony’s own-brand store.); altrarunning.com (brand_shop: Altra’s own-brand store.); yelp.com (not_a_shop: Business listings and reviews, not a retailer.)
- Screened 25 pages, kept 9
- ✓ **therunhouse.com** 103.95 USD (conf. 0.99) — Both listings are HOKA Clifton 10 men's shoes in Raw Linen/Stone; no model or variant difference is indicated. <https://therunhouse.com/products/men-s-clifton-10-raw-linen-stone>
- ✓ **shop.rrrc.run** 124.00 USD (conf. 0.97) — Both listings are HOKA Clifton 10 men's shoes in Raw Linen/Stone. <https://shop.rrrc.run/product/5404456/hoka/mens-clifton-10>
- ✓ **zappos.com** 108.50 USD (conf. 0.96) — Both listings are the men's HOKA Clifton 10; the Zappos listing does not specify a color variant. <https://www.zappos.com/p/mens-hoka-clifton-10/product/9984276>
- ✓ **roadrunnersports.com** 109.95 USD (conf. 0.94) — Both listings are men's HOKA Clifton 10 running shoes; the second listing does not specify a color, so no variant conflict is evident. <https://www.roadrunnersports.com/product/47718/mens-hoka-clifton-10>
- ✓ **fleetfeet.com** 116.25 USD (conf. 0.93) — Both listings are HOKA Clifton 10 men's shoes; the second listing does not specify a color variant, so no conflict is indicated. <https://www.fleetfeet.com/products/mens-hoka-clifton-10>
- rejected at verify: hoka.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: footlocker.com — Page not found (HTTP 404) — the product may have been removed.
- rejected at verify: rei.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.

## us-fellow-kettle — Specialty coffee shop (Shopify), shop name in the brand field

- Page: https://us.lacabra.com/products/fellow-stagg-ekg-2
- Read: Fellow Stagg EKG · brand None · GTIN None · MPN None · 165.00 USD · market united states
- Status: completed
- Attempts: 1 · queries: Fellow Stagg EKG kettle; Fellow Stagg EKG electric kettle buy; Fellow Stagg EKG kettle for sale
- Market research: electric gooseneck kettle shop
- Stores searched for the product: target.com, bonescoffee.com, artizancoffee.com, macys.com, fellowproducts.com, couleecoffee.com, wonderstate.com, williams-sonoma.com, crateandbarrel.com, surlatable.com, seattlecoffeegear.com, prima-coffee.com, clivecoffee.com, brewmethods.com, coffeeproject.com
- Sites skipped: walmart.com (marketplace: Marketplace and retailer for home appliances.); amazon.com (marketplace: Marketplace with many kettle sellers.); cocinare.com (brand_shop: Cocinare’s own kettle brand, not Fellow.); thewaytocoffee.com (media_or_review: Coffee gear review and guide site.); shop.greatergoods.com (brand_shop: Greater Goods’ own kettle brand, not Fellow.); hazelquinn.com (brand_shop: Own-brand kettle shop, not Fellow.); coffeechronicler.com (media_or_review: Coffee gear review and advice site.); smilingcoffeesnob.com (media_or_review: Coffee gear blog and review site.); reddit.com (not_a_
- Screened 14 pages, kept 5
- ✓ **formandfunctioncoffee.com** 169.95 USD (conf. 0.94) — Both listings identify the Fellow Stagg EKG kettle, with no conflicting model or variant details. <https://formandfunctioncoffee.com/shop/fellow-stagg-ekg-electric-kettle/>
- ✓ **costco.com** 129.99 USD (conf. 0.93) — Both listings identify the Fellow Stagg EKG electric kettle, with no differing model or variant specified. <https://www.costco.com/p/-/fellow-stagg-ekg-electric-kettle/4000397413>
- ✓ **palomacoffeebakery.com** 165.00 USD (conf. 0.93) — Both listings identify the Fellow Stagg EKG electric kettle, with no conflicting model or variant details. <https://palomacoffeebakery.com/products/fellow-stagg-ekg-electric-kettle>
- ✓ **domacoffee.com** 169.95 USD (conf. 0.91) — Both listings are for the Fellow EKG kettle, with no differing model or variant indicated. <https://www.domacoffee.com/products/fellow-ekg-kettle>
- rejected at verify: fellowproducts.com — The other listing’s page title includes “Pro” and “Pro Studio,” edition markers absent from your listing.

## uk-ninja-airfryer — Small appliance, shop SKU instead of the maker's model code

- Page: https://www.euronics.co.uk/catalogue/small-appliances/small-cooking-appliances/air-fryers/ninja-af100uk-38l-air-fryer-and-dehydrator-grey/p/NINAF100UK
- Read: Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · brand Ninja · GTIN None · MPN NINAF100UK · 99.00 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Ninja AF100UK 3.8L Air Fryer and Dehydrator; Ninja AF100UK air fryer grey buy UK; Ninja AF100UK grey 3.8L air fryer buy UK; NINAF100UK Ninja air fryer retailer; Ninja AF100UK air fryer and dehydrator price UK
- Market research: air fryer buy UK; air fryer shop UK
- Stores searched for the product: johnlewis.com, currys.co.uk, argos.co.uk, very.co.uk, ao.com, robertdyas.co.uk, lakeland.co.uk, ninjakitchen.co.uk, direct.asda.com, sharkninja.com, appliancesdirect.co.uk, hughes.co.uk, sonicdirect.co.uk, hartsstore.com, donaghybros.co.uk, electricaldiscountuk.co.uk, qvcuk.com, littlewoods.com
- Sites skipped: reddit.com (not_a_shop: Discussion forum, not a retailer.); which.co.uk (media_or_review: Product testing and buying advice.); goodhousekeeping.com (media_or_review: Publishes air fryer reviews.); youtube.com (unknown: No verdict from the model.); cosori.co.uk (brand_shop: COSORI's own shop sells its own brand.); instantpot.co.uk (brand_shop: Instant Pot's own shop sells its own brand.); bbcgoodfood.com (media_or_review: Food publication with product reviews.); saga.co.uk (media_or_review: Editorial buying advice, not an air fryer shop.); mumsnet.com (media_or_review: Parenting site with produ
- Screened 34 pages, kept 12
- ✓ **thewashhouse.com** 99.00 GBP (conf. 0.99) — The model AF100UK, 3.8L capacity, and grey color match exactly. <https://www.thewashhouse.com/ninja/ninja-af100uk-grey-200112629.html>
- ✓ **combensapps.co.uk** 99.99 GBP (conf. 0.99) — Both listings identify the Ninja AF100UK 3.8L Air Fryer and Dehydrator, with no variant differences indicated. <https://www.combensapps.co.uk/ninja-af100uk-grey-100002708.html>
- ✓ **littlewoods.com** 134.99 GBP (conf. 0.94) — Both listings identify the Ninja AF100UK 3.8L single-basket air fryer; the differing MPN appears to be a retailer or catalog code. <https://www.littlewoods.com/ninja-air-fryer-af100uk/1600348148.prd?bvstate=pg%3A31%2Fct%3Ar>
- rejected at verify: amazon.co.uk — No price found on the page.
- rejected at verify: robertdyas.co.uk — No price found on the page.
- rejected at verify: johnlewis.com — No price found on the page.
- rejected at verify: appliancesdirect.co.uk — Page not found (HTTP 410) — the product may have been removed.
- rejected at verify: qvcuk.com — This doesn't look like a single product page.
- rejected at verify: direct.asda.com — No price found on the page.
- rejected at verify: donaghybros.co.uk — No price found on the page.

## uk-helen-round-towel — Small designer brand without EAN, sold by gift shops

- Page: https://countrylivingshop.co.uk/products/winter-fox-linen-tea-towel
- Read: Winter Fox Linen Tea Towel · brand Helen Round · GTIN None · MPN None · 18.00 GBP · market united kingdom
- Status: completed
- Attempts: 1 · queries: Helen Round Winter Fox Linen Tea Towel; "Winter Fox" "Helen Round" tea towel; Helen Round linen tea towel
- Market research: linen tea towels buy UK
- Stores searched for the product: helenround.com, willowandstone.co.uk, home-landing.co.uk, countrysideart.co.uk, woodsfinelinens.com, johnlewis.com, fenwick.co.uk, amara.com, thelinenworks.co.uk, cuckooland.com, dotcomgiftshop.com, oliverbonas.com
- Sites skipped: ebay.co.uk (marketplace: Marketplace with many third-party sellers.); givans.co.uk (brand_shop: Own kitchen-linen range; not Helen Round.); pigletinbed.com (brand_shop: Own home-linen brand and range.); facebook.com (not_a_shop: Social platform, not a product shop.); linenme.com (brand_shop: Own linen brand and products.); ulsterweavers.com (brand_shop: Own tea-towel brand.); le-jacquard-francais.com (brand_shop: Own French kitchen-linen brand.); amazon.co.uk (marketplace: Marketplace with many third-party sellers.); fergusonsirishlinen.com (brand_shop: Own Irish-linen products.); breadtopia.c
- Screened 9 pages, kept 2
- ✓ **helenround.com** 18.00 GBP (conf. 0.98) — Both listings name the Winter Fox Linen Tea Towel, and no differing variant or condition is indicated. <https://www.helenround.com/products/winter-fox-collection-linen-tea-towel>
- ✓ **notonthehighstreet.com** 18.00 GBP (conf. 0.97) — Both listings identify the same Winter Fox Linen Tea Towel by Helen Round, with no differing variant or edition markers. <https://www.notonthehighstreet.com/helenround/product/winter-fox-linen-tea-towel>

## uk-lakeland-tin — Shop's own brand (negative control)

- Page: https://www.lakeland.co.uk/products/lakeland-brownie-traybake-tin
- Read: Lakeland Brownie Traybake Tin · brand Lakeland · GTIN None · MPN None · 9.99 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: "Lakeland Brownie Traybake Tin"; Lakeland Brownie Traybake Baking Tin buy; Lakeland brownie traybake tin retailer; Lakeland brownie traybake tin 23 x 33 cm buy UK; Lakeland brownie baking tin traybake stockist; "Lakeland Brownie Traybake" tin shop
- Market research: brownie traybake tin buy; brownie baking tin buy UK
- Stores searched for the product: dilektable.com, boroughkitchen.com, thebigkitchen.co.uk, pmecake.com, johnlewis.com, dunelm.com, robertdyas.co.uk, argos.co.uk, hobbycraft.co.uk, souschef.co.uk, nisbets.co.uk, buymeonce.co.uk, thecakedecoratingcompany.co.uk, sugarcraftshop.co.uk, infusions4chefs.co.uk, sugarandicecake.co.uk, japaneseknifecompany.com, bakerybits.co.uk, cakecraftworld.co.uk, cake-stuff.com, thecookskitchen.com, divertimenti.co.uk
- Sites skipped: olivemagazine.com (media_or_review: Food magazine and product reviews); procook.co.uk (brand_shop: ProCook’s own cookware brand shop); silverwoodbakewareusa.com (brand_shop: Silverwood brand shop serving the US); ebay.com (marketplace: Marketplace sellers can list Lakeland bakeware); silverwood-bakeware.com (brand_shop: Silverwood’s own bakeware shop); amazon.com (marketplace: Marketplace sellers can list products from other brands); etsy.com (marketplace: Marketplace sellers can list baking tins); facebook.com (not_a_shop: Social media post, not a shop); scientificallysweet.com (media_or_revi
- Screened 23 pages, kept 0

## fr-seb-pressure-cooker — Cookware, EAN, French-language shop

- Page: https://www.boulanger.com/ref/1230647
- Read: Autocuiseur SEB ClipsoMinut Gourmande 7.5L · brand SEB · GTIN 3045380402034 · MPN None · 126.10 EUR · market france
- Status: completed
- Attempts: 1 · queries: SEB ClipsoMinut Gourmande 7.5L autocuiseur; 3045380402034; SEB ClipsoMinut Gourmande 7,5 L autocuiseur
- Market research: autocuiseur acheter
- Stores searched for the product: electrodepot.fr, darty.com, mathon.fr, cuisinstore.com, seb.fr, claudiaandjulia.com, carrefour.fr, auchan.fr, ubaldi.com, cuisineandco.com, conforama.fr, leclercdrive.fr
- Sites skipped: achetezlemeilleur.ca (other_market: A shop for another country (CA).); ouest-france.fr (media_or_review: News site with buying guides, not a shop.); 123comparer.fr (price_comparison: Compares prices and offers from retailers.); facebook.com (not_a_shop: Social network, not a product retailer.); convicook.com (media_or_review: Informational article about pressure cookers.); sitram.fr (brand_shop: Own-brand cookware site; sells Sitram, not SEB.); fr.wikipedia.org (not_a_shop: Encyclopedia, not a shop.); quechoisir.org (media_or_review: Consumer advice and buying-guide site.); idealo.fr (price_co
- Screened 17 pages, kept 7
- ✓ **e.leclerc** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.e.leclerc/fp/cocotte-minute-7-5l-acier-inoxydable-p4624877-seb-3045380402034>
- ✓ **fnac.com** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.fnac.com/SEB-Cocotte-minute-7-5L-ClipsoMinut-Gourmande-P4624877/a22046556/w-4>
- ✓ **auchan.fr** 126.10 EUR (conf. 0.96) — Both listings identify the same SEB ClipsoMinut Gourmande 7.5L pressure cooker, with no differing variant markers. <https://www.auchan.fr/seb-autocuiseur-clipsominut-gourmande-7-5l/pr-296ef128-ec5d-4f2d-9411-b55483301a80>
- ✓ **showroomprive.com** 117.51 EUR (conf. 0.83) — Both listings identify the SEB ClipsoMinut Gourmande 7.5L autocooker with matching model and capacity. <https://www.showroomprive.com/market/catalog/productp.aspx?produit=m-10691928>
- rejected at verify: but.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: brico-travo.com — Page not found (HTTP 404) — the product may have been removed.
- rejected at verify: carrefour.fr — The AI-read price could not be verified against the page text.

## fr-ordinary-serum — Cosmetics in an online pharmacy, EAN

- Page: https://www.redcare-pharmacie.fr/beaute/BE04657888/the-ordinary-niacinamide-10-zinc-1.htm
- Read: THE ORDINARY Niacinamide 10% + Zinc 1% · brand The Ordinary. · GTIN 0769915195941 · MPN BE003370 · 5.69 EUR · market france
- Status: completed
- Attempts: 2 · queries: The Ordinary Niacinamide 10% + Zinc 1% 30 ml acheter; 0769915195941; The Ordinary Niacinamide 10% Zinc 1% 30 ml France; "The Ordinary" "Niacinamide 10% + Zinc 1%" 30 ml France acheter; "Niacinamide 10% + Zinc 1%" "The Ordinary" site:pharmacie*.fr; "769915195941" sérum niacinamide
- Market research: sérum niacinamide zinc acheter en ligne; sérum niacinamide The Ordinary acheter
- Stores searched for the product: nocibe.fr, boticinal.com, theordinary.com, lookfantastic.fr, stylevana.com, pharmaciepolygone.com, paraplus.fr, sephora.fr, notino.fr, marionnaud.fr, easypara.fr, cocooncenter.com, pharmaciedesdrakkars.com, ohmycream.com, pharmacie-forum-halles-paris.com, galaxus.fr, paraclik.com, bleulibellule.com, beautybay.com, douglas.fr, beautycoiffure.com, pharma-gdd.com, pharmacie-prado-mermoz.com, lasante.net
- Sites skipped: iciparisxl.be (other_market: A shop for another country (BE).); ecco-verde.be (other_market: A shop for another country (BE).); sephora.ch (other_market: A shop for another country (CH).); douglas.ch (other_market: A shop for another country (CH).); idealo.fr (price_comparison: Compares prices and merchants; does not stock products.); 20minutes.fr (media_or_review: News and editorial site, not a product shop.); touchelab.com (unknown: No verdict from the model.); fr.shopping.rakuten.com (marketplace: Marketplace with third-party sellers offering skincare.); bfmtv.com (media_or_review: News and
- Screened 40 pages, kept 8
- ✓ **pharmacie-forum-halles-paris.com** 6.00 EUR (conf. 0.99) — Both listings are The Ordinary Niacinamide 10% + Zinc 1% in the 30 ml size. <https://www.pharmacie-forum-halles-paris.com/the-ordinary-niacinamide-10-zinc-1-30ml-p51129>
- ✓ **pharma-gdd.com** 5.99 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.pharma-gdd.com/fr/the-ordinary-serum-niacinamide-10-zinc-1>
- ✓ **theordinary.com** 6.00 EUR (conf. 0.96) — Both listings identify The Ordinary Niacinamide 10% + Zinc 1% in the same 30 ml size; no variant difference is indicated. <https://theordinary.com/fr-fr/niacinamide-10-zinc-1-serum-100436.html>
- rejected at verify: sephora.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: nocibe.fr — No price found on the page.
- rejected at verify: paraclik.com — Sells in DZD, outside your market (EUR).
- rejected at verify: beautybay.com — Sells in USD, outside your market (EUR).

## nl-philips-airfryer — Appliance, no EAN in the page data, possibly discontinued

- Page: https://www.coolblue.nl/en/product/878234/philips-airfryer-l-hd9252-70.html
- Read: Philips Airfryer L HD9252/70 · brand Philips · GTIN None · MPN None · 99.00 EUR · market netherlands
- Status: completed
- Attempts: 2 · queries: Philips Airfryer L HD9252/70 kopen; Philips HD9252/70 airfryer; "HD9252/70" Philips airfryer; "HD9252 70" Philips Airfryer L; Philips HD9252/70 airfryer kopen Nederland
- Market research: airfryer kopen; airfryer kopen
- Stores searched for the product: mediamarkt.nl, expert.nl, wehkamp.nl, blokker.nl, bcc.nl, fonq.nl, alternate.nl, boxxer.nl, ep.nl, electroworld.nl, debijenkorf.nl, makro.nl, voordeelshop.nl, philips.nl, kijkshop.nl
- Sites skipped: bol.com (marketplace: Marketplace with appliance sellers and Philips products.); amazon.nl (marketplace: Marketplace with many sellers and Philips products.); eldi.be (other_market: A shop for another country (BE).); coolblue.be (other_market: A shop for another country (BE).); mediamarkt.be (other_market: A shop for another country (BE).); vandenborre.be (other_market: A shop for another country (BE).); test-aankoop.be (other_market: A shop for another country (BE).); us.home-appliances.philips (other_market: A shop for another country (US).); knibble.nl (price_comparison: Compares prices rat
- Screened 29 pages, kept 2
- rejected at verify: airfryerkopen.nl — No price found on the page.
- rejected at verify: piest.nl — This doesn't look like a single product page.

## pl-logitech-mouse — Electronics, EAN, currency PLN

- Page: https://mediamarkt.pl/pl/product/_mysz-logitech-mx-master-3s-bluetooth-edition-grafitowy-1497571.html
- Read: Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · brand LOGITECH · GTIN 5099206129382 · MPN None · 319.99 PLN · market poland
- Status: completed
- Attempts: 2 · queries: Logitech MX Master 3S SE Bluetooth Edition grafitowy; 5099206129382; Logitech MX Master 3S SE mysz grafitowa; Logitech 910-006559 MX Master 3S Bluetooth Edition graphite sklep Polska; Logitech MX Master 3S grafitowa 910-006559; 5099206129382 Logitech mysz sklep Polska
- Market research: mysz Logitech MX Master 3S kup; mysz ergonomiczna bezprzewodowa kup online
- Stores searched for the product: lenovo24.pl, sferis.pl, komputronik.pl, itnes.pl, euro.com.pl, mediaexpert.pl, morele.net, supertech.pl, x-kom.pl, logitech.com, oleole.pl, proshop.pl, avans.pl, vobis.pl, bechtle.com, kupcochcesz.pl, shoplet.pl, drukarki.pl, neonet.pl, proline.pl, al.to, senetic.pl, delkom.pl, matrixmedia.pl, notebooki.pl, amso.pl, balta.pl, 1.pl
- Sites skipped: arena.pl (marketplace: Marketplace listing Logitech MX Master 3S.); allegro.pl (marketplace: Marketplace listing the Bluetooth Edition model.); ceneo.pl (price_comparison: Compares prices and links to retailers.); e-katalog.pl (price_comparison: Catalog and price-comparison site.); zlozone.net (media_or_review: Product review article, not a shop.); geex.x-kom.pl (media_or_review: Technology review site.); dell24.pl (brand_shop: Dell-focused shop; not the Logitech brand store.); hppartner.pl (brand_shop: HP-focused shop; not the Logitech brand store.); reddit.com (not_a_shop: Discussion forum, 
- Screened 46 pages, kept 6
- ✓ **komputronik.pl** 340.00 PLN (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.komputronik.pl/product/984087/myszka-logitech-mx-master-3s-se-grafitowy.html>
- ✓ **senetic.pl** 305.70 PLN (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.senetic.pl/product/910-007501>
- rejected at verify: mediaexpert.pl — This doesn't look like a single product page.
- rejected at verify: euro.com.pl — No price found on the page.
- rejected at verify: x-kom.pl — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: al.to — No price found on the page.
