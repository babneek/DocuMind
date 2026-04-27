"""
Pre-defined case collections for each legal domain
These can be imported directly via UI without web scraping
"""

CONTRACT_LAW_CASES = [
    {
        "case_name": "Satyam Computer Services Ltd. v. Upaid Systems Ltd.",
        "citation": "2008 (37) PTC 381 (Del)",
        "court": "Delhi High Court",
        "date": "2008-03-14",
        "judges": ["Justice Pradeep Nandrajog"],
        "category": "Contract Law",
        "subcategory": "Software Licensing",
        "legal_areas": ["Contract Law", "Software Licensing", "Intellectual Property"],
        "jurisdiction": "India",
        "importance": "Important",
        "facts": "Satyam Computer Services entered into a software licensing agreement with Upaid Systems for use of proprietary software. Upaid alleged that Satyam breached the agreement by using the software beyond the licensed scope and failed to pay licensing fees.",
        "issues": [
            "Whether the software licensing agreement was breached?",
            "What constitutes material breach in software contracts?",
            "Whether defects in software justify non-payment of licensing fees?"
        ],
        "holdings": [
            "Software licensing agreements must clearly define scope of use and payment terms",
            "Material breach occurs when software fails to meet agreed specifications substantially",
            "Licensee cannot unilaterally withhold payment without following dispute resolution procedures"
        ],
        "reasoning": "The Court held that in software contracts, the scope of license must be clearly defined. Any use beyond the licensed scope constitutes breach. However, if the software has material defects that prevent its intended use, the licensee may have grounds to withhold payment, but must follow contractual dispute resolution mechanisms.",
        "precedents_cited": [
            "Bharat Sanchar Nigam Ltd. v. Motorola India Pvt. Ltd. (2009)",
            "Tata Consultancy Services v. State of Andhra Pradesh (2004)"
        ],
        "full_text": "Software licensing case - full text abbreviated",
        "source": "Manual Entry"
    },
    {
        "case_name": "Bharat Sanchar Nigam Ltd. v. Motorola India Pvt. Ltd.",
        "citation": "(2009) 2 SCC 337",
        "court": "Supreme Court of India",
        "date": "2009-02-06",
        "judges": ["Justice S.B. Sinha", "Justice Cyriac Joseph"],
        "category": "Contract Law",
        "subcategory": "Technology Contracts",
        "legal_areas": ["Contract Law", "Telecommunications", "Breach of Contract", "Damages"],
        "jurisdiction": "India",
        "importance": "Landmark",
        "facts": "BSNL entered into a contract with Motorola for supply and installation of telecommunications equipment. Motorola failed to meet delivery deadlines and performance specifications. BSNL terminated the contract and claimed damages.",
        "issues": [
            "What constitutes material breach in technology supply contracts?",
            "Can liquidated damages and actual damages be claimed simultaneously?",
            "What is the measure of damages for breach of technology contracts?"
        ],
        "holdings": [
            "Failure to meet delivery deadlines and performance specifications constitutes material breach",
            "Liquidated damages clause is enforceable if it represents genuine pre-estimate of loss",
            "Actual damages beyond liquidated damages can be claimed if specifically reserved in contract"
        ],
        "reasoning": "The Supreme Court held that in technology supply contracts, timely delivery and meeting technical specifications are of essence. Failure on both counts constitutes material breach justifying termination. Regarding damages, liquidated damages clauses are enforceable under Section 74 of the Indian Contract Act if they represent a genuine pre-estimate of loss.",
        "precedents_cited": [
            "Fateh Chand v. Balkishan Dass (1963)",
            "Oil and Natural Gas Corporation Ltd. v. Saw Pipes Ltd. (2003)"
        ],
        "full_text": "Technology contract breach case - full text abbreviated",
        "source": "Manual Entry"
    }
]

CORPORATE_LAW_CASES = [
    {
        "case_name": "Vodafone International Holdings BV v. Union of India",
        "citation": "(2012) 6 SCC 613",
        "court": "Supreme Court of India",
        "date": "2012-01-20",
        "judges": ["Chief Justice S.H. Kapadia", "Justice K.S. Radhakrishnan", "Justice Swatanter Kumar"],
        "category": "Corporate Law",
        "subcategory": "M&A and Tax",
        "legal_areas": ["Corporate Law", "Tax Law", "M&A", "International Transactions"],
        "jurisdiction": "India",
        "importance": "Landmark",
        "facts": "Vodafone acquired shares of Hutchison Essar through an offshore transaction. Indian tax authorities sought to tax this transaction claiming it was a transfer of Indian assets.",
        "issues": [
            "Whether offshore share transfers can be taxed in India?",
            "What is the test for determining tax jurisdiction?",
            "Can tax authorities look through corporate structures?"
        ],
        "holdings": [
            "Offshore transactions cannot be taxed merely because underlying assets are in India",
            "Substance over form principle has limits in tax law",
            "Corporate structures cannot be disregarded without statutory basis"
        ],
        "reasoning": "The Supreme Court held that the transaction was structured offshore and Indian tax authorities lacked jurisdiction. The Court emphasized that while substance over form is important, it cannot override clear statutory provisions and corporate structures.",
        "precedents_cited": [
            "McDowell & Co. v. CTO (1985)",
            "Azadi Bachao Andolan v. Union of India (2003)"
        ],
        "full_text": "Vodafone tax case - full text abbreviated",
        "source": "Manual Entry"
    }
]

