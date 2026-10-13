# Discovery agent — cross-market eval (baseline, before fixes)

10 cases · cases with ≥1 correct match: 8/10 · proposals: 17 correct, 2 wrong, 0 unlabeled · precision 89%
Tavily credits spent this run: 86 · LLM $0.019 · 8 min

| Case | Market | Read as | Proposed | ✓ | ✗ | ? | Credits | LLM $ |
|---|---|---|---|---|---|---|---|---|
| us-lodge-skillet | US | Lodge 10.25" Cast Iron Skillet - L8SK3 · 24.90 USD | 2 | 2 | 0 | 0 | 9 | 0.002 |
| us-hoka-clifton | US | HOKA Clifton 10 · 104.88 USD | 3 | 2 | 1 | 0 | 10 | 0.002 |
| us-fellow-kettle | US | Fellow Stagg EKG · 165.00 USD | 3 | 2 | 1 | 0 | 2 | 0.001 |
| uk-ninja-airfryer | UK | Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · 99.00 GBP | 2 | 2 | 0 | 0 | 11 | 0.003 |
| uk-helen-round-towel | UK | Winter Fox Linen Tea Towel · 18.00 GBP | 1 | 1 | 0 | 0 | 8 | 0.001 |
| uk-lakeland-tin | UK | Lakeland Brownie Traybake Tin · 9.99 GBP | 0 | 0 | 0 | 0 | 7 | 0.002 |
| fr-seb-pressure-cooker | France | Autocuiseur SEB ClipsoMinut Gourmande 7.5L · 126.10 EUR | 4 | 4 | 0 | 0 | 6 | 0.002 |
| fr-ordinary-serum | France | THE ORDINARY Niacinamide 10% + Zinc 1% · 5.69 EUR | 2 | 2 | 0 | 0 | 13 | 0.003 |
| nl-philips-airfryer | Netherlands | Philips Airfryer L HD9252/70 · 99.00 EUR | 0 | 0 | 0 | 0 | 8 | 0.002 |
| pl-logitech-mouse | Poland | Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · 319.99 P | 2 | 2 | 0 | 0 | 12 | 0.003 |

## us-lodge-skillet — Kitchen, branded, UPC on the page

- Page: https://www.abt.com/Lodge-10.25-Cast-Iron-Skillet-L8SK3/p/81755.html
- Read: Lodge 10.25" Cast Iron Skillet - L8SK3 · brand Lodge · GTIN 0075536300801 · MPN L8SK3 · 24.90 USD · market united states
- Status: completed
- Attempts: 1 · queries: Lodge L8SK3 10.25 cast iron skillet; 0075536300801; Lodge L8SK3 skillet buy
- Retailers guessed: amazon.com, walmart.com, target.com, kohls.com, macys.com, wayfair.com, sur la table.com, crateandbarrel.com, acehardware.com, lowes.com
- Screened 21 pages, kept 5
- ✓ **rainsofojai.com** 46.00 USD (conf. 0.99) — Same EAN/GTIN code on both pages. <https://rainsofojai.com/10-25-cast-iron-skillet-l8sk3-lodge>
- ✓ **shop.harmonsgrocery.com** 39.99 USD (conf. 0.92) — Both listings identify a Lodge 10.25-inch cast iron skillet, and no conflicting variant details are shown. <https://shop.harmonsgrocery.com/store/harmons/products/169296-lodge-cast-iron-10-25-cast-iron-skillet-1-ea>
- rejected at verify: homedepot.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: katom.com — This doesn't look like a single product page.
- rejected at verify: wasserstrom.com — This doesn't look like a single product page.

## us-hoka-clifton — Running shoes: sizes and colourways, no codes on the page

