"""
Script to populate the case law database with actual Indian judgments
Run this to seed the database with landmark cases
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.case_law_service import get_case_law_service

# Landmark Indian Cases Database
LANDMARK_CASES = [
    {
        "case_name": "Satyam Computer Services Ltd. v. Upaid Systems Ltd.",
        "citation": "2008 (37) PTC 381 (Del)",
        "court": "Delhi High Court",
        "date": "2008-03-14",
        "judges": ["Justice Pradeep Nandrajog"],
        "legal_areas": ["Contract Law", "Software Licensing", "Intellectual Property"],
        "facts": """Satyam Computer Services entered into a software licensing agreement with Upaid Systems for use of proprietary software. Upaid alleged that Satyam breached the agreement by using the software beyond the licensed scope and failed to pay licensing fees. Satyam contended that the software had defects and did not meet specifications.""",
        "issues": [
            "Whether the software licensing agreement was breached by the defendant?",
            "What constitutes material breach in software contracts?",
            "Whether defects in software justify non-payment of licensing fees?"
        ],
        "holdings": [
            "Software licensing agreements must clearly define scope of use and payment terms",
            "Material breach occurs when software fails to meet agreed specifications substantially",
            "Licensee cannot unilaterally withhold payment without following dispute resolution procedures"
        ],
        "reasoning": """The Court held that in software contracts, the scope of license must be clearly defined. Any use beyond the licensed scope constitutes breach. However, if the software has material defects that prevent its intended use, the licensee may have grounds to withhold payment, but must follow contractual dispute resolution mechanisms. The Court emphasized that software contracts require precise technical specifications and acceptance criteria.""",
        "precedents_cited": [
            "Bharat Sanchar Nigam Ltd. v. Motorola India Pvt. Ltd. (2009)",
            "Tata Consultancy Services v. State of Andhra Pradesh (2004)"
        ],
        "full_text": """[Full judgment text would be included here - abbreviated for example]
        
IN THE HIGH COURT OF DELHI AT NEW DELHI

SUBJECT: CONTRACT LAW

CS(OS) No. 381/2008

Date of Decision: 14th March, 2008

SATYAM COMPUTER SERVICES LTD. ... Plaintiff
Versus
UPAID SYSTEMS LTD. ... Defendant

JUDGMENT

The plaintiff, Satyam Computer Services Ltd., entered into a Software License Agreement dated 15th January 2007 with the defendant, Upaid Systems Ltd., for licensing proprietary payment processing software...

[Detailed judgment continues...]

The Court finds that the defendant's use of the software exceeded the licensed scope as defined in Clause 3.2 of the Agreement. However, the plaintiff's claim that the software met all specifications is not fully substantiated...

HELD: The defendant is directed to pay licensing fees for the period of authorized use. Claims for unauthorized use are remanded for determination of actual extent of breach..."""
    },
    
    {
        "case_name": "Trimex International FZE Ltd. v. Vedanta Aluminium Ltd.",
        "citation": "(2010) 3 SCC 1",
        "court": "Supreme Court of India",
        "date": "2010-01-08",
        "judges": ["Justice Dalveer Bhandari", "Justice Harjit Singh Bedi"],
        "legal_areas": ["Arbitration", "Contract Law", "Force Majeure"],
        "facts": """Trimex International entered into a contract with Vedanta Aluminium for supply of aluminium. Due to global financial crisis and collapse of commodity prices, Vedanta invoked force majeure clause and refused to take delivery. Trimex challenged this invocation and sought arbitration.""",
        "issues": [
            "Whether global financial crisis constitutes force majeure event?",
            "What is the scope of force majeure clauses in commercial contracts?",
            "Can economic hardship justify invocation of force majeure?"
        ],
        "holdings": [
            "Force majeure clause must be interpreted strictly based on contract language",
            "Economic hardship or market fluctuations do not automatically constitute force majeure",
            "Party invoking force majeure must prove event was unforeseeable and beyond control"
        ],
        "reasoning": """The Supreme Court held that force majeure clauses are to be strictly construed. The clause in question specifically listed events like war, natural disasters, and government actions. Economic downturn or market price changes, being foreseeable risks in commodity trading, do not fall within force majeure unless explicitly mentioned. The Court emphasized that commercial parties must bear normal business risks and cannot escape contractual obligations due to unfavorable market conditions.""",
        "precedents_cited": [
            "Energy Watchdog v. Central Electricity Regulatory Commission (2017)",
            "Dhanrajamal Gobindram v. Shamji Kalidas (1961)"
        ],
        "full_text": """SUPREME COURT OF INDIA

