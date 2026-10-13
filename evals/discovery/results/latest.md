# Discovery agent — cross-market eval

10 cases · cases with ≥1 correct match: 9/10 · proposals: 25 correct, 2 wrong, 1 unlabeled · precision 93%
Tavily credits spent this run: 57 · LLM $0.031 · 9 min

| Case | Market | Read as | Proposed | ✓ | ✗ | ? | Credits | LLM $ |
|---|---|---|---|---|---|---|---|---|
| us-lodge-skillet | US | Lodge 10.25" Cast Iron Skillet - L8SK3 · 24.90 USD | 3 | 3 | 0 | 0 | 2 | 0.004 |
| us-hoka-clifton | US | HOKA Clifton 10 · 104.88 USD | 4 | 4 | 0 | 0 | 2 | 0.002 |
| us-fellow-kettle | US | Fellow Stagg EKG · 165.00 USD | 4 | 4 | 0 | 0 | 6 | 0.003 |
| uk-ninja-airfryer | UK | Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · 99.00 GBP | 5 | 4 | 0 | 1 | 9 | 0.004 |
| uk-helen-round-towel | UK | Winter Fox Linen Tea Towel · 18.00 GBP | 1 | 1 | 0 | 0 | 7 | 0.003 |
| uk-lakeland-tin | UK | Lakeland Brownie Traybake Tin · 9.99 GBP | 0 | 0 | 0 | 0 | 6 | 0.003 |
| fr-seb-pressure-cooker | France | Autocuiseur SEB ClipsoMinut Gourmande 7.5L · 126.10 EUR | 4 | 4 | 0 | 0 | 3 | 0.002 |
| fr-ordinary-serum | France | THE ORDINARY Niacinamide 10% + Zinc 1% · 5.69 EUR | 4 | 3 | 1 | 0 | 7 | 0.004 |
| nl-philips-airfryer | Netherlands | Philips Airfryer L HD9252/70 · 99.00 EUR | 2 | 1 | 1 | 0 | 7 | 0.003 |
| pl-logitech-mouse | Poland | Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · 319.99 P | 1 | 1 | 0 | 0 | 8 | 0.004 |

## us-lodge-skillet — Kitchen, branded, UPC on the page

- Page: https://www.abt.com/Lodge-10.25-Cast-Iron-Skillet-L8SK3/p/81755.html
- Read: Lodge 10.25" Cast Iron Skillet - L8SK3 · brand Lodge · GTIN 0075536300801 · MPN L8SK3 · 24.90 USD · market united states
- Status: completed
- Attempts: 1 · queries: Lodge L8SK3 10.25 cast iron skillet; 0075536300801; Lodge L8SK3 skillet buy
- Market research: cast iron skillet shop
- Stores searched for the product: lodgecastiron.com, lehmans.com, target.com, kohls.com, macys.com, acehardware.com, homedepot.com, lowes.com, williams-sonoma.com, surlatable.com, basspro.com, jcpenney.com
- Sites skipped: appalachiancastiron.com (brand_shop: Own-brand American-made cast iron cookware.); fbgcastiron.com (brand_shop: Fredericksburg Cast Iron’s own cookware shop.); fieldcompany.com (brand_shop: Field Company sells its own cast iron cookware.); skeppshult1906.com (brand_shop: Skeppshult’s own cast iron cookware shop.); amazon.com (marketplace: Marketplace sellers offer Lodge skillets.); lecreuset.com (brand_shop: Le Creuset’s own cookware shop.); lancastercastiron.com (brand_shop: Lancaster’s own cast iron cookware shop.); stargazercastiron.com (brand_shop: Stargazer’s own cookware shop.); smithey.
- Screened 21 pages, kept 7
- ✓ **rainsofojai.com** 46.00 USD (conf. 0.99) — Same EAN/GTIN code on both pages. <https://rainsofojai.com/10-25-cast-iron-skillet-l8sk3-lodge>
- ✓ **walmart.com** 24.90 USD (conf. 0.95) — Both listings describe a 10.25-inch seasoned cast iron skillet; the Walmart listing does not specify a conflicting model or variant. <https://www.walmart.com/ip/Lodge-10-1-4-Cast-Iron-Skillet/5969628>
- ✓ **shop.harmonsgrocery.com** 39.99 USD (conf. 0.93) — Both listings are for Lodge’s 10.25-inch cast iron skillet, with no conflicting model or variant details. <https://shop.harmonsgrocery.com/store/harmons/products/169296-lodge-cast-iron-10-25-cast-iron-skillet-1-ea>
- rejected at verify: homedepot.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: katom.com — This doesn't look like a single product page.
- rejected at verify: wasserstrom.com — This doesn't look like a single product page.
- rejected at verify: amazon.com — No price found on the page.

