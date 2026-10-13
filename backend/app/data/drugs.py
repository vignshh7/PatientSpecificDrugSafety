# Synthetic demonstration evidence corpus.
#
# Modeled on the SECTION STRUCTURE of DailyMed / FDA Structured Product
# Labeling (indications, contraindications, warnings & precautions, adverse
# reactions, drug interactions, use in specific populations) and on
# well-established, publicly documented pharmacology facts for each drug.
#
# This is NOT scraped from DailyMed/PubMed and must not be presented as a
# live feed of those sources. It exists so the retrieval + generation
# pipeline has a controlled, citable, drug-specific evidence base to
# demonstrate patient-context retrieval behavior (per project rule: synthetic
# data demonstrates system functionality, not clinical effectiveness).

DRUGS = [
    {
        "drug_id": "metformin",
        "generic_name": "Metformin",
        "brand_names": ["Glucophage"],
        "drug_class": "Biguanide (antidiabetic)",
        "dailymed_setid": "056072d8-6228-4914-831d-ee7c0661b742",
        "sections": {
            "indications": (
                "Metformin is indicated as an adjunct to diet and exercise to improve "
                "glycemic control in adults and children with type 2 diabetes mellitus."
            ),
            "contraindications": (
                "Severe renal impairment (eGFR below 30 mL/min/1.73m2). Acute or chronic "
                "metabolic acidosis, including diabetic ketoacidosis. Known hypersensitivity "
                "to metformin."
            ),
            "warnings_and_precautions": (
                "Lactic acidosis is a rare but serious metabolic complication that can occur "
                "due to metformin accumulation. Risk increases with renal impairment, "
                "concomitant use of certain drugs, age 65 or older, radiologic contrast "
                "studies, surgery, and conditions associated with hypoperfusion or hypoxemia. "
                "Assess renal function before starting and periodically thereafter."
            ),
            "adverse_reactions": (
                "Most common: diarrhea, nausea/vomiting, flatulence, asthenia, indigestion, "
                "abdominal discomfort, headache. Vitamin B12 deficiency may occur with "
                "long-term use."
            ),
            "drug_interactions": (
                "Carbonic anhydrase inhibitors may increase risk of lactic acidosis. "
                "Iodinated contrast media can acutely alter renal function and increase "
                "lactic acidosis risk if metformin is not withheld appropriately. Alcohol "
                "potentiates the effect of metformin on lactate metabolism."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Not recommended with eGFR below 30 mL/min/1.73m2. Dose reduction is "
                    "recommended when eGFR is 30-45 mL/min/1.73m2; re-assess risk/benefit. "
                    "Renal function should be monitored regularly."
                ),
                "hepatic_impairment": (
                    "Avoid use in patients with clinically evident hepatic disease; hepatic "
                    "impairment is associated with cases of lactic acidosis."
                ),
                "geriatric_use": (
                    "Metformin is known to be substantially excreted by the kidney, and the "
                    "risk of serious adverse reactions is greater in patients with impaired "
                    "renal function. Because age-related decline in renal function is common, "
                    "monitor renal function more frequently in elderly patients."
                ),
                "pregnancy": (
                    "Limited data; uncontrolled hyperglycemia in pregnancy is associated with "
                    "adverse outcomes and clinicians should weigh risks individually."
                ),
            },
            "dosage_considerations": (
                "Assess eGFR prior to initiation. Do not initiate in patients with eGFR below "
                "45 mL/min/1.73m2 without careful risk assessment. Withhold temporarily for "
                "iodinated contrast procedures in patients with reduced eGFR."
            ),
        },
    },
    {
        "drug_id": "lisinopril",
        "generic_name": "Lisinopril",
        "brand_names": ["Prinivil", "Zestril"],
        "drug_class": "ACE inhibitor",
        "dailymed_setid": "34ebeea1-6812-4697-84c4-b2ae4f39e55f",
        "sections": {
            "indications": (
                "Lisinopril is indicated for treatment of hypertension, heart failure, and to "
                "improve survival after acute myocardial infarction."
            ),
            "contraindications": (
                "History of angioedema related to previous ACE inhibitor treatment. "
                "Hereditary or idiopathic angioedema. Concomitant use with aliskiren in "
                "patients with diabetes. Pregnancy."
            ),
            "warnings_and_precautions": (
                "Angioedema of the face, extremities, lips, tongue, glottis and/or larynx can "
                "occur. Hyperkalemia may occur, particularly in patients with renal impairment, "
                "diabetes, or those taking potassium-sparing diuretics or potassium "
                "supplements. Hypotension can occur, especially in volume-depleted patients. "
                "Can cause fetal/neonatal morbidity and mortality when used in pregnancy."
            ),
            "adverse_reactions": (
                "Most common: dizziness, headache, cough, hyperkalemia, hypotension, "
                "diarrhea, fatigue. Rare: angioedema, acute renal failure."
            ),
            "drug_interactions": (
                "NSAIDs may reduce the antihypertensive effect and increase risk of renal "
                "impairment, particularly in volume-depleted or elderly patients. Potassium "
                "supplements, potassium-sparing diuretics, or potassium-containing salt "
                "substitutes increase hyperkalemia risk. Lithium levels may increase."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Patients with renal impairment may require lower doses. Monitor renal "
                    "function and potassium; dose adjustment is recommended based on "
                    "creatinine clearance."
                ),
                "hepatic_impairment": (
                    "No specific dose adjustment established; use with caution as hepatic "
                    "impairment is not well studied."
                ),
                "geriatric_use": (
                    "No overall differences in safety/effectiveness observed, but elderly "
                    "patients may have reduced renal function; monitor renal function and "
                    "potassium."
                ),
                "pregnancy": (
                    "Contraindicated. Drugs that act on the renin-angiotensin system can cause "
                    "fetal and neonatal injury, including death, when used in the second and "
                    "third trimesters."
                ),
            },
            "dosage_considerations": (
                "In patients with renal impairment, starting dose should be reduced based on "
                "creatinine clearance; titrate based on blood pressure response and renal "
                "function/potassium monitoring."
            ),
        },
    },
    {
        "drug_id": "atorvastatin",
        "generic_name": "Atorvastatin",
        "brand_names": ["Lipitor"],
        "drug_class": "HMG-CoA reductase inhibitor (statin)",
        "dailymed_setid": "10e766cc-c3fd-4584-a0d7-652c516e828c",
        "sections": {
            "indications": (
                "Atorvastatin is indicated as an adjunct to diet to reduce elevated LDL "
                "cholesterol and triglycerides, and to reduce risk of cardiovascular events "
                "in patients with multiple risk factors."
            ),
            "contraindications": (
                "Active liver disease, which may include unexplained persistent elevations of "
                "hepatic transaminases. Known hypersensitivity to atorvastatin. Pregnancy and "
                "nursing."
            ),
            "warnings_and_precautions": (
                "Rare cases of fatal and non-fatal rhabdomyolysis with acute renal failure "
                "have been reported. Risk is increased by advanced age, hypothyroidism, renal "
                "impairment, and concomitant use of certain interacting drugs. Liver enzyme "
                "abnormalities may occur; monitor liver function as clinically indicated."
            ),
            "adverse_reactions": (
                "Most common: nasopharyngitis, arthralgia, diarrhea, pain in extremity, "
                "urinary tract infection. Myalgia and elevated transaminases can occur."
            ),
            "drug_interactions": (
                "Strong CYP3A4 inhibitors (e.g., certain antifungals, protease inhibitors, "
                "clarithromycin) increase atorvastatin exposure and myopathy risk. Concomitant "
                "fibrates or niacin increase risk of myopathy/rhabdomyolysis. Grapefruit juice "
                "in large quantities can increase exposure."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "No dose adjustment is necessary for renal impairment, since renal disease "
                    "does not substantially affect atorvastatin pharmacokinetics; however, "
                    "renal impairment is a risk factor for myopathy and should raise monitoring "
                    "vigilance."
                ),
                "hepatic_impairment": (
                    "Contraindicated in active liver disease. Use with caution and monitor "
                    "liver enzymes in patients with a history of liver disease or substantial "
                    "alcohol consumption."
                ),
                "geriatric_use": (
                    "Advanced age (greater than 65) is a predisposing factor for myopathy; "
                    "monitor for muscle symptoms."
                ),
                "pregnancy": (
                    "Contraindicated. May cause fetal harm; cholesterol and cholesterol "
                    "biosynthesis are important for fetal development."
                ),
            },
            "dosage_considerations": (
                "No renal dose adjustment required. Use lowest necessary dose when combined "
                "with interacting drugs; monitor liver enzymes at initiation and as clinically "
                "indicated."
            ),
        },
    },
    {
        "drug_id": "warfarin",
        "generic_name": "Warfarin",
        "brand_names": ["Coumadin", "Jantoven"],
        "drug_class": "Vitamin K antagonist (anticoagulant)",
        "dailymed_setid": "cdbbc317-35d3-42ba-94f0-c83891358529",
        "sections": {
            "indications": (
                "Warfarin is indicated for prophylaxis and treatment of venous thrombosis and "
                "its extension, pulmonary embolism, and thromboembolic complications "
                "associated with atrial fibrillation and/or cardiac valve replacement."
            ),
            "contraindications": (
                "Pregnancy (except in patients with mechanical heart valves at high risk). "
                "Active pathological bleeding. Hemorrhagic tendencies. Recent or planned "
                "major surgery with high bleeding risk."
            ),
            "warnings_and_precautions": (
                "Warfarin can cause major or fatal bleeding. Regular monitoring of INR is "
                "required. Risk factors for bleeding include high-intensity anticoagulation, "
                "age 65 or older, variable INR, history of GI bleeding, hypertension, "
                "cerebrovascular disease, serious heart disease, anemia, renal insufficiency, "
                "concomitant drugs that affect hemostasis, and long duration of therapy."
            ),
            "adverse_reactions": (
                "Most common: bleeding (minor to major), including bruising, epistaxis, "
                "hematuria, and GI bleeding. Rare: skin necrosis, purple toe syndrome."
            ),
            "drug_interactions": (
                "Numerous clinically significant interactions. NSAIDs and antiplatelet drugs "
                "increase bleeding risk. Many antibiotics potentiate anticoagulant effect. "
                "Dietary vitamin K intake and many CYP2C9/CYP3A4-interacting drugs alter INR "
                "control."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Renal impairment can enhance anticoagulant response; monitor INR more "
                    "frequently and consider lower doses."
                ),
                "hepatic_impairment": (
                    "Hepatic impairment can potentiate the anticoagulant response via reduced "
                    "clotting factor synthesis and reduced warfarin clearance; monitor INR "
                    "closely and consider dose reduction."
                ),
                "geriatric_use": (
                    "Elderly patients may be more sensitive to anticoagulant effects; a lower "
                    "initiation dose and more frequent INR monitoring is recommended."
                ),
                "pregnancy": (
                    "Contraindicated in most cases; can cause fetal bleeding and birth defects."
                ),
            },
            "dosage_considerations": (
                "Individualize dosing based on INR response. Lower initiation doses are "
                "recommended for elderly, hepatically impaired, or renally impaired patients, "
                "or those at increased bleeding risk."
            ),
        },
    },
    {
        "drug_id": "ibuprofen",
        "generic_name": "Ibuprofen",
        "brand_names": ["Advil", "Motrin"],
        "drug_class": "NSAID",
        "dailymed_setid": "152b0c90-b0c3-4b1b-9e93-4b4c6b3118bd",
        "sections": {
            "indications": (
                "Ibuprofen is indicated for relief of mild to moderate pain, fever, and "
                "inflammatory conditions such as osteoarthritis and rheumatoid arthritis."
            ),
            "contraindications": (
                "History of asthma, urticaria, or allergic-type reaction after NSAID or "
                "aspirin use. Active GI bleeding or peptic ulcer disease. Use in the setting "
                "of CABG surgery. Severe renal impairment."
            ),
            "warnings_and_precautions": (
                "NSAIDs can cause an increased risk of serious cardiovascular thrombotic "
                "events, myocardial infarction, and stroke. Can cause serious GI adverse "
                "events including bleeding, ulceration, and perforation. Can cause acute "
                "kidney injury, especially in volume-depleted patients, the elderly, or those "
                "with pre-existing renal impairment or heart failure."
            ),
            "adverse_reactions": (
                "Most common: dyspepsia, nausea, heartburn, dizziness, rash. Can cause fluid "
                "retention and edema."
            ),
            "drug_interactions": (
                "Concomitant ACE inhibitors/ARBs and diuretics (the 'triple whammy') markedly "
                "increase acute kidney injury risk. Increases bleeding risk with anticoagulants "
                "and antiplatelet agents. May reduce the antihypertensive effect of several "
                "drug classes. Increases lithium and methotrexate levels."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Avoid use in patients with advanced renal impairment; NSAID-related acute "
                    "kidney injury risk is substantially higher in patients with reduced eGFR, "
                    "volume depletion, or concomitant renin-angiotensin system blockade."
                ),
                "hepatic_impairment": (
                    "Use with caution; NSAIDs have been associated with elevations of liver "
                    "enzymes and rare severe hepatic reactions."
                ),
                "geriatric_use": (
                    "Elderly patients are at greater risk for serious GI and renal adverse "
                    "events; use the lowest effective dose for the shortest duration."
                ),
                "pregnancy": (
                    "Avoid use starting at 20 weeks gestation and later, as NSAIDs can cause "
                    "fetal renal dysfunction; avoid at 30 weeks or later due to risk of "
                    "premature closure of the ductus arteriosus."
                ),
            },
            "dosage_considerations": (
                "Use lowest effective dose for shortest duration, particularly in patients "
                "with reduced eGFR, concomitant ACE inhibitor/ARB and diuretic use, or "
                "advanced age."
            ),
        },
    },
    {
        "drug_id": "amoxicillin",
        "generic_name": "Amoxicillin",
        "brand_names": ["Amoxil"],
        "drug_class": "Aminopenicillin antibiotic",
        "dailymed_setid": "61a9829b-4792-4caa-b75a-b84812f28d4a",
        "sections": {
            "indications": (
                "Amoxicillin is indicated for the treatment of susceptible bacterial "
                "infections including otitis media, sinusitis, respiratory tract infections, "
                "skin infections, and urinary tract infections."
            ),
            "contraindications": (
                "Known serious hypersensitivity (e.g., anaphylaxis, Stevens-Johnson syndrome) "
                "to amoxicillin, other penicillins, or beta-lactams."
            ),
            "warnings_and_precautions": (
                "Serious and occasionally fatal hypersensitivity (anaphylactic) reactions have "
                "occurred in patients on penicillin therapy. Clostridioides difficile-"
                "associated diarrhea has been reported with nearly all antibacterial agents."
            ),
            "adverse_reactions": (
                "Most common: diarrhea, nausea, vomiting, rash. Hypersensitivity reactions "
                "range from mild rash to anaphylaxis."
            ),
            "drug_interactions": (
                "Probenecid decreases renal excretion and increases amoxicillin levels. May "
                "reduce efficacy of estrogen-containing oral contraceptives in some patients."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Dose adjustment or extended dosing interval is recommended in patients "
                    "with marked renal impairment (eGFR below 30 mL/min/1.73m2), since "
                    "amoxicillin is primarily renally excreted."
                ),
                "hepatic_impairment": (
                    "No specific dose adjustment established; use with caution and monitor "
                    "liver function if treatment is prolonged."
                ),
                "geriatric_use": (
                    "No overall differences in safety/effectiveness, although age-related "
                    "renal impairment should be considered for dosing."
                ),
                "pregnancy": (
                    "Generally considered compatible with pregnancy when clinically indicated; "
                    "penicillins have a long history of use without documented teratogenicity."
                ),
            },
            "dosage_considerations": (
                "Reduce dose or extend interval in patients with eGFR below 30 mL/min/1.73m2. "
                "Always document known penicillin/beta-lactam allergy before prescribing."
            ),
        },
    },
    {
        "drug_id": "digoxin",
        "generic_name": "Digoxin",
        "brand_names": ["Lanoxin"],
        "drug_class": "Cardiac glycoside",
        "dailymed_setid": "dfac7f13-28be-423d-9389-9089da29da17",
        "sections": {
            "indications": (
                "Digoxin is indicated for the treatment of mild to moderate heart failure and "
                "for control of ventricular response rate in patients with chronic atrial "
                "fibrillation."
            ),
            "contraindications": (
                "Ventricular fibrillation. Known hypersensitivity to digoxin or other "
                "digitalis glycosides."
            ),
            "warnings_and_precautions": (
                "Digoxin toxicity can cause life-threatening arrhythmias; the toxic-to-"
                "therapeutic ratio is narrow. Risk of toxicity is increased by renal "
                "impairment (digoxin is primarily renally eliminated), hypokalemia, "
                "hypomagnesemia, hypercalcemia, hypothyroidism, and advanced age."
            ),
            "adverse_reactions": (
                "Most common: nausea, vomiting, anorexia, visual disturbances. Cardiac "
                "arrhythmias of many types can occur with toxicity."
            ),
            "drug_interactions": (
                "P-glycoprotein inhibitors (e.g., amiodarone, verapamil, clarithromycin) can "
                "significantly increase digoxin levels. Diuretics causing hypokalemia or "
                "hypomagnesemia increase toxicity risk."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Digoxin is predominantly eliminated renally; reduced eGFR substantially "
                    "increases serum digoxin levels and toxicity risk. Dose reduction and "
                    "serum level monitoring are recommended."
                ),
                "hepatic_impairment": (
                    "Hepatic impairment has minimal effect on digoxin pharmacokinetics since "
                    "elimination is primarily renal; no specific dose adjustment usually "
                    "required."
                ),
                "geriatric_use": (
                    "Elderly patients often have reduced renal function and lower lean body "
                    "mass, increasing susceptibility to toxicity; lower maintenance doses and "
                    "serum level monitoring are recommended."
                ),
                "pregnancy": (
                    "Use only if clearly needed; crosses the placenta, and pharmacokinetics "
                    "may change during pregnancy."
                ),
            },
            "dosage_considerations": (
                "Base maintenance dose on renal function (eGFR/creatinine) and body weight; "
                "monitor serum digoxin concentration and electrolytes, particularly potassium, "
                "in renally impaired or elderly patients."
            ),
        },
    },
    {
        "drug_id": "metoprolol",
        "generic_name": "Metoprolol",
        "brand_names": ["Lopressor", "Toprol-XL"],
        "drug_class": "Beta-1 selective adrenergic blocker",
        "dailymed_setid": "aec38606-2009-4933-b9d7-5031be85e898",
        "sections": {
            "indications": (
                "Metoprolol is indicated for treatment of hypertension, angina pectoris, "
                "stable chronic heart failure, and to reduce cardiovascular mortality after "
                "myocardial infarction."
            ),
            "contraindications": (
                "Severe bradycardia, sick sinus syndrome or second/third-degree AV block "
                "(without a pacemaker), decompensated heart failure, cardiogenic shock, severe "
                "peripheral arterial circulatory disorders."
            ),
            "warnings_and_precautions": (
                "Abrupt discontinuation can precipitate severe exacerbation of angina, "
                "myocardial infarction, or ventricular arrhythmias; taper gradually. May mask "
                "symptoms of hypoglycemia and worsen peripheral arterial disease. Can "
                "exacerbate bronchospastic disease."
            ),
            "adverse_reactions": (
                "Most common: fatigue, dizziness, bradycardia, hypotension, diarrhea, "
                "shortness of breath."
            ),
            "drug_interactions": (
                "Concomitant verapamil or diltiazem increases risk of bradycardia and AV "
                "block. CYP2D6 inhibitors can increase metoprolol exposure. May potentiate "
                "effects of other antihypertensives and bradycardic agents."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "No specific dose adjustment is generally required, as metoprolol is "
                    "primarily hepatically metabolized; however, monitor for excessive effect "
                    "in reduced renal clearance states with concomitant conditions."
                ),
                "hepatic_impairment": (
                    "Metoprolol undergoes extensive hepatic first-pass metabolism; hepatic "
                    "impairment can substantially increase plasma levels. Lower starting doses "
                    "and careful titration are recommended."
                ),
                "geriatric_use": (
                    "No overall differences in effectiveness, but elderly patients may be more "
                    "sensitive to bradycardic and hypotensive effects."
                ),
                "pregnancy": (
                    "May cause fetal/neonatal bradycardia and hypoglycemia; use only if "
                    "benefit justifies risk."
                ),
            },
            "dosage_considerations": (
                "Use lower starting doses and slower titration in hepatic impairment. Taper "
                "gradually over 1-2 weeks when discontinuing; do not stop abruptly."
            ),
        },
    },
    {
        "drug_id": "gabapentin",
        "generic_name": "Gabapentin",
        "brand_names": ["Neurontin"],
        "drug_class": "Anticonvulsant / neuropathic pain agent",
        "dailymed_setid": "3dac0d5f-6e65-4c58-9d2a-4f6910b2d4ef",
        "sections": {
            "indications": (
                "Gabapentin is indicated for management of postherpetic neuralgia and as "
                "adjunctive therapy for partial-onset seizures."
            ),
            "contraindications": (
                "Known hypersensitivity to gabapentin or its components."
            ),
            "warnings_and_precautions": (
                "Can cause CNS depression (somnolence, dizziness, ataxia), especially when "
                "combined with other CNS depressants such as opioids; concomitant opioid use "
                "has been associated with risk of respiratory depression. Risk of "
                "suicidal ideation (class-wide signal for antiepileptics)."
            ),
            "adverse_reactions": (
                "Most common: somnolence, dizziness, ataxia, fatigue, peripheral edema."
            ),
            "drug_interactions": (
                "Concomitant opioids increase risk of CNS and respiratory depression. "
                "Antacids containing aluminum/magnesium can reduce gabapentin bioavailability."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Gabapentin is eliminated almost entirely by renal excretion; dose must be "
                    "reduced in patients with reduced eGFR, and dosing adjustment is required "
                    "for patients on hemodialysis."
                ),
                "hepatic_impairment": (
                    "Not extensively metabolized by the liver; no specific dose adjustment is "
                    "generally required for hepatic impairment alone."
                ),
                "geriatric_use": (
                    "Elderly patients often have reduced renal clearance; lower maintenance "
                    "doses and slower titration are recommended, with increased risk of "
                    "somnolence and ataxia."
                ),
                "pregnancy": (
                    "Use only if the potential benefit justifies the potential risk to the "
                    "fetus; data are limited."
                ),
            },
            "dosage_considerations": (
                "Dose must be adjusted according to eGFR/creatinine clearance; renal "
                "impairment is the single most important dosing factor for this drug."
            ),
        },
    },
    {
        "drug_id": "sertraline",
        "generic_name": "Sertraline",
        "brand_names": ["Zoloft"],
        "drug_class": "SSRI (antidepressant)",
        "dailymed_setid": "b5e98b93-d8f8-4eed-8a0a-63b347b670ed",
        "sections": {
            "indications": (
                "Sertraline is indicated for treatment of major depressive disorder, "
                "obsessive-compulsive disorder, panic disorder, PTSD, and social anxiety "
                "disorder."
            ),
            "contraindications": (
                "Concomitant use with monoamine oxidase inhibitors (MAOIs) or within 14 days "
                "of stopping an MAOI. Concomitant use with pimozide."
            ),
            "warnings_and_precautions": (
                "Increased risk of suicidal thinking and behavior in children, adolescents, "
                "and young adults. Risk of serotonin syndrome, particularly with other "
                "serotonergic drugs. Can increase bleeding risk, especially when combined with "
                "NSAIDs, aspirin, or anticoagulants. Hyponatremia has been reported, "
                "particularly in elderly patients."
            ),
            "adverse_reactions": (
                "Most common: nausea, diarrhea, insomnia, dry mouth, somnolence, dizziness, "
                "sexual dysfunction."
            ),
            "drug_interactions": (
                "Increases bleeding risk when combined with NSAIDs, antiplatelet agents, or "
                "anticoagulants (including warfarin) via antiplatelet effects and potential "
                "pharmacokinetic interaction. Serotonergic drugs increase serotonin syndrome "
                "risk."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "No substantial dose adjustment required for mild-moderate renal "
                    "impairment; use with caution in severe impairment due to limited data."
                ),
                "hepatic_impairment": (
                    "Clearance is reduced in hepatic impairment; a lower dose or reduced "
                    "frequency is recommended, and sertraline should be used with caution."
                ),
                "geriatric_use": (
                    "Increased risk of hyponatremia (SIADH) in elderly patients; monitor "
                    "sodium, particularly when combined with diuretics."
                ),
                "pregnancy": (
                    "Use requires individualized risk-benefit assessment; untreated depression "
                    "itself carries risk, and neonatal effects have been reported with "
                    "third-trimester SSRI exposure."
                ),
            },
            "dosage_considerations": (
                "Reduce dose/frequency in hepatic impairment. Use caution with concomitant "
                "anticoagulants/antiplatelets/NSAIDs due to additive bleeding risk."
            ),
        },
    },
    {
        "drug_id": "omeprazole",
        "generic_name": "Omeprazole",
        "brand_names": ["Prilosec"],
        "drug_class": "Proton pump inhibitor",
        "dailymed_setid": "c5e3a37a-f6e3-43d4-a8a9-54db6c271908",
        "sections": {
            "indications": (
                "Omeprazole is indicated for treatment of GERD, erosive esophagitis, duodenal "
                "and gastric ulcers, and in combination regimens for H. pylori eradication."
            ),
            "contraindications": (
                "Known hypersensitivity to omeprazole or substituted benzimidazoles. "
                "Concomitant use with rilpivirine-containing products."
            ),
            "warnings_and_precautions": (
                "Long-term use has been associated with increased risk of bone fracture, "
                "Clostridioides difficile-associated diarrhea, vitamin B12 deficiency, "
                "hypomagnesemia, and cutaneous/systemic lupus erythematosus. May mask "
                "symptoms of gastric malignancy."
            ),
            "adverse_reactions": (
                "Most common: headache, abdominal pain, nausea, diarrhea, vomiting, "
                "flatulence."
            ),
            "drug_interactions": (
                "Reduces absorption of drugs requiring acidic gastric pH (e.g., certain "
                "antifungals). Can increase clopidogrel inactive metabolite formation, "
                "potentially reducing clopidogrel's antiplatelet effect. Increases levels of "
                "methotrexate in some regimens."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "No dose adjustment is generally necessary for renal impairment."
                ),
                "hepatic_impairment": (
                    "Clearance is reduced in significant hepatic impairment; dose reduction "
                    "or lower maintenance dosing should be considered for long-term therapy."
                ),
                "geriatric_use": (
                    "No overall dose adjustment required based on age alone, but long-term "
                    "fracture and deficiency risks are more clinically relevant in elderly "
                    "patients."
                ),
                "pregnancy": (
                    "Available data have not shown an increased risk of major birth defects; "
                    "use when clinically indicated."
                ),
            },
            "dosage_considerations": (
                "Consider dose reduction for long-term therapy in hepatic impairment. Use the "
                "lowest effective dose for the shortest duration consistent with the condition "
                "being treated, especially in elderly patients, given long-term fracture and "
                "deficiency risks."
            ),
        },
    },
    {
        "drug_id": "insulin_glargine",
        "generic_name": "Insulin glargine",
        "brand_names": ["Lantus", "Basaglar"],
        "drug_class": "Long-acting basal insulin analog",
        "dailymed_setid": "3ac85ebb-5594-59c8-77fd-df254329d151",
        "sections": {
            "indications": (
                "Insulin glargine is indicated to improve glycemic control in adults and "
                "children with type 1 or type 2 diabetes mellitus."
            ),
            "contraindications": (
                "During episodes of hypoglycemia. Known hypersensitivity to insulin glargine "
                "or its excipients."
            ),
            "warnings_and_precautions": (
                "Hypoglycemia is the most common adverse reaction and can be life-threatening. "
                "Risk is increased by renal or hepatic impairment, changes in physical "
                "activity, meal patterns, or concomitant medications. Never share insulin pens "
                "between patients."
            ),
            "adverse_reactions": (
                "Most common: hypoglycemia, injection site reactions, lipodystrophy, weight "
                "gain, edema."
            ),
            "drug_interactions": (
                "Beta-blockers may mask symptoms of hypoglycemia. Many oral antidiabetic "
                "agents, ACE inhibitors, and alcohol can potentiate glucose-lowering effects "
                "and hypoglycemia risk."
            ),
            "use_in_specific_populations": {
                "renal_impairment": (
                    "Renal impairment may reduce insulin requirements due to decreased insulin "
                    "clearance; closely monitor glucose and adjust dose to reduce hypoglycemia "
                    "risk."
                ),
                "hepatic_impairment": (
                    "Hepatic impairment may reduce insulin requirements due to reduced "
                    "gluconeogenesis and insulin clearance; monitor glucose closely and adjust "
                    "dose."
                ),
                "geriatric_use": (
                    "Hypoglycemia may be harder to recognize in elderly patients; initiate "
                    "conservatively and titrate carefully with frequent monitoring."
                ),
                "pregnancy": (
                    "Insulin requirements may change substantially during pregnancy; "
                    "glycemic control is important for maternal/fetal outcomes and dosing "
                    "should be individualized with close monitoring."
                ),
            },
            "dosage_considerations": (
                "Reduce dose and monitor closely in renal or hepatic impairment due to "
                "decreased insulin clearance/requirements and elevated hypoglycemia risk."
            ),
        },
    },
]