- Page: https://www.runningwarehouse.com/HOKA_Clifton_10/descpage-H10CM15.html
- Read: HOKA Clifton 10 · brand HOKA · GTIN None · MPN None · 104.88 USD · market united states
- Status: completed
- Attempts: 2 · queries: HOKA Clifton 10 running shoes; HOKA Clifton 10 men's shoes; HOKA Clifton 10; HOKA Clifton 10 men's running shoe buy; HOKA Clifton 10 road running shoe size color; HOKA Clifton 10 1162030
- Retailers guessed: roadrunnersports.com, fleetfeet.com, rei.com, zappos.com, dickssportinggoods.com, nordstrom.com, shoe palace.com, holabirdsports.com, athleticannex.com, thewalkingcompany.com, asics.com, backcountry.com, paragon sports.com, shoemall.com, als.com
- Screened 21 pages, kept 10
- ✓ **costco.com** 114.99 USD (conf. 0.97) — Both listings identify the HOKA Clifton 10, with no conflicting variant details. <https://www.costco.com/p/-/hoka-mens-clifton-10-shoe/4000377854>
- ✓ **fleetfeet.com** 116.25 USD (conf. 0.97) — Both listings are for the HOKA Clifton 10, and the men's designation does not conflict with any variant specified for your product. <https://www.fleetfeet.com/products/mens-hoka-clifton-10>
- ✗ **familyfootwearcenter.com** 124.00 USD (conf. 0.95) — Both listings are HOKA Clifton 10 running shoes; the oatmeal/oat milk color is an unspecified variant of the product. <https://www.familyfootwearcenter.com/hoka-1162030-clifton-10-running-shoes-oatmeal-oat-milk>
- rejected at verify: hoka.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: footlocker.com — Page not found (HTTP 404) — the product may have been removed.
- rejected at verify: dickssportinggoods.com — Couldn't load the page: HTTP 451; the backup reader (Tavily) was blocked too.
- rejected at verify: dickssportinggoods.com — Couldn't load the page: HTTP 451; the backup reader (Tavily) was blocked too.
- rejected at verify: jdsports.com — This doesn't look like a single product page.
- rejected at verify: rei.com — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.

## us-fellow-kettle — Specialty coffee shop (Shopify), shop name in the brand field

- Page: https://us.lacabra.com/products/fellow-stagg-ekg-2
- Read: Fellow Stagg EKG · brand None · GTIN None · MPN None · 165.00 USD · market united states
- Status: completed
- Attempts: 1 · queries: Fellow Stagg EKG electric kettle; Fellow Stagg EKG pour-over kettle for sale
- Retailers guessed: williams-sonoma.com, crateandbarrel.com, sur latable.com, seattlecoffeegear.com, prima-coffee.com, clivecoffee.com, wholelattelove.com
- Screened 11 pages, kept 3
- ✓ **costco.com** 129.99 USD (conf. 0.98) — Both listings identify the Fellow Stagg EKG electric kettle, with no conflicting variant details. <https://www.costco.com/p/-/fellow-stagg-ekg-electric-kettle/4000397413>
- ✗ **fellowproducts.com** 199.95 USD (conf. 0.96) — Both listings identify the Fellow Stagg EKG electric kettle, with no conflicting variant details. <https://fellowproducts.com/products/stagg-ekg-electric-pour-over-kettle>
- ✓ **formandfunctioncoffee.com** 169.95 USD (conf. 0.96) — Both listings identify the Fellow Stagg EKG electric kettle, with no conflicting model or variant details. <https://formandfunctioncoffee.com/shop/fellow-stagg-ekg-electric-kettle/>

## uk-ninja-airfryer — Small appliance, shop SKU instead of the maker's model code

- Page: https://www.euronics.co.uk/catalogue/small-appliances/small-cooking-appliances/air-fryers/ninja-af100uk-38l-air-fryer-and-dehydrator-grey/p/NINAF100UK
- Read: Ninja AF100UK 3.8L Air Fryer and Dehydrator - Grey · brand Ninja · GTIN None · MPN NINAF100UK · 99.00 GBP · market united kingdom
- Status: completed
- Attempts: 1 · queries: Ninja AF100UK 3.8L Air Fryer and Dehydrator Grey; Ninja AF100UK air fryer
- Retailers guessed: currys.co.uk, argos.co.uk, johnlewis.com, ao.com, very.co.uk, robertdyas.co.uk, lakeland.co.uk, dunelm.com
- Screened 20 pages, kept 6
- ✓ **noelgrimleys.com** 99.99 GBP (conf. 0.98) — The model, 3.8L capacity, product type, and grey color match; the MPNs refer to the same AF100UK model. <https://noelgrimleys.com/p-24018-ninja-af100uk-3-8l-air-fryer-and-dehydrator-grey.aspx>
- ✓ **very.co.uk** 109.00 GBP (conf. 0.98) — Both listings identify the Ninja AF100UK with a 3.8 L capacity; the title wording differs but indicates the same model and variant. <https://www.very.co.uk/ninja-4-in-1-38-litre-single-basketnbspair-fryer-af100uk/1600348148.prd>
- rejected at verify: johnlewis.com — No price found on the page.
- rejected at verify: business.currys.co.uk — No price found on the page.
- rejected at verify: robertdyas.co.uk — No price found on the page.

