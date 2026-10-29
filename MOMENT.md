# MOMENT.md

## The moment

It is 04:10 on the four-to-eight watch in the Arabian Sea. Arjun Menon, Second Officer on a product tanker, has a twenty minute internet window each day. His manning agent has offered a six month contract starting 1 February. His medical fitness certificate expires 14 March. He does not know that tonight, and he would find out at the agency desk, where the job would go to someone else.

Dogwatch computes it from his own certificates, on his own machine, and answers inside his window: not ready, the medical lapses on day 42 of 181, book it before joining, and a packet for the agent is ready to approve.

## What is true / Source / Retrieved

| What is true | Source | Retrieved |
|---|---|---|
| The 2021 BIMCO/ICS report counted a current shortfall of 26,240 STCW certified officers. | Joint press release, read on a trade-press reprint because the ICS and BIMCO pages refuse automated access. [reprint](https://www.hellenicshippingnews.com/?p=880386), [ICS page](https://www.ics-shipping.org/?p=12692) | 2026-10-28 |
| About 1.89 million seafarers serve the world merchant fleet (same report). | Same reprint | 2026-10-28 |
| Certificates required by the Convention must be carried in original form on board. | [AMSA Marine Notice 2025/05](https://www.amsa.gov.au/sites/default/files/2025-05-Marine-notice-revalidation-Australian-STCW-certificates.pdf) | 2026-10-28 |
| STCW certificates are revalidated at intervals not exceeding five years. | [IMO STCW supplement, April 2017, Regulation I/11](https://law.resource.org/pub/us/cfr/ibr/inc/imo/imo.stcw.supp.2017.pdf) | 2026-10-28 |
| Australia: 360 days of sea service in the 5 years, or 90 days in the 6 months, before applying. Applications are best made in the 6 months before expiry. | [AMSA revalidation page](https://www.amsa.gov.au/qualifications-training/international-qualifications/revalidation-stcw-master-and-deck-certificates) | 2026-10-28 |
| UK: tanker endorsements need at least 3 months of approved service in the preceding 5 years. | [MCA MIN 494](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/945374/MIN_494.pdf) | 2026-10-28 |
| The ILO minimum monthly basic wage for an able seafarer is US$704 from 1 January 2027. A floor, not Arjun's wage. | [ILO news item](https://www.ilo.org/resource/news/subcommittee-wages-seafarers-reaches-agreement-increase-seafarer-minimum) | 2026-10-28 |

Money figure: a six month contract measured at the ILO floor is 6 x US$704 = US$4,224. `tests/test_sources.py` reads the 704 from `evidence/need/sources.json` and asserts the arithmetic.

## Not yet read from the source (so not used)

- India DG Shipping revalidation circulars: the host refused connections from the build machine.
- Singapore MPA Shipping Circular 3 of 2026: the page returned 404 to automated fetches.
- Paris MoU annual report deficiency tables: not fetched.

Until those are read, the India and Singapore packs hold no rules and the engine answers `ASK_ADMINISTRATION` for anything that needs them. `evidence/need/sources.json` lists each with its status.

## The founder stake

The builder is pursuing STCW certification. His own Basic Safety Training certificates are stored only on his machine, never committed, never shown.
