# Introduction and Related Work: motivacija, namen, raziskovalna vprašanja

1. Introduction

Word order is a central typological feature that shapes the syntactic and pragmatic organization of language. The arrangement of subject (S), verb (V), and object (O) plays a crucial role in sentence structure and cross-linguistic variation. The World Atlas of Language Structures (WALS) identifies SVO as the most frequent dominant word order across the world’s languages, followed by SOV and VSO. However, while these classifications offer a broad overview of syntactic typology, they often reflect idealized or canonical forms found in written registers, leaving open the question of how much variation exists in actual usage—especially in spoken language.

This article explores word order variation across both spoken and written corpora in three typologically diverse languages—Slovenian, French, and English. Using the Universal Dependencies (UD) treebanks as empirical data sources, we investigate how SVO and alternative word orders manifest in different modalities, and to what extent spoken language deviates from the dominant typological patterns identified in WALS. Our aim is to assess whether spoken corpora exhibit more flexibility, reduced standardization, or pragmatic reordering not captured in written texts.

The study is guided by the following research questions:

How does word order vary between spoken and written corpora within Slovenian, French, and English?

Are non-canonical orders (e.g., OSV, VOS) more prevalent or functionally motivated in spoken discourse?

How do these patterns align with or challenge the dominant word order typologies defined by WALS?

By examining real usage data across modalities and languages, this study seeks to offer new insights into the interaction between typology, modality, and syntactic variation.

2. Related Work

Research on word order typology traditionally classifies languages by dominant SVO, SOV, or VSO patterns, as documented in WALS (WORDORDERTYPOLOGYANDLANGUAGEUNIVERSALS.pdf; P15-2034.pdf). However, recent corpus-based studies have emphasized that these dominant types often mask significant variation. Many languages exhibit gradient or probabilistic preferences rather than fixed rules, with word order shaped by information structure, morphology, and genre (Token-based typology and word order entropy A study based on Universal Dependencies.pdf; ecp18155010.pdf; syntaxfest.RediscoveringGreenbergsWordOrderUniversalsinUD.pdf).

Large-scale studies using Universal Dependencies (UD) corpora have confirmed known typological tendencies while also revealing their limitations. For example, quantitative investigations show that morphologically rich and syntactically flexible languages tend to display higher word order entropy, particularly in oblique, adverbial, and adjunct positions (Token-based typology and word order entropy A study based on Universal Dependencies.pdf). Studies have also observed that head-directionality is not categorical, and that most languages show both head-initial and head-final patterns to some degree (1-s2.0-S0024384109002137-main.pdf; L18-1719.pdf; 2023.depling-1.7.pdf).

Several multilingual analyses using UD and alignment-based methods have shown high overlap with WALS classifications, but also highlight discrepancies in languages where annotation inconsistencies, translation effects, or corpus composition distort the observed patterns (P15-2034.pdf; 2023.udw-1.5.pdf; 2021.ranlp-1.33.pdf). Dominant word order can vary within a single language depending on genre, register, and text type (2021.quasy-1.3.pdf; 10.1515_lingvan-2021-0001.pdf).

While most typological research has focused on written texts, a few studies acknowledge that spoken corpora introduce different structural tendencies. Spoken data often contains more fragments, disfluencies, and pragmatically-driven reorderings, while written language more consistently reflects standardized syntax (pgk31ssgzbx.pdf; 2021.quasy-1.3.pdf). Some findings even suggest that written language, especially in formal contexts, permits more marked word order patterns for discourse purposes, while speech relies more heavily on prosody to convey focus (pgk31ssgzbx.pdf).

Despite these observations, modality is rarely a primary variable in typological comparison. Spoken data is often included without differentiation, or only briefly acknowledged as a potential source of inconsistency (2021.ranlp-1.33.pdf; 2021.quasy-1.3.pdf). Existing studies have not yet systematically compared spoken and written corpora across multiple languages to assess the impact of modality on dominant and alternative word orders.

This study addresses that gap by analyzing spoken and written corpora in three typologically distinct languages—Slovenian, French, and English—using UD treebanks. Anchored in WALS typology, it investigates the distribution of SVO and alternative word orders across modalities, offering a new perspective on how syntactic patterns shift between speech and writing in real usage.

