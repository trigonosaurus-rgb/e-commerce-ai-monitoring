# Discovery agent — cross-market eval

10 cases · cases with ≥1 correct match: 8/10 · proposals: 24 correct, 0 wrong, 0 unlabeled · precision 100%
Tavily credits spent this run: 39 · LLM $0.022 · 5 min

| Case | Market | Read as | Proposed | ✓ | ✗ | ? | Credits | LLM $ |
|---|---|---|---|---|---|---|---|---|
| us-lodge-skillet | US | Lodge 10.25" Cast Iron Skillet - L8SK3 · 24.90 USD | 4 | 4 | 0 | 0 | 4 | 0.003 |
| us-hoka-clifton | US | HOKA Clifton 10 · 104.88 USD | 4 | 4 | 0 | 0 | 2 | 0.001 |
| us-fellow-kettle | US | Fellow Stagg EKG · 165.00 USD | 4 | 4 | 0 | 0 | 2 | 0.001 |
| uk-ninja-airfryer | UK | Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · 99.00 GBP | 2 | 2 | 0 | 0 | 9 | 0.005 |
| uk-helen-round-towel | UK | Winter Fox Linen Tea Towel · 18.00 GBP | 1 | 1 | 0 | 0 | 5 | 0.002 |
| uk-lakeland-tin | UK | Lakeland Brownie Traybake Tin · 9.99 GBP | 0 | 0 | 0 | 0 | 6 | 0.001 |
| fr-seb-pressure-cooker | France | Autocuiseur SEB ClipsoMinut Gourmande 7.5L · 126.10 EUR | 4 | 4 | 0 | 0 | 2 | 0.002 |
| fr-ordinary-serum | France | THE ORDINARY Niacinamide 10% + Zinc 1% · 5.69 EUR | 3 | 3 | 0 | 0 | 2 | 0.001 |
| nl-philips-airfryer | Netherlands | Philips Airfryer L HD9252/70 · 99.00 EUR | 0 | 0 | 0 | 0 | 5 | 0.002 |
| pl-logitech-mouse | Poland | Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · 319.99 P | 2 | 2 | 0 | 0 | 2 | 0.002 |

## us-lodge-skillet — Kitchen, branded, UPC on the page

- Page: https://www.abt.com/Lodge-10.25-Cast-Iron-Skillet-L8SK3/p/81755.html
- Read: Lodge 10.25" Cast Iron Skillet - L8SK3 · brand Lodge · GTIN 0075536300801 · MPN L8SK3 · 24.90 USD · market united states
- Status: completed
- Attempts: 1 · queries: Lodge L8SK3 10.25 inch cast iron skillet; 0075536300801; Lodge L8SK3 skillet cast iron
- Retailers guessed: walmart.com, target.com, kohls.com, macys.com, acehardware.com, tractorsupply.com, dickssportinggoods.com, amazon.com
- Screened 20 pages, kept 7
- ✓ **rainsofojai.com** 46.00 USD (conf. 0.99) — Same EAN/GTIN code on both pages. <https://rainsofojai.com/10-25-cast-iron-skillet-l8sk3-lodge>
- ✓ **walmart.com** 24.90 USD (conf. 0.95) — Both listings describe Lodge’s seasoned 10.25-inch cast iron skillet, with no conflicting model or variant details. <https://www.walmart.com/ip/Lodge-10-1-4-Cast-Iron-Skillet/5969628>
- ✓ **shop.harmonsgrocery.com** 39.99 USD (conf. 0.94) — Both listings describe Lodge’s 10.25-inch cast iron skillet, with no conflicting model or variant details. <https://shop.harmonsgrocery.com/store/harmons/products/169296-lodge-cast-iron-10-25-cast-iron-skillet-1-ea>
- ✓ **bar-b-que.com** 29.99 USD (conf. 0.9) — Same manufacturer part number (L8SK3). <https://www.bar-b-que.com/lodge-l8sk3-logic-cast-iron-skillet-10-31-in>
- rejected at verify: homedepot.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: amazon.com — No price found on the page.
- rejected at verify: katom.com — This doesn't look like a single product page.

## us-hoka-clifton — Running shoes: sizes and colourways, no codes on the page