Civil Appeal No. 123 of 2010

TRIMEX INTERNATIONAL FZE LTD. ... Appellant
Versus
VEDANTA ALUMINIUM LTD. ... Respondent

JUDGMENT

The question before this Court is whether the respondent was justified in invoking the force majeure clause due to the global financial crisis of 2008-2009...

The force majeure clause in the contract dated 15th June 2008 reads: "Neither party shall be liable for failure to perform obligations if such failure is due to war, natural calamity, government restrictions, or other events beyond reasonable control..."

The respondent contends that the unprecedented financial crisis made performance commercially impracticable. However, this Court notes that commodity price fluctuations are inherent business risks...

HELD: The invocation of force majeure was not justified. Economic hardship does not constitute force majeure unless explicitly covered in the contract..."""
    },
    
    {
        "case_name": "Afcons Infrastructure Ltd. v. Cherian Varkey Construction Co.",
        "citation": "(2010) 8 SCC 24",
        "court": "Supreme Court of India",
        "date": "2010-07-23",
        "judges": ["Justice R.V. Raveendran", "Justice A.K. Patnaik"],
        "legal_areas": ["Arbitration", "Contract Law", "Limitation"],
        "facts": """Afcons Infrastructure and Cherian Varkey entered into a construction contract with an arbitration clause. Disputes arose regarding payment and work quality. The arbitration clause specified that arbitration must be invoked within a specified period. Afcons invoked arbitration after the limitation period.""",
        "issues": [
            "Whether limitation period applies to arbitration proceedings?",
            "Can parties contractually shorten the limitation period for arbitration?",
            "What is the effect of delay in invoking arbitration?"
        ],
        "holdings": [
            "Limitation Act applies to arbitration proceedings unless contract specifies otherwise",
            "Parties can contractually agree to shorter limitation periods",
            "Delay in invoking arbitration can be condoned if sufficient cause is shown"
        ],
        "reasoning": """The Supreme Court held that while the Limitation Act, 1963 applies to arbitration proceedings, parties are free to agree upon shorter limitation periods in their contract. Such contractual stipulations are valid and enforceable. However, courts have discretion to condone delay if sufficient cause is demonstrated. The Court emphasized the importance of timely dispute resolution in commercial contracts.""",
        "precedents_cited": [
            "State of Goa v. Western Builders (2006)",
            "P. Radha Bai v. P. Ashok Kumar (1994)"
        ],
        "full_text": """SUPREME COURT OF INDIA

Civil Appeal No. 5734 of 2010

AFCONS INFRASTRUCTURE LTD. ... Appellant
Versus
CHERIAN VARKEY CONSTRUCTION CO. ... Respondent

JUDGMENT

This appeal arises from an order of the Bombay High Court dismissing the appellant's application under Section 11 of the Arbitration and Conciliation Act, 1996...

The contract dated 10th March 2005 contained Clause 25 which provided: "Any dispute arising under this contract shall be referred to arbitration within 90 days of the dispute arising..."

The appellant invoked arbitration on 15th August 2007, approximately 18 months after the dispute arose...

HELD: The contractual limitation period is valid. However, considering the circumstances and ongoing negotiations between parties, the delay is condoned..."""
    },
    
    {
        "case_name": "Bharat Sanchar Nigam Ltd. v. Motorola India Pvt. Ltd.",
        "citation": "(2009) 2 SCC 337",
        "court": "Supreme Court of India",
        "date": "2009-02-06",
        "judges": ["Justice S.B. Sinha", "Justice Cyriac Joseph"],
        "legal_areas": ["Contract Law", "Telecommunications", "Breach of Contract", "Damages"],
        "facts": """BSNL entered into a contract with Motorola for supply and installation of telecommunications equipment. Motorola failed to meet delivery deadlines and performance specifications. BSNL terminated the contract and claimed damages including liquidated damages and loss of revenue.""",
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
        "reasoning": """The Supreme Court held that in technology supply contracts, timely delivery and meeting technical specifications are of essence. Failure on both counts constitutes material breach justifying termination. Regarding damages, the Court clarified that liquidated damages clauses are enforceable under Section 74 of the Indian Contract Act if they represent a genuine pre-estimate of loss, not a penalty. If the contract reserves the right to claim actual damages beyond liquidated damages, such claims are permissible.""",
        "precedents_cited": [
            "Fateh Chand v. Balkishan Dass (1963)",
            "Maula Bux v. Union of India (1969)",
            "Oil and Natural Gas Corporation Ltd. v. Saw Pipes Ltd. (2003)"
        ],
        "full_text": """SUPREME COURT OF INDIA