--

Choi et al. (2021) studied dominant word order in Slovenian using Universal Dependencies (UD) corpora. They found that Slovenian typically follows an SVO (Subject-Verb-Object) order in its standard or written form, while spoken language shows more variability, resulting in a classification of no dominant order (NDO). However, their study did not directly compare the written and spoken Slovenian corpora. These findings thus form the basis for our research, which aims to explore how word order varies between spoken and written Slovenian and whether the variability in spoken language reveals distinct patterns.  change so it won’t be limited to Slovenian

- Data and Methods:

- Izbor in priprava korpusov

6 languages, French, English, Slovenian, Norwegian (Bokmal and Nynorsk), Spanish

2 modalities, written and spoken

Corpora chosen based on 2 criteria: corpus size and representativeness of different genres

Corpora: UD latest version (v2.15), French: Rhapsodie (spoken) and GSD (written), English: GUM which we broke into 2 parts based on predefined criteria, Slovenian: SST (spoken), SSJ (written). Spanish:  GSD (written), COSER (spoken), Norwegian nynorsk: NynorskLIA (spoken), Nynorsk (written), Norwegian bokmal: Bokmaal (written and here only written one exists).

GUM splitting:

The GUM corpus was split into spoken and written categories based on several classification criteria.

Classification Criteria:

Genre-based classification: Documents with genres associated with speech, such as court, interview, conversation, dialogue, speech, podcast, and vlog, were categorized as spoken.

Speaker count: Documents with one or more speakers (speakerCount > 0) were classified as spoken, unless the genre was fiction or letter, in which case they were manually checked and classified as written. Others were classified as written.

GUM Statistics Summary:

Genre and document counts:

Spoken genres: conversation (14 documents), court (6), interview (19), podcast (5), speech (15), and vlog (15).

Written genres: academic (18), bio (20), essay (5), fiction (19), letter (6), news (23), textbook (15), voyage (18), whow (19).

File statistics: The whole corpus contains a total of 217 documents.

Spoken: 74 documents (4766 paragraphs, 5653 sentences).

Written: 143 documents (5114 paragraphs, 6493 sentences).

Token Statistics:

Tokens are defined as lines beginning with a numeric character (digits).

Spoken: 83359 tokens.

Written: 132265 tokens.

All these stats probably not that important because they’re only for GUM, but maybe add link to the split GUM?

Add footnote about UD-Multigenre and GUM and that we chose more metadata for spoken

We conducted quantitative research using the tool STARK.

Syntactic patterns were extracted from the corpora using the STARK tool, a specialized program designed for forming UD-based dependency trees. The following query was used to extract examples of verbal constructions with nominal subjects and objects:

query = upos=VERB >nsubj _ >obj _

complete=no

This query identifies all verbs (upos=VERB) that govern nominal subjects (nsubj) and direct objects (obj). The output from the STARK tool was: SVO, SOV, VSO, OSV, OVS, or VOS  maybe add some additional STARK configuration? Or not

Q: je ok, da iz analize izpuščamo tudi primere, kjer nista izražena oba argumenta (npr. stavki z nsubj in brez obj ter obratno) – v jezikih, kot je slovenščina, lahko namreč osebek izražamo tudi morfološko (Kupila je jabolka vs. Ona je kupila jabolka).  A: ja, za samo analizo WALS lastnosti je ok, če se izpušča to dvoje (v opisu je namreč navedeno, da se zemljevid in z njim podatki navezujejo samo na tranzitivne stavke – deklarativne stavke, kjer tako osebek kot predmet vsebujeta samostalnik).

- Luščenje podatkov

3.       Results:

3.1 Splošne ugotovitve

3.2 Analiza po jezikih

kolikšen je delež VO brez S (se pravi je S izražen na druge možne načine, npr. morfološko, kot v Kupila je jabolko.).  Bi bilo zanimivo videti, ali so tukaj kakšne razlike.  primerjati podatke VSO in VS, kako točno?

Comparison with WALS?

Limitations

Only 6 languages, indo-european, biased (like many of previous papers). Could expand the research to other languages that have both spoken and written treebanks (representative).

4.       Diskusija / zaključek