## us-hoka-clifton — Running shoes: sizes and colourways, no codes on the page

- Page: https://www.runningwarehouse.com/HOKA_Clifton_10/descpage-H10CM15.html
- Read: HOKA Clifton 10 · brand HOKA · GTIN None · MPN None · 104.88 USD · market united states
- Status: completed
- Attempts: 1 · queries: HOKA Clifton 10 Men's Raw Linen Stone; HOKA Clifton 10 men's shoes; HOKA Clifton 10 Raw Linen Stone men's
- Market research: men's HOKA running shoes
- Stores searched for the product: marathonsports.com, shop.7kft.co, tradehome.com, scheels.com, fleetfeet.com, footlocker.com, whentheshoefits.com, als.com, hoka.com, dickssportinggoods.com, publiclands.com, roadrunnersports.com, rei.com, zappos.com, holabirdsports.com
- Sites skipped: runnersworld.com (media_or_review: Running magazine and product reviews, not a retailer.); runrepeat.com (media_or_review: Running shoe reviews and comparisons, not a shop.); youtube.com (media_or_review: Video platform with shoe review content, not a retailer.); forbes.com (media_or_review: Editorial shoe recommendations, not a shop.)
- Screened 22 pages, kept 7
- ✓ **therunhouse.com** 103.95 USD (conf. 0.99) — Both listings are for HOKA Clifton 10 men's shoes in Raw Linen/Stone. <https://therunhouse.com/products/men-s-clifton-10-raw-linen-stone>
- ✓ **shop.rrrc.run** 124.00 USD (conf. 0.99) — Both listings are HOKA Clifton 10 men's shoes in Raw Linen/Stone. <https://shop.rrrc.run/product/5404456/hoka/mens-clifton-10>
- ✓ **fleetfeet.com** 116.25 USD (conf. 0.87) — Both listings are for the men's HOKA Clifton 10; the other listing does not specify a color, so no variant conflict is indicated. <https://www.fleetfeet.com/products/mens-hoka-clifton-10>
- ✓ **zappos.com** 108.50 USD (conf. 0.84) — Both listings identify the men's HOKA Clifton 10; the Zappos listing does not specify a color, so no variant conflict is evident. <https://www.zappos.com/p/mens-hoka-clifton-10/product/9984276>
- rejected at verify: hoka.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: rei.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: costco.com — The Costco listing does not specify the Raw Linen/Stone color variant, so it cannot be confirmed as the same product.

## us-fellow-kettle — Specialty coffee shop (Shopify), shop name in the brand field