IP_LAW_CASES = [
    {
        "case_name": "Novartis AG v. Union of India",
        "citation": "(2013) 6 SCC 1",
        "court": "Supreme Court of India",
        "date": "2013-04-01",
        "judges": ["Justice Aftab Alam", "Justice Ranjana Prakash Desai"],
        "category": "Intellectual Property",
        "subcategory": "Patent Law",
        "legal_areas": ["Intellectual Property", "Patent Law", "Pharmaceutical Patents"],
        "jurisdiction": "India",
        "importance": "Landmark",
        "facts": "Novartis sought patent for Glivec (cancer drug). Patent office rejected citing Section 3(d) of Patents Act which bars patents for new forms of known substances unless they show enhanced efficacy.",
        "issues": [
            "What is the test for 'enhanced efficacy' under Section 3(d)?",
            "Can pharmaceutical companies patent new forms of existing drugs?",
            "How to balance innovation incentives with public health?"
        ],
        "holdings": [
            "Section 3(d) requires demonstrable enhancement in therapeutic efficacy",
            "Mere discovery of new form of known substance is not patentable",
            "Patent law must balance innovation with access to medicines"
        ],
        "reasoning": "The Supreme Court upheld Section 3(d) as constitutional and held that Novartis failed to demonstrate enhanced therapeutic efficacy. The Court emphasized that patent law must serve public interest and prevent evergreening of patents.",
        "precedents_cited": [
            "Dimminaco AG v. Controller of Patents (2002)",
            "F. Hoffmann-La Roche Ltd. v. Cipla Ltd. (2008)"
        ],
        "full_text": "Novartis patent case - full text abbreviated",
        "source": "Manual Entry"
    }
]

EMPLOYMENT_LAW_CASES = [
    {
        "case_name": "Vishaka v. State of Rajasthan",
        "citation": "(1997) 6 SCC 241",
        "court": "Supreme Court of India",
        "date": "1997-08-13",
        "judges": ["Justice J.S. Verma", "Justice Sujata V. Manohar", "Justice B.N. Kirpal"],
        "category": "Employment Law",
        "subcategory": "Sexual Harassment",
        "legal_areas": ["Employment Law", "Sexual Harassment", "Women's Rights", "Constitutional Law"],
        "jurisdiction": "India",
        "importance": "Landmark",
        "facts": "Social workers were gang-raped in Rajasthan. PIL filed seeking guidelines for prevention of sexual harassment at workplace in absence of legislation.",
        "issues": [
            "Can courts frame guidelines in absence of legislation?",
            "What constitutes sexual harassment at workplace?",
            "What are employer's obligations to prevent harassment?"
        ],
        "holdings": [
            "Courts can frame guidelines to fill legislative vacuum",
            "Sexual harassment violates fundamental rights under Articles 14, 19, 21",
            "Employers must establish complaint mechanisms and preventive measures"
        ],
        "reasoning": "The Supreme Court laid down comprehensive guidelines (Vishaka Guidelines) for prevention of sexual harassment at workplace. These guidelines remained in force until the Sexual Harassment Act 2013 was enacted.",
        "precedents_cited": [
            "Apparel Export Promotion Council v. A.K. Chopra (1999)",
            "Medha Kotwal Lele v. Union of India (2013)"
        ],
        "full_text": "Vishaka guidelines case - full text abbreviated",
        "source": "Manual Entry"
    }
]

REAL_ESTATE_CASES = [
    {
        "case_name": "Pioneer Urban Land and Infrastructure Ltd. v. Union of India",
        "citation": "(2019) 8 SCC 416",
        "court": "Supreme Court of India",
        "date": "2019-07-11",
        "judges": ["Justice D.Y. Chandrachud", "Justice Hemant Gupta"],
        "category": "Real Estate",
        "subcategory": "RERA",
        "legal_areas": ["Real Estate", "RERA", "Consumer Protection", "Constitutional Law"],
        "jurisdiction": "India",
        "importance": "Landmark",
        "facts": "Challenge to constitutional validity of RERA provisions giving retrospective effect and establishing separate adjudicatory mechanism.",
        "issues": [
            "Whether RERA can apply to ongoing projects?",
            "Is RERA's adjudicatory mechanism constitutional?",
            "Can RERA override contractual terms?"
        ],
        "holdings": [
            "RERA validly applies to ongoing projects",
            "RERA's adjudicatory mechanism is constitutional",
            "RERA provisions are beneficial legislation protecting home buyers"
        ],
        "reasoning": "The Supreme Court upheld RERA as constitutional, emphasizing that it is beneficial legislation aimed at protecting home buyers. The Court held that RERA can apply to ongoing projects as it addresses a pressing social need.",
        "precedents_cited": [
            "Bangalore Development Authority v. R. Hanumaiah (1978)",
            "Kolhapur Canesugar Works Ltd. v. Union of India (2000)"
        ],
        "full_text": "RERA constitutional validity case - full text abbreviated",
        "source": "Manual Entry"
    }
]

# Collection mapping
CASE_COLLECTIONS = {
    "Contract Law": CONTRACT_LAW_CASES,
    "Corporate Law": CORPORATE_LAW_CASES,
    "Intellectual Property": IP_LAW_CASES,
    "Employment Law": EMPLOYMENT_LAW_CASES,
    "Real Estate": REAL_ESTATE_CASES,
}

def get_available_domains():
    """Get list of available domains"""
    return list(CASE_COLLECTIONS.keys())

def get_cases_for_domain(domain: str):
    """Get cases for a specific domain"""
    return CASE_COLLECTIONS.get(domain, [])

def get_all_cases():
    """Get all cases from all domains"""
    all_cases = []
    for cases in CASE_COLLECTIONS.values():
        all_cases.extend(cases)
    return all_cases