## uk-helen-round-towel — Small designer brand without EAN, sold by gift shops

- Page: https://countrylivingshop.co.uk/products/winter-fox-linen-tea-towel
- Read: Winter Fox Linen Tea Towel · brand Helen Round · GTIN None · MPN None · 18.00 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Helen Round Winter Fox Linen Tea Towel; Helen Round fox linen tea towel UK; "Winter Fox" "Helen Round" tea towel; Helen Round Winter Fox tea towel stockist UK; Helen Round Winter Fox tea towel linen shop; "Winter Fox" Helen Round tea towel buy
- Retailers guessed: thebasketcompany.com, contemporaryhome.com, nationaltrust.org.uk, shop.britishmuseum.org, shop.rhs.org.uk, designmuseumshop.com, amara.com, johnlewis.com, utilitydesign.co.uk, thefuturekept.com, theconranshop.com, heals.com, roseandgrey.co.uk, designist.ie, lifestyle.co.uk, fenwick.co.uk
- Screened 11 pages, kept 2
- ✓ **helenround.com** 18.00 GBP (conf. 0.98) — The listing has the same product name, and no conflicting variant details are shown. <https://www.helenround.com/products/winter-fox-collection-linen-tea-towel>
- rejected at verify: helenround.com — The listing describes generic linen tea towels and does not identify the specific Winter Fox design.

## uk-lakeland-tin — Shop's own brand (negative control)

- Page: https://www.lakeland.co.uk/products/lakeland-brownie-traybake-tin
- Read: Lakeland Brownie Traybake Tin · brand Lakeland · GTIN None · MPN None · 9.99 GBP · market united kingdom
- Status: completed
- Attempts: 2 · queries: Lakeland Brownie Traybake Tin; Lakeland brownie traybake tin buy UK; Lakeland brownie tin traybake; Lakeland brownie traybake tin 20 x 20 cm UK; Lakeland brownie baking tin traybake pan buy UK; Lakeland square brownie tin Lakeland baking tin
- Retailers guessed: robertdyas.co.uk, johnlewis.com, dunelm.com, nisbets.co.uk, souschef.co.uk, wayfair.co.uk, very.co.uk, next.co.uk, thecookskitchen.com, kitchenwareonline.com, harts of stur.com
- Screened 18 pages, kept 1
- rejected at verify: amazon.co.uk — Sells in EUR, outside your market (GBP).

## fr-seb-pressure-cooker — Cookware, EAN, French-language shop

- Page: https://www.boulanger.com/ref/1230647
- Read: Autocuiseur SEB ClipsoMinut Gourmande 7.5L · brand SEB · GTIN 3045380402034 · MPN None · 126.10 EUR · market france
- Status: completed
- Attempts: 1 · queries: SEB ClipsoMinut Gourmande 7,5 L autocuiseur; 3045380402034; autocuiseur SEB ClipsoMinut Gourmande 7.5L
- Retailers guessed: darty.com, fnac.com, carrefour.fr, auchan.fr, ubaldi.com, conforama.fr, electrodepot.fr
- Screened 21 pages, kept 7
- ✓ **e.leclerc** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.e.leclerc/fp/cocotte-minute-7-5l-acier-inoxydable-p4624877-seb-3045380402034>
- ✓ **fnac.com** 110.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.fnac.com/SEB-Cocotte-minute-7-5L-ClipsoMinut-Gourmande-P4624877/a22046556/w-4>
- ✓ **auchan.fr** 126.10 EUR (conf. 0.98) — Both listings identify the SEB ClipsoMinut Gourmande 7.5L autocooker, with no differing variant details. <https://www.auchan.fr/seb-autocuiseur-clipsominut-gourmande-7-5l/pr-296ef128-ec5d-4f2d-9411-b55483301a80>
- ✓ **showroomprive.com** 117.51 EUR (conf. 0.87) — Both listings identify the SEB ClipsoMinut Gourmande 7.5L autocooker. <https://www.showroomprive.com/market/catalog/productp.aspx?produit=m-10691928>
- rejected at verify: but.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: brico-travo.com — Page not found (HTTP 404) — the product may have been removed.
- rejected at verify: carrefour.fr — The AI-read price could not be verified against the page text.

## fr-ordinary-serum — Cosmetics in an online pharmacy, EAN