- Page: https://www.runningwarehouse.com/HOKA_Clifton_10/descpage-H10CM15.html
- Read: HOKA Clifton 10 · brand HOKA · GTIN None · MPN None · 104.88 USD · market united states
- Status: completed
- Attempts: 1 · queries: HOKA Clifton 10 Men's Raw Linen Stone; HOKA Clifton 10 men's shoes; HOKA Clifton 10 Raw Linen/Stone men's
- Retailers guessed: roadrunnersports.com, fleetfeet.com, dickssportinggoods.com, rei.com, zappos.com, holabirdsports.com, athleticannex.com, theathletesfoot.com
- Screened 26 pages, kept 9
- ✓ **therunhouse.com** 103.95 USD (conf. 0.98) — Both listings are HOKA Clifton 10 men's shoes in Raw Linen/Stone. <https://therunhouse.com/products/men-s-clifton-10-raw-linen-stone>
- ✓ **shop.rrrc.run** 124.00 USD (conf. 0.94) — Both listings are HOKA men's Clifton 10 shoes in Raw Linen/Stone. <https://shop.rrrc.run/product/5404456/hoka/mens-clifton-10>
- ✓ **fleetfeet.com** 116.25 USD (conf. 0.91) — Both listings are for the men's HOKA Clifton 10; the other listing does not specify a different color or variant. <https://www.fleetfeet.com/products/mens-hoka-clifton-10>
- ✓ **zappos.com** 108.50 USD (conf. 0.91) — Both listings are the men's HOKA Clifton 10; the Zappos listing does not specify a color, so no variant mismatch is established. <https://www.zappos.com/p/mens-hoka-clifton-10/product/9984276>
- rejected at verify: hoka.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: footlocker.com — Page not found (HTTP 404) — the product may have been removed.
- rejected at verify: roadrunnersports.com — Both are men's HOKA Clifton 10 shoes, but the first specifies Raw Linen/Stone while the second does not identify a color variant.
- rejected at verify: rei.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.

## us-fellow-kettle — Specialty coffee shop (Shopify), shop name in the brand field

- Page: https://us.lacabra.com/products/fellow-stagg-ekg-2
- Read: Fellow Stagg EKG · brand None · GTIN None · MPN None · 165.00 USD · market united states
- Status: completed
- Attempts: 1 · queries: Fellow Stagg EKG electric kettle; Fellow Stagg EKG kettle buy; Fellow Stagg EKG pour-over kettle
- Retailers guessed: williams-sonoma.com, surlatable.com, crateandbarrel.com, prima-coffee.com, clivecoffee.com, seattlecoffeegear.com, food52.com
- Screened 22 pages, kept 5
- ✓ **formandfunctioncoffee.com** 169.95 USD (conf. 0.96) — Both listings identify the Fellow Stagg EKG electric kettle, with no differing model or variant details. <https://formandfunctioncoffee.com/shop/fellow-stagg-ekg-electric-kettle/>
- ✓ **costco.com** 129.99 USD (conf. 0.91) — Both listings identify the Fellow Stagg EKG kettle, and neither indicates a different variant or edition. <https://www.costco.com/p/-/fellow-stagg-ekg-electric-kettle/4000397413>
- ✓ **palomacoffeebakery.com** 165.00 USD (conf. 0.91) — Both listings identify the Fellow Stagg EKG electric kettle, with no different model or variant indicated. <https://palomacoffeebakery.com/products/fellow-stagg-ekg-electric-kettle>
- ✓ **domacoffee.com** 169.95 USD (conf. 0.9) — Both listings are for the Fellow Stagg EKG kettle, with no conflicting variant or market details. <https://www.domacoffee.com/products/fellow-ekg-kettle>
- rejected at verify: fellowproducts.com — The other listing’s page title includes “Pro” and “Pro Studio” variant markers, which are absent from your listing.

## uk-ninja-airfryer — Small appliance, shop SKU instead of the maker's model code

- Page: https://www.euronics.co.uk/catalogue/small-appliances/small-cooking-appliances/air-fryers/ninja-af100uk-38l-air-fryer-and-dehydrator-grey/p/NINAF100UK
- Read: Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · brand Ninja · GTIN None · MPN NINAF100UK · 99.00 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Ninja AF100UK 3.8L air fryer and dehydrator; Ninja AF100UK air fryer grey buy UK; Ninja AF100UK air fryer dehydrator UK stockist; Ninja AF100UK 3.8 litre fryer grey retailer; NINAF100UK air fryer buy online UK
- Retailers guessed: ao.com, currys.co.uk, argos.co.uk, johnlewis.com, very.co.uk, robertdyas.co.uk, lakeland.co.uk, direct-vacuum.co.uk, appliancesdirect.co.uk, hughes.co.uk, sonicdirect.co.uk, buywiseappliances.co.uk, electricaldiscountuk.co.uk, electricalworld.com, tesco.com, freemans.com, littlewoods.com, bush.co.uk
- Screened 41 pages, kept 13
- ✓ **mobiletvservices.co.uk** 99.00 GBP (conf. 0.98) — The listing matches the Ninja AF100UK model, 3.8L capacity, and grey color. <https://www.mobiletvservices.co.uk/ninja-af100uk-grey-20251.html>
- ✓ **very.co.uk** 109.00 GBP (conf. 0.95) — Both listings identify the Ninja AF100UK 3.8L single-basket air fryer; the 4-in-1 label and differing retailer MPN do not indicate a different model or variant. <https://www.very.co.uk/ninja-4-in-1-38-litre-single-basketnbspair-fryer-af100uk/1600348148.prd>
- rejected at verify: amazon.co.uk — No price found on the page.
- rejected at verify: robertdyas.co.uk — No price found on the page.
- rejected at verify: johnlewis.com — No price found on the page.
- rejected at verify: business.currys.co.uk — No price found on the page.
- rejected at verify: callaghanselectrical.co.uk — The listing is a CB350UK blender, while your product is an AF100UK air fryer and dehydrator.
- rejected at verify: appliancesdirect.co.uk — Page not found (HTTP 410) — the product may have been removed.
- rejected at verify: littlewoods.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: freemans.com — Couldn't load the page: the site did not respond in time; the backup reader (Tavily) was blocked too.
- rejected at verify: tesco.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.

