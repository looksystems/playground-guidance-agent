#!/usr/bin/env python3
"""Review and analyze consultations from training sessions.

This script provides various ways to query, filter, and review consultations
that have been persisted to the database during training runs.

Usage:
    # List all consultations
    python scripts/review_consultations.py list

    # Show details of a specific consultation
    python scripts/review_consultations.py show <consultation_id>

    # Filter by training session
    python scripts/review_consultations.py list --session <session_id>

    # Filter by success/failure
    python scripts/review_consultations.py list --successful
    python scripts/review_consultations.py list --failed

    # Filter by compliance
    python scripts/review_consultations.py list --non-compliant

    # Show conversation transcript
    python scripts/review_consultations.py conversation <consultation_id>

    # Export to JSON
    python scripts/review_consultations.py export --session <session_id> --output results.json

    # Statistics for a session
    python scripts/review_consultations.py stats --session <session_id>
"""

import argparse
import json
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import desc, and_, or_
from sqlalchemy.orm import Session

from guidance_agent.core.database import get_session, Consultation


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "N/A"


def format_duration(seconds: int) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def list_consultations(
    session: Session,
    training_session_id: Optional[str] = None,
    successful: Optional[bool] = None,
    compliant: Optional[bool] = None,
    limit: int = 50,
    show_conversation: bool = False,
) -> None:
    """List consultations with optional filters.

    Args:
        session: Database session
        training_session_id: Filter by training session
        successful: Filter by success status
        compliant: Filter by compliance status
        limit: Maximum results to return
        show_conversation: Whether to show conversation preview
    """
    query = session.query(Consultation).order_by(desc(Consultation.start_time))

    # Apply filters
    if training_session_id:
        query = query.filter(
            Consultation.meta["training_session_id"].astext == training_session_id
        )

    if successful is not None:
        query = query.filter(
            Consultation.outcome["successful"].astext == str(successful).lower()
        )

    if compliant is not None:
        query = query.filter(
            Consultation.outcome["fca_compliant"].astext == str(compliant).lower()
        )

    consultations = query.limit(limit).all()

    if not consultations:
        print("No consultations found matching criteria.")
        return

    print(f"\n{'=' * 120}")
    print(f"Found {len(consultations)} consultation(s)")
    print(f"{'=' * 120}\n")

    for i, consultation in enumerate(consultations, 1):
        outcome = consultation.outcome or {}
        meta = consultation.meta or {}

        # Basic info
        print(f"[{i}] Consultation ID: {consultation.id}")
        print(f"    Start: {format_datetime(consultation.start_time)}")
        print(f"    Duration: {format_duration(consultation.duration_seconds or 0)}")
        print(
            f"    Customer: {meta.get('customer_name', 'Unknown')} (age {meta.get('customer_age', '?')})"
        )
        print(f"    Advisor: {meta.get('advisor_name', 'Unknown')}")

        # Outcome metrics
        success = outcome.get("successful", False)
        compliance = outcome.get("fca_compliant", False)
        satisfaction = outcome.get("customer_satisfaction", 0)
        comprehension = outcome.get("comprehension", 0)

        status_icon = "✓" if success else "✗"
        compliance_icon = "✓" if compliance else "✗"

        print(f"    Success: {status_icon} {success}")
        print(f"    Compliance: {compliance_icon} {compliance}")
        print(f"    Satisfaction: {satisfaction:.1f}/10")
        print(f"    Comprehension: {comprehension:.1f}/10")

        # Show session ID if available
        session_id = meta.get("training_session_id", "")
        if session_id:
            print(f"    Session: {session_id[:8]}...")

        # Show conversation preview
        if show_conversation and consultation.conversation:
            turn_count = len(consultation.conversation)
            print(f"    Turns: {turn_count}")
            if turn_count > 0:
                first_message = consultation.conversation[0]
                preview = first_message.get("content", "")[:80]
                print(f"    First message: {preview}...")

        print()


