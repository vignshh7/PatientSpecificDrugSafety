# Synthetic "biomedical literature" evidence entries.
#
# Modeled on how a PubMed search result / abstract would be represented after
# ingestion (pmid, title, year, journal, finding, relevance tags) and on
# well-established, publicly documented clinical findings for each drug.
# These are paraphrased summaries of general/consensus knowledge, NOT scraped
# PubMed abstracts and NOT real article identifiers. They exist to give the
# retrieval layer a second, lower-priority evidence tier (per evidence
# hierarchy: label > literature) alongside the drug label corpus.

LITERATURE = [
    # --- metformin ---
    {
        "pmid": "SYN10001",
        "drug_id": "metformin",
        "title": "Metformin-associated lactic acidosis risk across renal function strata",
        "year": 2019,
        "journal": "Synthetic Clinical Pharmacology Review",
        "finding": (
            "Pooled case-series data show metformin-associated lactic acidosis is rare but "
            "clusters strongly in patients with eGFR under 30 mL/min/1.73m2, acute illness, "
            "or recent contrast exposure; risk in patients with normal renal function is "
            "very low."
        ),
        "relevance_tags": ["renal_impairment", "elderly"],
    },
    {
        "pmid": "SYN10002",
        "drug_id": "metformin",
        "title": "Vitamin B12 deficiency with long-term metformin therapy",
        "year": 2016,
        "journal": "Synthetic Diabetes Care Letters",
        "finding": (
            "Long-term metformin use (over 4 years) was associated with a measurable "
            "reduction in serum B12 levels in a longitudinal cohort; periodic B12 testing "
            "was suggested for patients on chronic therapy."
        ),
        "relevance_tags": ["chronic_use"],
    },
    # --- lisinopril ---
    {
        "pmid": "SYN10003",
        "drug_id": "lisinopril",
        "title": "Hyperkalemia incidence with ACE inhibitor use in chronic kidney disease",
        "year": 2020,
        "journal": "Synthetic Nephrology Reports",
        "finding": (
            "ACE inhibitor initiation in patients with CKD stage 3b or worse showed "
            "significantly higher rates of clinically relevant hyperkalemia within 90 days "
            "compared with patients with preserved renal function, particularly when "
            "combined with potassium-sparing diuretics."
        ),
        "relevance_tags": ["renal_impairment", "interactions"],
    },
    {
        "pmid": "SYN10004",
        "drug_id": "lisinopril",
        "title": "Angioedema risk factors with ACE inhibitor therapy",
        "year": 2018,
        "journal": "Synthetic Allergy & Immunology Notes",
        "finding": (
            "A retrospective review found Black race, prior drug-induced angioedema, and "
            "concomitant mTOR-inhibitor use were associated with higher angioedema incidence "
            "during ACE inhibitor therapy."
        ),
        "relevance_tags": ["allergy"],
    },
    # --- atorvastatin ---
    {
        "pmid": "SYN10005",
        "drug_id": "atorvastatin",
        "title": "Statin-associated myopathy risk in elderly patients with polypharmacy",
        "year": 2021,
        "journal": "Synthetic Geriatric Pharmacotherapy Journal",
        "finding": (
            "Among patients over 75 on five or more medications, statin-associated muscle "
            "symptoms were reported more frequently than in younger, less polypharmacy-"
            "exposed cohorts, with CYP3A4-interacting co-medications a major contributing "
            "factor."
        ),
        "relevance_tags": ["elderly", "interactions"],
    },
    {
        "pmid": "SYN10006",
        "drug_id": "atorvastatin",
        "title": "Hepatic transaminase elevation patterns during statin therapy",
        "year": 2017,
        "journal": "Synthetic Hepatology Bulletin",
        "finding": (
            "Persistent transaminase elevation above three times the upper limit of normal "
            "was uncommon overall but occurred more often in patients with pre-existing "
            "hepatic disease or concomitant hepatotoxic medication exposure."
        ),
        "relevance_tags": ["hepatic_impairment"],
    },
    # --- warfarin ---
    {
        "pmid": "SYN10007",
        "drug_id": "warfarin",
        "title": "Bleeding risk stratification for warfarin therapy in older adults",
        "year": 2015,
        "journal": "Synthetic Thrombosis & Hemostasis Digest",
        "finding": (
            "A validated bleeding-risk score identified age over 65, prior GI bleed, renal "
            "impairment, and concomitant antiplatelet therapy as the strongest independent "
            "predictors of major hemorrhage on warfarin."
        ),
        "relevance_tags": ["elderly", "renal_impairment", "interactions"],
    },
    {
        "pmid": "SYN10008",
        "drug_id": "warfarin",
        "title": "Hepatic impairment and warfarin dose requirements",
        "year": 2014,
        "journal": "Synthetic Clinical Hepatology Reports",
        "finding": (
            "Patients with Child-Pugh B/C hepatic impairment required substantially lower "
            "warfarin maintenance doses to achieve therapeutic INR, reflecting reduced "
            "clotting factor synthesis and drug clearance."
        ),
        "relevance_tags": ["hepatic_impairment"],
    },
    # --- ibuprofen ---
    {
        "pmid": "SYN10009",
        "drug_id": "ibuprofen",
        "title": "NSAID-associated acute kidney injury with concomitant ACE inhibitor and diuretic use",
        "year": 2019,
        "journal": "Synthetic Renal Medicine Review",
        "finding": (
            "The combination of NSAID, ACE inhibitor/ARB, and diuretic ('triple whammy') was "
            "associated with a markedly elevated odds ratio for acute kidney injury compared "
            "with any two of the three classes alone."
        ),
        "relevance_tags": ["renal_impairment", "interactions", "elderly"],
    },
    {
        "pmid": "SYN10010",
        "drug_id": "ibuprofen",
        "title": "Cardiovascular thrombotic risk with short-term NSAID exposure",
        "year": 2020,
        "journal": "Synthetic Cardiology Outcomes Journal",
        "finding": (
            "Even short courses of nonselective NSAIDs were associated with a small but "
            "measurable increase in cardiovascular thrombotic events in patients with "
            "pre-existing cardiovascular disease."
        ),
        "relevance_tags": ["cardiovascular"],
    },
    # --- amoxicillin ---
    {
        "pmid": "SYN10011",
        "drug_id": "amoxicillin",
        "title": "Beta-lactam allergy labeling and cross-reactivity reassessment",
        "year": 2022,
        "journal": "Synthetic Clinical Allergy Reports",
        "finding": (
            "Formal allergy evaluation reclassified a large proportion of patients labeled "
            "'penicillin allergic' as tolerant, but patients with a history of anaphylaxis or "
            "Stevens-Johnson syndrome retained a contraindication to re-exposure without "
            "specialist evaluation."
        ),
        "relevance_tags": ["allergy"],
    },
    {
        "pmid": "SYN10012",
        "drug_id": "amoxicillin",
        "title": "Amoxicillin dosing in renal impairment: a pharmacokinetic analysis",
        "year": 2013,
        "journal": "Synthetic Antimicrobial Pharmacokinetics Journal",
        "finding": (
            "Amoxicillin half-life increased substantially as eGFR fell below 30 mL/min/"
            "1.73m2, supporting extended dosing intervals in that population to avoid "
            "accumulation."
        ),
        "relevance_tags": ["renal_impairment"],
    },
    # --- digoxin ---
    {
        "pmid": "SYN10013",
        "drug_id": "digoxin",
        "title": "Digoxin toxicity predictors in elderly patients with reduced renal function",
        "year": 2017,
        "journal": "Synthetic Cardiac Pharmacotherapy Review",
        "finding": (
            "Serum digoxin concentrations above the therapeutic range were disproportionately "
            "observed in elderly patients with eGFR under 45 mL/min/1.73m2 who were not dose-"
            "adjusted after renal function decline."
        ),
        "relevance_tags": ["renal_impairment", "elderly"],
    },
    {
        "pmid": "SYN10014",
        "drug_id": "digoxin",
        "title": "Electrolyte disturbance and digoxin arrhythmia risk",
        "year": 2012,
        "journal": "Synthetic Electrophysiology Notes",
        "finding": (
            "Hypokalemia and hypomagnesemia, often diuretic-induced, substantially increased "
            "the risk of digoxin-related arrhythmia even at serum digoxin levels within the "
            "nominal therapeutic range."
        ),
        "relevance_tags": ["interactions"],
    },
    # --- metoprolol ---
    {
        "pmid": "SYN10015",
        "drug_id": "metoprolol",
        "title": "Hepatic clearance variability of metoprolol and dosing implications",
        "year": 2016,
        "journal": "Synthetic Clinical Pharmacokinetics Bulletin",
        "finding": (
            "Patients with cirrhosis showed substantially higher metoprolol plasma "
            "concentrations at standard doses, consistent with reduced first-pass hepatic "
            "metabolism, supporting conservative dosing in hepatic impairment."
        ),
        "relevance_tags": ["hepatic_impairment"],
    },
    {
        "pmid": "SYN10016",
        "drug_id": "metoprolol",
        "title": "Beta-blocker discontinuation syndrome: incidence and prevention",
        "year": 2011,
        "journal": "Synthetic Cardiology Safety Review",
        "finding": (
            "Abrupt beta-blocker discontinuation was associated with rebound tachycardia and "
            "angina exacerbation; a tapering schedule over 1-2 weeks substantially reduced "
            "these events."
        ),
        "relevance_tags": ["chronic_use"],
    },
    # --- gabapentin ---
    {
        "pmid": "SYN10017",
        "drug_id": "gabapentin",
        "title": "Gabapentin accumulation and sedation risk in chronic kidney disease",
        "year": 2018,
        "journal": "Synthetic Nephro-Pharmacology Journal",
        "finding": (
            "Patients with eGFR under 30 mL/min/1.73m2 who received standard gabapentin "
            "doses showed significantly elevated plasma concentrations and higher rates of "
            "sedation and ataxia compared with dose-adjusted patients."
        ),
        "relevance_tags": ["renal_impairment", "elderly"],
    },
    {
        "pmid": "SYN10018",
        "drug_id": "gabapentin",
        "title": "Concomitant opioid-gabapentinoid use and respiratory depression risk",
        "year": 2021,
        "journal": "Synthetic Pain Medicine Safety Letters",
        "finding": (
            "Concomitant opioid and gabapentinoid prescribing was associated with an "
            "increased risk of opioid-related respiratory depression and death compared with "
            "opioid use alone in a large claims-based cohort."
        ),
        "relevance_tags": ["interactions"],
    },
    # --- sertraline ---
    {
        "pmid": "SYN10019",
        "drug_id": "sertraline",
        "title": "SSRI-associated upper gastrointestinal bleeding risk with concomitant NSAID use",
        "year": 2015,
        "journal": "Synthetic Psychopharmacology & Safety Journal",
        "finding": (
            "Concomitant SSRI and NSAID use was associated with a significantly higher "
            "relative risk of upper GI bleeding compared with either drug class alone, "
            "attributed to additive antiplatelet-like effects."
        ),
        "relevance_tags": ["interactions"],
    },
    {
        "pmid": "SYN10020",
        "drug_id": "sertraline",
        "title": "Hyponatremia incidence with SSRI therapy in older adults",
        "year": 2019,
        "journal": "Synthetic Geriatric Psychiatry Review",
        "finding": (
            "SIADH-related hyponatremia during SSRI therapy occurred predominantly in "
            "patients over 65, especially within the first month of treatment and when "
            "combined with thiazide diuretics."
        ),
        "relevance_tags": ["elderly", "interactions"],
    },
    # --- omeprazole ---
    {
        "pmid": "SYN10021",
        "drug_id": "omeprazole",
        "title": "Long-term proton pump inhibitor use and fracture risk",
        "year": 2014,
        "journal": "Synthetic Bone & Mineral Research Letters",
        "finding": (
            "Long-term PPI use (greater than 1 year) was associated with a modest but "
            "statistically significant increase in hip fracture risk, particularly in "
            "postmenopausal women and elderly patients."
        ),
        "relevance_tags": ["chronic_use", "elderly"],
    },
    {
        "pmid": "SYN10022",
        "drug_id": "omeprazole",
        "title": "Omeprazole-clopidogrel interaction and cardiovascular outcomes",
        "year": 2010,
        "journal": "Synthetic Cardiology Pharmacology Digest",
        "finding": (
            "Concomitant omeprazole use reduced clopidogrel active metabolite formation via "
            "CYP2C19 inhibition; observational data suggested a possible association with "
            "reduced antiplatelet effectiveness, though causality remained debated."
        ),
        "relevance_tags": ["interactions", "cardiovascular"],
    },
    # --- insulin glargine ---
    {
        "pmid": "SYN10023",
        "drug_id": "insulin_glargine",
        "title": "Hypoglycemia risk with basal insulin in renal impairment",
        "year": 2018,
        "journal": "Synthetic Endocrine Pharmacotherapy Review",
        "finding": (
            "Patients with eGFR under 45 mL/min/1.73m2 on fixed-dose basal insulin regimens "
            "experienced significantly more hypoglycemic events than those with preserved "
            "renal function, consistent with reduced insulin clearance."
        ),
        "relevance_tags": ["renal_impairment"],
    },
    {
        "pmid": "SYN10024",
        "drug_id": "insulin_glargine",
        "title": "Insulin dose adjustment needs across hepatic function strata",
        "year": 2016,
        "journal": "Synthetic Hepato-Endocrinology Bulletin",
        "finding": (
            "Patients with significant hepatic impairment required dose reductions of 20-30% "
            "on average to avoid hypoglycemia, attributed to reduced hepatic gluconeogenesis "
            "and insulin clearance."
        ),
        "relevance_tags": ["hepatic_impairment"],
    },
]