- Page: https://www.redcare-pharmacie.fr/beaute/BE04657888/the-ordinary-niacinamide-10-zinc-1.htm
- Read: THE ORDINARY Niacinamide 10% + Zinc 1% · brand The Ordinary. · GTIN 0769915195941 · MPN BE003370 · 5.69 EUR · market france
- Status: completed
- Attempts: 2 · queries: The Ordinary Niacinamide 10% + Zinc 1% 30 ml; 769915195941; The Ordinary Niacinamide 10% Zinc 1% acheter France; 0769915195941; The Ordinary Niacinamide 10% Zinc 1% 60 ml France; The Ordinary sérum niacinamide zinc grand format 60 ml acheter; The Ordinary Niacinamide 10% + Zinc 1% 60 ml 769915195941
- Retailers guessed: sephora.fr, notino.fr, nocibe.fr, easypara.fr, cocooncenter.com, lookfantastic.fr, pharmacieeurope.com, marionnaud.fr, carrefour.fr, auchan.fr, monoprix.fr, galerieslafayette.com, pharmacie-monaco.com, pharmacie-prado-mermoz.com, pharmacie-des-drakkars.com, pharma-gdd.com, parapharmacie-en-ligne.com, greenweez.com
- Screened 53 pages, kept 5
- ✓ **marionnaud.fr** 6.00 EUR (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.marionnaud.fr/soin-visage/purifiant-et-matifiant/anti-imperfections-niacinamide-10-zinc-1-the-ordinary/p/BP_102671260>
- ✓ **theordinary.com** 6.00 EUR (conf. 0.94) — The product name matches The Ordinary Niacinamide 10% + Zinc 1%; the listing’s MPN indicates the EU 30 ml variant, with no conflicting variant details. <https://theordinary.com/fr-fr/niacinamide-10-zinc-1-serum-100436.html>
- rejected at verify: sephora.fr — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: notino.fr — Different EAN/GTIN (769915195958 vs 0769915195941).
- rejected at verify: galerieslafayette.com — This doesn't look like a single product page.

## nl-philips-airfryer — Appliance, no EAN in the page data, possibly discontinued

- Page: https://www.coolblue.nl/en/product/878234/philips-airfryer-l-hd9252-70.html
- Read: Philips Airfryer L HD9252/70 · brand Philips · GTIN None · MPN None · 99.00 EUR · market netherlands
- Status: completed
- Attempts: 2 · queries: Philips Airfryer L HD9252/70 kopen; Philips HD9252/70 airfryer; Philips HD9252/70; Philips HD9252/70 Airfryer L bestellen; Philips HD9252/70 heteluchtfriteuse; Philips HD9252/70 friteuse aanbieding
- Retailers guessed: bol.com, mediamarkt.nl, wehkamp.nl, expert.nl, blokker.nl, fonq.nl, artandcraft.com, vandenborre.be, electroworld.nl, handyman.nl, maxict.nl, alternate.nl, kookwinkel.nl, keukenloods.nl, ep.nl, bemmel-kroon.nl, hellotv.nl
- Screened 39 pages, kept 1
- rejected at verify: joybuy.nl — This doesn't look like a single product page.

## pl-logitech-mouse — Electronics, EAN, currency PLN

- Page: https://mediamarkt.pl/pl/product/_mysz-logitech-mx-master-3s-bluetooth-edition-grafitowy-1497571.html
- Read: Mysz LOGITECH MX Master 3S "SE" Bluetooth Edition Grafitowy · brand LOGITECH · GTIN 5099206129382 · MPN None · 319.99 PLN · market poland
- Status: completed
- Attempts: 1 · queries: Logitech MX Master 3S SE Bluetooth Edition grafitowy; 5099206129382; Logitech MX Master 3S Bluetooth Edition grafitowy cena
- Retailers guessed: x-kom.pl, morele.net, euro.com.pl, komputronik.pl, oleole.pl, mediaexpert.pl, proshop.pl, al.to
- Screened 28 pages, kept 7
- ✓ **morele.net** 319.00 PLN (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.morele.net/mysz-logitech-mx-master-3s-bluetooth-edition-graphite-910-007501-15520069/>
- ✓ **komputronik.pl** 340.00 PLN (conf. 0.99) — Same EAN/GTIN code on both pages. <https://www.komputronik.pl/product/984087/myszka-logitech-mx-master-3s-se-grafitowy.html>
- rejected at verify: mediaexpert.pl — This doesn't look like a single product page.
- rejected at verify: euro.com.pl — No price found on the page.
- rejected at verify: oleole.pl — This doesn't look like a single product page.
- rejected at verify: x-kom.pl — Couldn't load the page: HTTP 403; the backup reader (Tavily) was blocked too.
- rejected at verify: al.to — No price found on the page.