def show_consultation_details(session: Session, consultation_id: str) -> None:
    """Show detailed information about a consultation.

    Args:
        session: Database session
        consultation_id: Consultation UUID
    """
    try:
        consultation = (
            session.query(Consultation)
            .filter(Consultation.id == UUID(consultation_id))
            .first()
        )
    except ValueError:
        print(f"Error: Invalid consultation ID format: {consultation_id}")
        return

    if not consultation:
        print(f"Consultation not found: {consultation_id}")
        return

    outcome = consultation.outcome or {}
    meta = consultation.meta or {}

    print(f"\n{'=' * 80}")
    print(f"CONSULTATION DETAILS: {consultation.id}")
    print(f"{'=' * 80}\n")

    # Timestamps
    print("TIMING:")
    print(f"  Start:    {format_datetime(consultation.start_time)}")
    print(f"  End:      {format_datetime(consultation.end_time)}")
    print(f"  Duration: {format_duration(consultation.duration_seconds or 0)}")
    print()

    # Participants
    print("PARTICIPANTS:")
    print(f"  Customer: {meta.get('customer_name', 'Unknown')} (ID: {consultation.customer_id})")
    print(f"  Age:      {meta.get('customer_age', '?')}")
    print(f"  Advisor:  {meta.get('advisor_name', 'Unknown')} (ID: {consultation.advisor_id})")
    print()

    # Session info
    print("SESSION:")
    print(f"  Training Session: {meta.get('training_session_id', 'N/A')}")
    print(f"  Acceleration:     {meta.get('acceleration_factor', 'N/A')}x")
    print()

    # Outcome metrics
    print("OUTCOME METRICS:")
    print(f"  Success:        {outcome.get('successful', False)}")
    print(f"  FCA Compliant:  {outcome.get('fca_compliant', False)}")
    print(f"  Satisfaction:   {outcome.get('customer_satisfaction', 0):.1f}/10")
    print(f"  Comprehension:  {outcome.get('comprehension', 0):.1f}/10")
    print(f"  Goal Alignment: {outcome.get('goal_alignment', 0):.1f}/10")
    print()

    # Quality checks
    print("QUALITY CHECKS:")
    print(f"  Risks Identified:      {outcome.get('risks_identified', False)}")
    print(f"  Guidance Appropriate:  {outcome.get('guidance_appropriate', False)}")
    print(f"  Understanding Checked: {outcome.get('understanding_checked', False)}")
    print(f"  Signposted:            {outcome.get('signposted_when_needed', False)}")
    print()

    # DB pension check
    has_db = outcome.get("has_db_pension", False)
    db_warning = outcome.get("db_warning_given", False)
    print("DB PENSION CHECK:")
    print(f"  Has DB Pension:  {has_db}")
    print(f"  Warning Given:   {db_warning}")
    print()

    # Issues
    issues = outcome.get("issues", [])
    if issues:
        print("ISSUES IDENTIFIED:")
        for issue in issues:
            print(f"  - {issue}")
        print()

    # Reasoning
    reasoning = outcome.get("reasoning", "")
    if reasoning:
        print("REASONING:")
        print(f"  {reasoning}")
        print()

    # Conversation stats
    if consultation.conversation:
        turn_count = len(consultation.conversation)
        advisor_turns = sum(
            1 for msg in consultation.conversation if msg.get("role") == "advisor"
        )
        customer_turns = sum(
            1 for msg in consultation.conversation if msg.get("role") == "customer"
        )
        print("CONVERSATION:")
        print(f"  Total Turns:    {turn_count}")
        print(f"  Advisor Turns:  {advisor_turns}")
        print(f"  Customer Turns: {customer_turns}")
        print()


def show_conversation(session: Session, consultation_id: str) -> None:
    """Show the full conversation transcript.

    Args:
        session: Database session
        consultation_id: Consultation UUID
    """
    try:
        consultation = (
            session.query(Consultation)
            .filter(Consultation.id == UUID(consultation_id))
            .first()
        )
    except ValueError:
        print(f"Error: Invalid consultation ID format: {consultation_id}")
        return

    if not consultation:
        print(f"Consultation not found: {consultation_id}")
        return

    if not consultation.conversation:
        print("No conversation data available for this consultation.")
        return

    meta = consultation.meta or {}

    print(f"\n{'=' * 80}")
    print(f"CONVERSATION TRANSCRIPT")
    print(f"Consultation ID: {consultation.id}")
    print(f"Customer: {meta.get('customer_name', 'Unknown')}")
    print(f"Advisor: {meta.get('advisor_name', 'Unknown')}")
    print(f"Start: {format_datetime(consultation.start_time)}")
    print(f"{'=' * 80}\n")

    for i, message in enumerate(consultation.conversation, 1):
        role = message.get("role", "unknown").upper()
        content = message.get("content", "")

        # Format role with color/style
        if role == "ADVISOR":
            header = f"[Turn {i}] ADVISOR:"
        elif role == "CUSTOMER":
            header = f"[Turn {i}] CUSTOMER:"
        else:
            header = f"[Turn {i}] {role}:"

        print(header)
        print(f"{content}")
        print(f"{'-' * 80}\n")


def export_consultations(
    session: Session,
    training_session_id: Optional[str] = None,
    output_file: str = "consultations.json",
) -> None:
    """Export consultations to JSON file.

    Args:
        session: Database session
        training_session_id: Filter by training session
        output_file: Output file path
    """
    query = session.query(Consultation).order_by(Consultation.start_time)

    if training_session_id:
        query = query.filter(
            Consultation.meta["training_session_id"].astext == training_session_id
        )

    consultations = query.all()

    if not consultations:
        print("No consultations found to export.")
        return

    # Convert to JSON-serializable format
    data = []
    for consultation in consultations:
        data.append(
            {
                "id": str(consultation.id),
                "customer_id": str(consultation.customer_id),
                "advisor_id": str(consultation.advisor_id),
                "conversation": consultation.conversation,
                "outcome": consultation.outcome,
                "start_time": consultation.start_time.isoformat()
                if consultation.start_time
                else None,
                "end_time": consultation.end_time.isoformat()
                if consultation.end_time
                else None,
                "duration_seconds": consultation.duration_seconds,
                "metadata": consultation.meta,
            }
        )

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Exported {len(consultations)} consultation(s) to {output_file}")