## uk-helen-round-towel — Small designer brand without EAN, sold by gift shops

- Page: https://countrylivingshop.co.uk/products/winter-fox-linen-tea-towel
- Read: Winter Fox Linen Tea Towel · brand Helen Round · GTIN None · MPN None · 18.00 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Helen Round Winter Fox Linen Tea Towel; "Winter Fox" "Helen Round" tea towel; Helen Round Winter Fox tea towel UK; Helen Round Winter Fox tea towel buy UK; Helen Round fox linen kitchen towel; "Winter Fox" linen tea towel Helen Round stockist
- Retailers guessed: johnlewis.com, fenwick.co.uk, grahamandgreen.co.uk, naturalcollection.com, shop.nationaltrust.org.uk, britishmuseumshoponline.org, libertylondon.com, selfridges.com, heals.com, amara.com, theconranshop.com, houseofbruar.com, lisaangel.co.uk, thecontemporaryhome.com, utilitydesign.co.uk, rhsplants.co.uk
- Screened 15 pages, kept 3
- ✓ **helenround.com** 18.00 GBP (conf. 0.98) — Both listings name the Winter Fox Linen Tea Towel, with no variant or market difference indicated. <https://www.helenround.com/products/winter-fox-collection-linen-tea-towel>
- rejected at verify: helenround.com — This doesn't look like a single product page.
- rejected at verify: hotlifeonline.com — Sells in USD, outside your market (GBP).

## uk-lakeland-tin — Shop's own brand (negative control)

- Page: https://www.lakeland.co.uk/products/lakeland-brownie-traybake-tin
- Read: Lakeland Brownie Traybake Tin · brand Lakeland · GTIN None · MPN None · 9.99 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Lakeland Brownie Traybake Tin; Lakeland Brownie Traybake Baking Tin; "Lakeland Brownie Traybake Tin" UK; Lakeland brownie traybake tin 33 x 23 cm; Lakeland non-stick brownie baking tin rectangular UK; Lakeland brownie pan baking tin
- Retailers guessed: dunelm.com, robertdyas.co.uk, hartsofstur.com, johnlewis.com, very.co.uk, argos.co.uk, therange.co.uk, hobbycraft.co.uk, nisbets.co.uk, procook.co.uk, souschef.co.uk, bakerybits.co.uk, cakecraftshop.co.uk, kitchenwarehouse.uk.com, tesco.com, sainsburys.co.uk
- Screened 27 pages, kept 0

## fr-seb-pressure-cooker — Cookware, EAN, French-language shop

- Page: https://www.boulanger.com/ref/1230647
- Read: Autocuiseur SEB ClipsoMinut Gourmande 7.5L · brand SEB · GTIN 3045380402034 · MPN None · 126.10 EUR · market france
- Status: completed
- Attempts: 1 · queries: SEB ClipsoMinut Gourmande 7.5L autocuiseur; 3045380402034; SEB ClipsoMinut Gourmande 7,5 L cocotte-minute
- Retailers guessed: darty.com, fnac.com, cdiscount.com, carrefour.fr, auchan.fr, conforama.fr, manomano.fr
- Screened 24 pages, kept 8
- ✓ **e.leclerc** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.e.leclerc/fp/cocotte-minute-7-5l-acier-inoxydable-p4624877-seb-3045380402034>
- ✓ **fnac.com** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.fnac.com/SEB-Cocotte-minute-7-5L-ClipsoMinut-Gourmande-P4624877/a22046556/w-4>
- ✓ **auchan.fr** 126.10 EUR (conf. 0.98) — Both listings identify the SEB ClipsoMinut Gourmande 7.5L autocooker, with no conflicting variant details. <https://www.auchan.fr/seb-autocuiseur-clipsominut-gourmande-7-5l/pr-296ef128-ec5d-4f2d-9411-b55483301a80>
- ✓ **showroomprive.com** 117.51 EUR (conf. 0.87) — Both listings identify the SEB ClipsoMinut Gourmande 7.5L autocooker, with no variant differences indicated. <https://www.showroomprive.com/market/catalog/productp.aspx?produit=m-10691928>
- rejected at verify: but.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: brico-travo.com — Page not found (HTTP 404) — the product may have been removed.
- rejected at verify: carrefour.fr — The AI-read price could not be verified against the page text.