- Page: https://us.lacabra.com/products/fellow-stagg-ekg-2
- Read: Fellow Stagg EKG · brand None · GTIN None · MPN None · 165.00 USD · market united states
- Status: completed
- Attempts: 1 · queries: Fellow Stagg EKG electric kettle; Fellow Stagg EKG kettle buy; Fellow Stagg EKG gooseneck kettle
- Market research: electric gooseneck kettle buy
- Stores searched for the product: target.com, thegingerbreadmansion.com, artizancoffee.com, twinpike.com, williams-sonoma.com, crateandbarrel.com, surlatable.com, seattlecoffeegear.com, prima-coffee.com, wholelattelove.com, clivecoffee.com, abchome.com
- Sites skipped: driproast.com (media_or_review: Gooseneck-kettle review and buying guide.); bonavitabrand.co (brand_shop: Bonavita’s own kettle brand shop.); nytimes.com (media_or_review: Wirecutter product reviews.); cocinare.com (media_or_review: Gooseneck-kettle picks and review content.); shop.greatergoods.com (brand_shop: Greater Goods’ own kettle shop.); thewaytocoffee.com (media_or_review: Coffee equipment testing and buying guide.); youtube.com (media_or_review: Video review platform.); smilingcoffeesnob.com (media_or_review: Coffee gear advice and reviews.); reddit.com (not_a_shop: Discussion forum, 
- Screened 20 pages, kept 7
- ✓ **palomacoffeebakery.com** 165.00 USD (conf. 0.94) — Both listings identify the Fellow Stagg EKG electric kettle, with no differing model or variant indicated. <https://palomacoffeebakery.com/products/fellow-stagg-ekg-electric-kettle>
- ✓ **costco.com** 129.99 USD (conf. 0.91) — Both listings identify the Fellow Stagg EKG electric kettle, with no differing model or variant indicated. <https://www.costco.com/p/-/fellow-stagg-ekg-electric-kettle/4000397413>
- ✓ **formandfunctioncoffee.com** 169.95 USD (conf. 0.9) — Both listings identify the Fellow Stagg EKG electric kettle, with no differing variant or edition specified. <https://formandfunctioncoffee.com/shop/fellow-stagg-ekg-electric-kettle/>
- ✓ **domacoffee.com** 169.95 USD (conf. 0.82) — Both listings refer to Fellow’s EKG kettle, and the second title appears to omit the Stagg name rather than identify a different model. <https://www.domacoffee.com/products/fellow-ekg-kettle>
- rejected at verify: fellowproducts.com — The other listing’s page title includes “Pro” and “Pro Studio,” markers absent from your listing.
- rejected at verify: williams-sonoma.com — No price found on the page.
- rejected at verify: thegingerbreadmansion.com — This doesn't look like a single product page.

## uk-ninja-airfryer — Small appliance, shop SKU instead of the maker's model code

- Page: https://www.euronics.co.uk/catalogue/small-appliances/small-cooking-appliances/air-fryers/ninja-af100uk-38l-air-fryer-and-dehydrator-grey/p/NINAF100UK
- Read: Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · brand Ninja · GTIN None · MPN NINAF100UK · 99.00 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Ninja AF100UK 3.8L Air Fryer and Dehydrator; Ninja AF100UK air fryer; NINAF100UK; Ninja AF100UK air fryer buy UK; Ninja AF100UK dehydrator 3.8 litre retailer; Ninja AF100UK 0622356237644
- Market research: air fryer buy online; Ninja air fryer buy UK
- Stores searched for the product: sharkninja.com, currys.co.uk, argos.co.uk, ao.com, very.co.uk, johnlewis.com, robertdyas.co.uk, dunelm.com, webbs.tv, markselectrical.co.uk, freemans.com, jdwilliams.co.uk, tesco.com, sainsburys.co.uk, asda.com, littlewoods.com, electricaldiscountuk.co.uk, appliancesdirect.co.uk, kitchenappliancesdirect.com, donaghybros.co.uk, hughes.co.uk
- Sites skipped: us.home-appliances.philips (other_market: A shop for another country (US).); amazon.in (online_shop: India-focused retailer; not a UK source.); consumerreports.org (media_or_review: Product reviews and buying advice, not a shop.); macys.com (online_shop: US department store; does not serve the UK market.); target.com (online_shop: US retailer; does not serve the UK market.); bestbuy.com (online_shop: US electronics retailer; does not serve the UK market.); amazon.com (marketplace: US marketplace, rather than a UK shop.); costco.com (online_shop: US retailer; its US range is not the UK market.)
- Screened 32 pages, kept 13
- ? **thewashhouse.com** 99.00 GBP (conf. 0.99) — Both listings name the Ninja AF100UK 3.8L Air Fryer and Dehydrator in grey, with no variant difference indicated. <https://www.thewashhouse.com/ninja/ninja-af100uk-grey-200112629.html>
- ✓ **combensapps.co.uk** 99.99 GBP (conf. 0.98) — Both listings identify the Ninja AF100UK 3.8L Air Fryer and Dehydrator; the grey color is not contradicted by the listing. <https://www.combensapps.co.uk/ninja-af100uk-grey-100002708.html>
- ✓ **panasonicstore-inverness.com** 99.00 GBP (conf. 0.98) — The model AF100UK, 3.8L capacity, product type, and grey color match exactly. <https://panasonicstore-inverness.com/ninja-af100uk-50009826.html>
- ✓ **sainsburys.co.uk** 99.00 GBP (conf. 0.97) — Both listings identify the Ninja AF100UK 3.8L air fryer and dehydrator, with no conflicting variant details. <https://www.sainsburys.co.uk/groceries/product/ninja-38l-air-fryer-and-dehydrator-%E2%80%93-af100uk>
- ✓ **littlewoods.com** 134.99 GBP (conf. 0.95) — Both listings identify the Ninja AF100UK 3.8L air fryer; the 4-in-1 description is consistent with its functions, and no variant difference is indicated. <https://www.littlewoods.com/ninja-air-fryer-af100uk/1600348148.prd?bvstate=pg%3A31%2Fct%3Ar>
- rejected at verify: appliancesdirect.co.uk — Page not found (HTTP 410) — the product may have been removed.
- rejected at verify: freemans.com — Couldn't load the page: the site did not respond in time; the backup reader (Tavily) was blocked too.
- rejected at verify: direct.asda.com — No price found on the page.

## uk-helen-round-towel — Small designer brand without EAN, sold by gift shops

- Page: https://countrylivingshop.co.uk/products/winter-fox-linen-tea-towel
- Read: Winter Fox Linen Tea Towel · brand Helen Round · GTIN None · MPN None · 18.00 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Helen Round Winter Fox Linen Tea Towel; "Winter Fox" "Helen Round" tea towel; Helen Round Winter Fox linen tea towel buy UK; Helen Round Winter Fox tea towel stockist UK; Helen Round fox linen tea towel kitchen towel; Helen Round Winter Fox tea towel shop
- Market research: linen tea towel shop; linen tea towels buy UK
- Stores searched for the product: thebirchstore.com, johnlewis.com, thelinenworks.co.uk, redcandy.co.uk, roseandgrey.co.uk, dotcomgiftshop.com, nationaltrust.org.uk, willowandstone.co.uk, home-landing.co.uk, givans.co.uk, breadtopia.com, towelcompany.co.uk, grahamandgreen.co.uk, amara.com, utilitydesign.co.uk, theconranshop.co.uk, skandium.com, bohemiadesign.co.uk, thehouseofthings.com, lovethyhome.co.uk, thehandcrafted.co.uk
- Sites skipped: us.halemercantile.com (other_market: A shop for another country (US).); us.pigletinbed.com (other_market: A shop for another country (US).); botanicapaper.com (brand_shop: Its own linen tea towels; not Helen Round.); spoonflower.com (marketplace: Custom-designed towels from its own marketplace, not this brand.); ourheiday.com (brand_shop: Sells its own linen tea towels.); facebook.com (not_a_shop: Social media platform, not a shop.); beaheart.com (brand_shop: Its own faith-themed tea towel, not Helen Round.); instagram.com (not_a_shop: Social media platform, not a shop.); floursacktowels.com (
- Screened 14 pages, kept 1
- ✓ **helenround.com** 18.00 GBP (conf. 0.97) — Both listings name the Winter Fox Linen Tea Towel, with no differing variant or condition indicated. <https://www.helenround.com/products/winter-fox-collection-linen-tea-towel>

## uk-lakeland-tin — Shop's own brand (negative control)

- Page: https://www.lakeland.co.uk/products/lakeland-brownie-traybake-tin
- Read: Lakeland Brownie Traybake Tin · brand Lakeland · GTIN None · MPN None · 9.99 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Lakeland Brownie Traybake Tin; Lakeland Brownie Traybake Baking Tin; Lakeland brownie traybake tin UK; Lakeland "Brownie Traybake" tin buy UK; Lakeland brownie traybake baking tin 12 portion; "Lakeland Brownie Traybake Tin" stockist
- Market research: brownie baking tin buy; brownie tin buy UK
- Stores searched for the product: dunelm.com, robertdyas.co.uk, johnlewis.com, hobbycraft.co.uk, nisbets.co.uk, souschef.co.uk, cakecraftworld.co.uk, argos.co.uk, marksandspencer.com, wayfair.co.uk, cakecraftshop.co.uk, bakerybits.co.uk
- Sites skipped: olivemagazine.com (media_or_review: Food magazine with product reviews); etsy.com (marketplace: Marketplace sellers offer baking tins); davidscookies.com (online_shop: US bakery selling baked goods); amazon.com (marketplace: US marketplace, not UK-focused); walmart.com (marketplace: US marketplace, not UK-focused); ebay.com (marketplace: US marketplace, not UK-focused); 360cookware.com (brand_shop: Another cookware brand’s own shop); nordicware.com (brand_shop: Another bakeware brand’s own shop); pmecake.com (online_shop: US baking-supplies shop); usapan.com (brand_shop: Another bakeware brand
- Screened 27 pages, kept 1
- rejected at verify: amazon.co.uk — Sells in EUR, outside your market (GBP).

## fr-seb-pressure-cooker — Cookware, EAN, French-language shop

- Page: https://www.boulanger.com/ref/1230647
- Read: Autocuiseur SEB ClipsoMinut Gourmande 7.5L · brand SEB · GTIN 3045380402034 · MPN None · 126.10 EUR · market france
- Status: completed
- Attempts: 1 · queries: SEB ClipsoMinut Gourmande 7.5L autocuiseur; 3045380402034; autocuiseur SEB ClipsoMinut Gourmande 7,5 L
- Market research: autocuiseur SEB acheter
- Stores searched for the product: darty.com, laboutiquedunet.com, carrefour.fr, mathon.fr, electrodepot.fr, conforama.fr, seb.fr, pulsat.fr, auchan.fr, e.leclerc, ubaldi.com, cuisineaddict.com
- Sites skipped: fr.fnac.be (other_market: A shop for another country (BE).); amazon.com.be (other_market: A shop for another country (BE).); 123comparer.fr (price_comparison: Compares offers from retailers.); idealo.fr (price_comparison: Compares product prices across shops.); 20minutes.fr (media_or_review: News site covering product deals.); amazon.fr (marketplace: Marketplace with SEB cookware offers.); stickafork.net (media_or_review: Publishes a pressure-cooker review.); cdiscount.com (marketplace: Marketplace selling SEB Clipso pressure cookers.); le-sav.com (online_shop: Specializes in replacement parts
- Screened 18 pages, kept 7
- ✓ **e.leclerc** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.e.leclerc/fp/cocotte-minute-7-5l-acier-inoxydable-p4624877-seb-3045380402034>
- ✓ **fnac.com** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.fnac.com/SEB-Cocotte-minute-7-5L-ClipsoMinut-Gourmande-P4624877/a22046556/w-4>
- ✓ **auchan.fr** 126.10 EUR (conf. 0.98) — Both listings identify the SEB ClipsoMinut Gourmande 7.5L autocooker, with no differing variant markers. <https://www.auchan.fr/seb-autocuiseur-clipsominut-gourmande-7-5l/pr-296ef128-ec5d-4f2d-9411-b55483301a80>
- ✓ **showroomprive.com** 117.51 EUR (conf. 0.94) — Both listings identify the SEB ClipsoMinut Gourmande 7.5L, with no variant or market difference indicated. <https://www.showroomprive.com/market/catalog/productp.aspx?produit=m-10691928>
- rejected at verify: but.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: brico-travo.com — Page not found (HTTP 404) — the product may have been removed.
- rejected at verify: carrefour.fr — The AI-read price could not be verified against the page text.

## fr-ordinary-serum — Cosmetics in an online pharmacy, EAN

- Page: https://www.redcare-pharmacie.fr/beaute/BE04657888/the-ordinary-niacinamide-10-zinc-1.htm
- Read: THE ORDINARY Niacinamide 10% + Zinc 1% · brand The Ordinary. · GTIN 0769915195941 · MPN BE003370 · 5.69 EUR · market france
- Status: completed
- Attempts: 2 · queries: The Ordinary Niacinamide 10% + Zinc 1% 30 ml; 0769915195941; The Ordinary Niacinamide 10% Zinc 1% BE003370; "The Ordinary" "Niacinamide 10% + Zinc 1%" acheter France; "The Ordinary Niacinamide 10% Zinc 1%" sérum 30 ml; "0769915195941"
- Market research: sérum niacinamide acheter; sérum niacinamide visage acheter en ligne
- Stores searched for the product: nocibe.fr, farmaciasdirect.fr, theordinary.com, maquibeauty.fr, sephora.fr, marionnaud.fr, lookfantastic.fr, easypara.fr, cocooncenter.com, parapharmacie-en-ligne.com, farma2go.com, parfumdreams.fr, boticinal.com, jeancoutu.com, pharmaforce.fr, sephora.com, notino.fr, beautybay.com, cultbeauty.com, my-origines.com, pharma-gdd.com, atida.fr, basler-beauty.fr, cosmetis.com, carethy.fr
- Sites skipped: siri.mo.it (other_market: A shop for another country (IT).); zalando.lu (other_market: A shop for another country (LU).); noovomoi.ca (other_market: A shop for another country (CA).); farma2go.com (online_shop: Online pharmacy primarily serving Spain, not the French market.); jeancoutu.com (online_shop: Canadian pharmacy retailer, not serving the French market.); 20minutes.fr (media_or_review: News and media website.); amazon.com (marketplace: US marketplace listing other products; not the French market.); ouest-france.fr (media_or_review: News and media website.); aroma-zone.com (brand_shop: 
- Screened 38 pages, kept 5
- ✓ **theordinary.com** 6.00 EUR (conf. 0.98) — Both listings identify The Ordinary Niacinamide 10% + Zinc 1%, and the other listing’s product code indicates the same 30 ml size. <https://theordinary.com/fr-fr/niacinamide-10-zinc-1-serum-100436.html>
- ✓ **boticinal.com** 5.99 EUR (conf. 0.97) — Both listings are The Ordinary Niacinamide 10% + Zinc 1% serum in the 30 ml size. <https://www.boticinal.com/the-ordinary-niacinamide-10-zinc-1-serum-anti-imperfections-visage-peaux-normales-a-imperfections-30ml.html>
- ✗ **notino.fr** 10.80 EUR (conf. 0.92) — Both listings are The Ordinary Niacinamide 10% + Zinc 1%; the differing MPNs and missing size detail do not indicate a different variant. <https://www.notino.fr/the-ordinary/niacinamide-10-zinc-1-high-strength-vitamin-and-mineral-blemish-formula-serum-leger-visage-anti-imperfections-de-la-peau>
- ✓ **my-origines.com** 6.00 EUR (conf. 0.91) — Both listings identify The Ordinary Niacinamide 10% + Zinc 1%; the other listing does not specify a different size or variant. <https://www.my-origines.com/fr/niacinamide-10-zinc-1-89K57102.html?sds=0&sop=0&bvstate=pg%3A3%2Fct%3Ar>
- rejected at verify: sephora.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.

## nl-philips-airfryer — Appliance, no EAN in the page data, possibly discontinued

- Page: https://www.coolblue.nl/en/product/878234/philips-airfryer-l-hd9252-70.html
- Read: Philips Airfryer L HD9252/70 · brand Philips · GTIN None · MPN None · 99.00 EUR · market netherlands
- Status: completed
- Attempts: 2 · queries: Philips Airfryer L HD9252/70 kopen; Philips HD9252/70 airfryer; Philips Airfryer L HD9252/70 Nederland; Philips HD9252/70 4,1 liter airfryer; Philips Essential Airfryer L HD9252/70 kopen; "HD9252/70" airfryer aanbieding
- Market research: airfryer kopen; airfryer kopen
- Stores searched for the product: mediamarkt.nl, wehkamp.nl, expert.nl, blokker.nl, ep.nl, alternate.nl, electroworld.nl, fonq.nl, puurmieke.nl, marskramer.nl, boxxer.nl, joybuy.nl, welhof.com, proshop.nl, yorcom.nl, maxict.nl, voordeeldrogisterij.nl, kookwinkel.nl
- Sites skipped: mediamarkt.be (other_market: A shop for another country (BE).); krefel.be (other_market: A shop for another country (BE).); vandenborre.be (other_market: A shop for another country (BE).); test-aankoop.be (other_market: A shop for another country (BE).); eldi.be (other_market: A shop for another country (BE).); us.home-appliances.philips (other_market: A shop for another country (US).); kitchenbrothers.nl (brand_shop: KitchenBrothers own-brand shop; this is a Philips product.); bol.com (marketplace: Marketplace with many sellers and air fryers.); knibble.nl (price_comparison: Compares prices a
- Screened 38 pages, kept 3
- ✓ **marskramer.nl** 79.99 EUR (conf. 0.95) — Both listings identify the Philips HD9252/70; “Essential” is an additional product-line description, not a different model or variant. <https://www.marskramer.nl/philips-airfryer-essential-hd9252-70-212-9252/>
- ✗ **re.now** 79.00 EUR (conf. 0.95) — Both listings identify the Philips HD9252/70 air fryer; “Essential” is an additional line description, not a different model or variant. <https://re.now/products/philips-airfryer-essential-hd9252-70-1400w>
- rejected at verify: joybuy.nl — This doesn't look like a single product page.

## pl-logitech-mouse — Electronics, EAN, currency PLN

- Page: https://mediamarkt.pl/pl/product/_mysz-logitech-mx-master-3s-bluetooth-edition-grafitowy-1497571.html
- Read: Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · brand LOGITECH · GTIN 5099206129382 · MPN None · 319.99 PLN · market poland
- Status: completed
- Attempts: 2 · queries: Logitech MX Master 3S SE Bluetooth Edition grafitowy; 5099206129382; Logitech MX Master 3S Bluetooth Edition grafitowy kup; Logitech MX Master 3S grafitowa mysz Bluetooth sklep Polska; Logitech 910-007... MX Master 3S SE Polska; Logitech MX Master 3S 5099206129382 sklep internetowy Polska
- Market research: mysz bezprzewodowa Logitech kupić; mysz Logitech MX Master kup
- Stores searched for the product: komputronik.pl, logitech.com, morele.net, x-kom.pl, euro.com.pl, mediaexpert.pl, oleole.pl, sferis.pl, proshop.pl, beafoto.pl, supertech.pl, electro.pl, neonet.pl, avans.pl, proline.pl, senetic.pl, itnes.pl, al.to, komputronik-biznes.pl, sklep.benchmark.pl
- Sites skipped: allegro.pl (marketplace: Marketplace with many sellers offering Logitech mice.); erli.pl (marketplace: Marketplace listing Logitech wireless mice.); ceneo.pl (price_comparison: Compares offers from shops selling Logitech mice.); logitechg.com (brand_shop: Logitech G gaming brand shop; this is a productivity MX mouse.); skapiec.pl (price_comparison: Compares prices and offers for Logitech mice.); e-katalog.pl (price_comparison: Compares Logitech mouse prices across Polish shops.); amazon.pl (marketplace: Marketplace with third-party sellers and Logitech products.); facebook.com (not_a_shop: Soc
- Screened 33 pages, kept 4
- ✓ **itnes.pl** 439.00 PLN (conf. 0.99) — Same EAN/GTIN code on both pages. <https://itnes.pl/myszy-komputerowe-logitech/mysz-bezprzewodowa-logitech-mx-master-3s-bluetooth-edition-910-007501-grafitowa.html>
- rejected at verify: mediaexpert.pl — This doesn't look like a single product page.
- rejected at verify: euro.com.pl — No price found on the page.
- rejected at verify: logitech.com — The first listing includes the “SE” variant marker, which is absent from the second listing.