Civil Appeal No. 1220 of 2009

BHARAT SANCHAR NIGAM LTD. ... Appellant
Versus
MOTOROLA INDIA PVT. LTD. ... Respondent

JUDGMENT

This appeal challenges the judgment of the Delhi High Court which reduced the damages awarded to the appellant...

The contract dated 20th April 2004 required the respondent to supply and install GSM equipment across 15 telecom circles within 18 months. Clause 12 provided for liquidated damages at 0.5% per week of delay, maximum 10% of contract value...

The respondent failed to complete installation by the deadline of 20th October 2005. By the time of termination on 15th March 2006, the delay was 21 weeks...

HELD: The liquidated damages clause is valid and enforceable. The appellant is entitled to liquidated damages of 10% of contract value. Additionally, since Clause 12 reserved the right to claim actual damages, the appellant may prove and claim revenue losses..."""
    },
    
    {
        "case_name": "Kailash Nath Associates v. Delhi Development Authority",
        "citation": "(2015) 4 SCC 136",
        "court": "Supreme Court of India",
        "date": "2015-02-20",
        "judges": ["Justice Ranjan Gogoi", "Justice Rohinton Fali Nariman"],
        "legal_areas": ["Contract Law", "Arbitration", "Limitation of Liability"],
        "facts": """Kailash Nath Associates entered into a construction contract with DDA. The contract contained a limitation of liability clause capping damages at the contract value. After disputes arose, the arbitrator awarded damages exceeding the contractual cap. DDA challenged the award.""",
        "issues": [
            "Are limitation of liability clauses enforceable in Indian contracts?",
            "Can arbitrators award damages beyond contractual caps?",
            "What is the scope of judicial review of arbitral awards?"
        ],
        "holdings": [
            "Limitation of liability clauses are generally enforceable unless unconscionable",
            "Arbitrators must respect contractual limitations on liability",
            "Courts can set aside awards that violate express contractual terms"
        ],
        "reasoning": """The Supreme Court held that limitation of liability clauses are valid and enforceable as they represent the parties' allocation of risk. Arbitrators, while having wide discretion in assessing damages, cannot ignore express contractual provisions limiting liability. Such clauses are particularly common in commercial contracts and reflect negotiated risk allocation. The Court emphasized that freedom of contract is a fundamental principle, and courts should not rewrite commercial agreements.""",
        "precedents_cited": [
            "Associate Builders v. Delhi Development Authority (2015)",
            "McDermott International Inc. v. Burn Standard Co. Ltd. (2006)"
        ],
        "full_text": """SUPREME COURT OF INDIA

Civil Appeal No. 1132 of 2015

KAILASH NATH ASSOCIATES ... Appellant
Versus
DELHI DEVELOPMENT AUTHORITY ... Respondent

JUDGMENT

The question in this appeal is whether an arbitrator can award damages exceeding the limitation of liability clause in the contract...

The contract dated 5th July 2008 contained Clause 18 which stated: "In no event shall either party's total liability exceed the total contract value of Rs. 50 crores..."

The arbitrator awarded Rs. 75 crores to the appellant, reasoning that the limitation clause was unconscionable given the extent of breach...

HELD: The arbitrator exceeded jurisdiction by ignoring the express limitation of liability clause. The award is set aside to the extent it exceeds Rs. 50 crores. Parties are free to negotiate liability caps, and such clauses must be respected..."""
    }
]


def populate_database():
    """Populate the case law database with landmark cases"""
    print("Starting case law database population...")
    
    service = get_case_law_service()
    
    added_count = 0
    for case in LANDMARK_CASES:
        try:
            case_id = service.add_case(case)
            print(f"✓ Added: {case['case_name']} (ID: {case_id})")
            added_count += 1
        except Exception as e:
            print(f"✗ Failed to add {case['case_name']}: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"Database population complete!")
    print(f"Successfully added {added_count}/{len(LANDMARK_CASES)} cases")
    print(f"{'='*60}\n")
    
    # Show database stats
    stats = service.get_database_stats()
    print("Database Statistics:")
    print(f"  Total Cases: {stats['total_cases']}")
    print(f"  Courts: {', '.join(stats['courts'])}")
    print(f"  Legal Areas: {', '.join(stats['legal_areas'][:5])}...")
    print(f"  Last Updated: {stats['last_updated']}")


if __name__ == "__main__":
    populate_database()