## fr-ordinary-serum — Cosmetics in an online pharmacy, EAN

- Page: https://www.redcare-pharmacie.fr/beaute/BE04657888/the-ordinary-niacinamide-10-zinc-1.htm
- Read: THE ORDINARY Niacinamide 10% + Zinc 1% · brand The Ordinary. · GTIN 0769915195941 · MPN BE003370 · 5.69 EUR · market france
- Status: completed
- Attempts: 1 · queries: The Ordinary Niacinamide 10% + Zinc 1% 30 ml; The Ordinary Niacinamide 10% + Zinc 1% 0769915195941; sérum The Ordinary Niacinamide 10% Zinc 1% 30 ml; 0769915195941
- Retailers guessed: sephora.fr, nocibe.fr, easypara.fr, cocooncenter.com, lookfantastic.fr, pharma-gdd.com, parapharmadirect.com, atida.fr
- Screened 33 pages, kept 4
- ✓ **pharma-gdd.com** 5.99 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.pharma-gdd.com/fr/the-ordinary-serum-niacinamide-10-zinc-1>
- ✓ **lookfantastic.fr** 5.75 EUR (conf. 0.98) — Both listings are The Ordinary Niacinamide 10% + Zinc 1% serum in the 30 ml size. <https://www.lookfantastic.fr/p/the-ordinary-niacinamide-10-zinc-1-serum-30ml/13187076/>
- ✓ **boticinal.com** 5.99 EUR (conf. 0.97) — Both listings describe The Ordinary Niacinamide 10% + Zinc 1% serum in the same 30 ml size. <https://www.boticinal.com/the-ordinary-niacinamide-10-zinc-1-serum-anti-imperfections-visage-peaux-normales-a-imperfections-30ml.html>
- rejected at verify: sephora.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.

## nl-philips-airfryer — Appliance, no EAN in the page data, possibly discontinued

- Page: https://www.coolblue.nl/en/product/878234/philips-airfryer-l-hd9252-70.html
- Read: Philips Airfryer L HD9252/70 · brand Philips · GTIN None · MPN None · 99.00 EUR · market netherlands
- Status: completed
- Attempts: 2 · queries: Philips Airfryer L HD9252/70 kopen; Philips HD9252/70 airfryer; Philips HD9252/70 heteluchtfriteuse; Philips HD9252/70 Airfryer L kopen Nederland; Philips HD9252/70 heteluchtfriteuse aanbieding; "HD9252/70" Philips Airfryer
- Retailers guessed: mediamarkt.nl, wehkamp.nl, expert.nl, ep.nl, blokker.nl, electroworld.nl, fonq.nl, debijenkorf.nl, alternate.nl, maxict.nl, kookpunt.nl, kokenkoken.nl, makro.nl, praxis.nl
- Screened 32 pages, kept 2
- rejected at verify: joybuy.nl — This doesn't look like a single product page.
- rejected at verify: airfryerkopen.nl — No price found on the page.

## pl-logitech-mouse — Electronics, EAN, currency PLN

- Page: https://mediamarkt.pl/pl/product/_mysz-logitech-mx-master-3s-bluetooth-edition-grafitowy-1497571.html
- Read: Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · brand LOGITECH · GTIN 5099206129382 · MPN None · 319.99 PLN · market poland
- Status: completed
- Attempts: 1 · queries: Logitech MX Master 3S SE Bluetooth Edition grafitowy; Logitech MX Master 3S Bluetooth Edition 5099206129382; 5099206129382
- Retailers guessed: euro.com.pl, x-kom.pl, morele.net, komputronik.pl, al.to
- Screened 28 pages, kept 6
- ✓ **morele.net** 319.00 PLN (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.morele.net/mysz-logitech-mx-master-3s-bluetooth-edition-graphite-910-007501-15520069/>
- ✓ **komputronik.pl** 340.00 PLN (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.komputronik.pl/product/984087/myszka-logitech-mx-master-3s-se-grafitowy.html>
- rejected at verify: mediaexpert.pl — This doesn't look like a single product page.
- rejected at verify: euro.com.pl — No price found on the page.
- rejected at verify: al.to — No price found on the page.
- rejected at verify: x-kom.pl — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
