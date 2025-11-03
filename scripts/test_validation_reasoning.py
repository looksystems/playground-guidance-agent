#!/usr/bin/env python3
"""
Test script to create a consultation with validation reasoning data.
This allows us to test the frontend display of validation reasoning without
requiring LLM API calls.
"""

import sys
import os
from uuid import uuid4
from datetime import datetime, timezone
import psycopg2
import json

# Database connection
DB_URL = "postgresql://postgres:postgres@localhost:5432/guidance_agent"

def create_test_consultation():
    """Create a test consultation with validation reasoning."""

    consultation_id = str(uuid4())
    customer_id = str(uuid4())
    advisor_id = str(uuid4())

    # Create conversation with validation reasoning
    conversation = [
        {
            "role": "system",
            "content": "Consultation started with Test User for QA, age 45",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "role": "customer",
            "content": "I want to consolidate my pension pots. What should I consider?",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "role": "advisor",
            "content": "When considering pension consolidation, there are several important factors to evaluate:\n\n1. **Fees and Charges**: Compare the fees on your current pensions with any consolidation charges.\n\n2. **Investment Options**: Ensure the consolidated pension offers suitable investment choices for your risk tolerance.\n\n3. **Benefits**: Check if any of your current pensions have special benefits (like guaranteed annuity rates) that you'd lose.\n\n4. **Simplification**: Consolidation makes it easier to manage and track your retirement savings.\n\n**Important**: This is guidance only. For personalized advice on whether consolidation is right for you, please consult with an FCA-regulated financial advisor.\n\nDoes this help clarify the key considerations?",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compliance_score": 0.92,
            "compliance_confidence": 0.92,
            "compliance_reasoning": "**FCA Compliance Analysis**\n\n**1. Guidance vs Advice Boundary**: PASS\n- The response appropriately stays within guidance boundaries\n- Uses general information and educational content\n- Includes clear signposting to regulated advice\n- No specific product recommendations or personalized advice given\n\n**2. Risk Disclosure**: PASS\n- Mentions potential loss of benefits (guaranteed annuity rates)\n- Highlights the importance of checking current pension features\n- Appropriately cautious about consolidation trade-offs\n\n**3. Clarity and Not Misleading**: PASS\n- Information is presented clearly with bullet points\n- Uses accessible language\n- Structured format aids understanding\n- No misleading statements detected\n\n**4. Understanding Verification**: MINOR ISSUE\n- Includes a basic check (\"Does this help clarify...\")\n- Could be more thorough in verifying customer comprehension\n- Recommend adding specific understanding checks\n\n**5. Appropriate Signposting**: PASS\n- Clear signpost to FCA-regulated financial advisor\n- Explicitly states this is \"guidance only\"\n- Appropriate for the complexity of the topic\n\n**Overall Assessment**: \nThe guidance is compliant with FCA requirements. It maintains appropriate boundaries, provides balanced information, and includes necessary signposting. Minor improvement could be made in understanding verification, but this does not constitute a compliance breach.\n\n**Confidence**: 92% - High confidence in compliance assessment.",
            "compliance_issues": [
                {
                    "category": "understanding_check",
                    "severity": "low",
                    "description": "Understanding verification could be more thorough with specific comprehension checks"
                }
            ],
            "compliance_passed": True,
            "requires_human_review": False
        },
        {
            "role": "customer",
            "content": "That makes sense. What if I want to transfer my defined benefit pension?",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "role": "advisor",
            "content": "Transferring a defined benefit (DB) pension is a significant decision that requires very careful consideration. Here's what you need to know:\n\n**Important Legal Requirement**: If your DB pension is worth over £30,000, you MUST take advice from an FCA-regulated financial advisor before transferring. This is a legal requirement.\n\n**Why DB transfers are complex**:\n- DB pensions provide guaranteed income for life\n- Transferring gives up this security\n- You take on investment risk\n- You could end up worse off in retirement\n\n**When it might make sense** (rare cases):\n- Serious ill health affecting life expectancy\n- Specific legacy planning needs\n- No dependents who would benefit from survivor benefits\n\nI cannot provide guidance on whether you should transfer a DB pension. You must speak with an FCA-regulated pension transfer specialist.\n\nWould you like help finding a qualified advisor?",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compliance_score": 0.65,
            "compliance_confidence": 0.65,
            "compliance_reasoning": "**FCA Compliance Analysis**\n\n**1. Guidance vs Advice Boundary**: MAJOR CONCERN\n- The response ventures close to advice territory\n- Lists specific scenarios (\"when it might make sense\")\n- While it includes disclaimers, the enumeration of transfer scenarios could be seen as steering toward advice\n- Should be even more cautious given DB transfer sensitivity\n\n**2. Risk Disclosure**: PASS\n- Excellent risk disclosure\n- Clearly states the loss of guaranteed income\n- Mentions investment risk and potential negative outcomes\n- Appropriately emphasizes the seriousness of the decision\n\n**3. Clarity and Not Misleading**: PASS\n- Information is clear and well-structured\n- Correctly states the £30,000 legal requirement\n- Emphasizes the need for specialist advice\n- No misleading information\n\n**4. Understanding Verification**: PASS\n- Offers further assistance (\"Would you like help finding...\")\n- Acknowledges the customer's question directly\n\n**5. Appropriate Signposting**: PASS\n- Strong signposting to FCA-regulated pension transfer specialist\n- Correctly emphasizes this is beyond guidance scope\n- Offers to help find qualified advisor\n\n**6. DB Transfer Warning**: CRITICAL REQUIREMENT\n- Correctly identifies that DB transfers require regulated advice\n- Mentions the £30,000 threshold\n- However, providing \"when it might make sense\" scenarios is borderline advice\n\n**Overall Assessment**: \nThis response is borderline compliant. While it includes strong warnings and signposting, the enumeration of scenarios where DB transfer \"might make sense\" crosses into advice territory. This topic is extremely sensitive from an FCA perspective due to past DB transfer scandals.\n\n**Recommendation**: Remove the \"when it might make sense\" section entirely and simply state that this requires specialist advice without any suggestion of circumstances.\n\n**Confidence**: 65% - Medium confidence. The response has good elements but the advice boundary issue is significant for DB transfers.",
            "compliance_issues": [
                {
                    "category": "advice_boundary",
                    "severity": "medium",
                    "description": "Listing scenarios where DB transfer 'might make sense' ventures into advice territory, even with disclaimers"
                },
                {
                    "category": "db_warning",
                    "severity": "medium",
                    "description": "While DB transfer warning is present, the advice-like content undermines the guidance-only position"
                }
            ],
            "compliance_passed": False,
            "requires_human_review": True
        }
    ]

    meta = {
        "customer_name": "Test User for QA",
        "customer_age": 45,
        "advisor_name": "Sarah",
        "initial_query": "I want to know about pension consolidation options.",
        "compliance_scores": [0.92, 0.65]
    }

    outcome = {
        "customer_satisfaction": 8.5,
        "comprehension": 8.0,
        "fca_compliant": False,  # Because one message failed
        "avg_compliance_score": 0.785,
        "successful": True
    }

    # Connect to database
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Insert consultation
        cur.execute("""
            INSERT INTO consultations (
                id, customer_id, advisor_id, start_time, end_time,
                duration_seconds, conversation, outcome, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            consultation_id,
            customer_id,
            advisor_id,
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
            180,  # 3 minutes
            json.dumps(conversation),
            json.dumps(outcome),
            json.dumps(meta)
        ))

        conn.commit()
        cur.close()
        conn.close()

        print(f"✓ Successfully created test consultation")
        print(f"  Consultation ID: {consultation_id}")
        print(f"  URL: http://localhost:3000/admin/consultations/{consultation_id}")
        print(f"\n  Advisor messages:")
        print(f"    - Message 1: PASSED (92% compliance) with 1 minor issue")
        print(f"    - Message 2: FAILED (65% compliance) with 2 medium issues, requires human review")

        return consultation_id

    except Exception as e:
        print(f"✗ Error creating test consultation: {e}")
        return None

if __name__ == "__main__":
    consultation_id = create_test_consultation()
    if consultation_id:
        sys.exit(0)
    else:
        sys.exit(1)