def show_statistics(
    session: Session, training_session_id: Optional[str] = None
) -> None:
    """Show statistics for consultations.

    Args:
        session: Database session
        training_session_id: Filter by training session
    """
    query = session.query(Consultation)

    if training_session_id:
        query = query.filter(
            Consultation.meta["training_session_id"].astext == training_session_id
        )

    consultations = query.all()

    if not consultations:
        print("No consultations found.")
        return

    total = len(consultations)
    successful = sum(
        1
        for c in consultations
        if c.outcome and c.outcome.get("successful", False)
    )
    compliant = sum(
        1
        for c in consultations
        if c.outcome and c.outcome.get("fca_compliant", False)
    )

    avg_satisfaction = sum(
        c.outcome.get("customer_satisfaction", 0)
        for c in consultations
        if c.outcome
    ) / total
    avg_comprehension = sum(
        c.outcome.get("comprehension", 0) for c in consultations if c.outcome
    ) / total
    avg_goal_alignment = sum(
        c.outcome.get("goal_alignment", 0) for c in consultations if c.outcome
    ) / total

    avg_duration = sum(c.duration_seconds or 0 for c in consultations) / total

    print(f"\n{'=' * 80}")
    print("CONSULTATION STATISTICS")
    if training_session_id:
        print(f"Session: {training_session_id}")
    print(f"{'=' * 80}\n")

    print(f"Total Consultations:  {total}")
    print(f"Successful:           {successful} ({successful/total*100:.1f}%)")
    print(f"FCA Compliant:        {compliant} ({compliant/total*100:.1f}%)")
    print()

    print("AVERAGE METRICS:")
    print(f"  Satisfaction:   {avg_satisfaction:.2f}/10")
    print(f"  Comprehension:  {avg_comprehension:.2f}/10")
    print(f"  Goal Alignment: {avg_goal_alignment:.2f}/10")
    print(f"  Duration:       {format_duration(int(avg_duration))}")
    print()

    # Time range
    if consultations:
        earliest = min(c.start_time for c in consultations if c.start_time)
        latest = max(c.start_time for c in consultations if c.start_time)
        print("TIME RANGE:")
        print(f"  First: {format_datetime(earliest)}")
        print(f"  Last:  {format_datetime(latest)}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Review and analyze consultations from training sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List consultations")
    list_parser.add_argument("--session", help="Filter by training session ID")
    list_parser.add_argument(
        "--successful", action="store_true", help="Show only successful consultations"
    )
    list_parser.add_argument(
        "--failed", action="store_true", help="Show only failed consultations"
    )
    list_parser.add_argument(
        "--non-compliant", action="store_true", help="Show only non-compliant consultations"
    )
    list_parser.add_argument(
        "--limit", type=int, default=50, help="Maximum results (default: 50)"
    )
    list_parser.add_argument(
        "--show-conversation", action="store_true", help="Show conversation preview"
    )

    # Show command
    show_parser = subparsers.add_parser(
        "show", help="Show detailed consultation information"
    )
    show_parser.add_argument("consultation_id", help="Consultation ID")

    # Conversation command
    conv_parser = subparsers.add_parser(
        "conversation", help="Show conversation transcript"
    )
    conv_parser.add_argument("consultation_id", help="Consultation ID")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export consultations to JSON")
    export_parser.add_argument("--session", help="Filter by training session ID")
    export_parser.add_argument(
        "--output", default="consultations.json", help="Output file (default: consultations.json)"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--session", help="Filter by training session ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Get database session
    db_session = get_session()

    try:
        if args.command == "list":
            successful = True if args.successful else (False if args.failed else None)
            compliant = False if args.non_compliant else None

            list_consultations(
                session=db_session,
                training_session_id=args.session,
                successful=successful,
                compliant=compliant,
                limit=args.limit,
                show_conversation=args.show_conversation,
            )

        elif args.command == "show":
            show_consultation_details(db_session, args.consultation_id)

        elif args.command == "conversation":
            show_conversation(db_session, args.consultation_id)

        elif args.command == "export":
            export_consultations(
                session=db_session,
                training_session_id=args.session,
                output_file=args.output,
            )

        elif args.command == "stats":
            show_statistics(db_session, training_session_id=args.session)

    finally:
        db_session.close()


if __name__ == "__main__":
    main()
