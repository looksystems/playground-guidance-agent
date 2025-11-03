"""Virtual training environment for advisor agents.

This module provides the main VirtualEnvironment class that orchestrates
complete training sessions with time acceleration, consultation management,
and learning integration.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from uuid import uuid4

from guidance_agent.environment.time_manager import VirtualTimeManager
from guidance_agent.environment.orchestrator import EventOrchestrator, ConsultationResult
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.customer.generator import generate_customer_profile
from guidance_agent.learning.case_learning import learn_from_successful_consultation
from guidance_agent.learning.reflection import learn_from_failure
from guidance_agent.retrieval.retriever import CaseBase, RulesBase
from guidance_agent.core.types import AdvisorProfile, CustomerProfile, OutcomeResult
from guidance_agent.core.database import get_session, Consultation


@dataclass
class TrainingMetrics:
    """Metrics tracked during training session.

    Attributes:
        total_consultations: Total number of consultations completed
        successful_consultations: Number of successful consultations
        total_satisfaction: Sum of customer satisfaction scores
        total_comprehension: Sum of comprehension scores
        compliance_violations: Number of compliance violations
        cases_learned: Number of cases added to case base
        rules_learned: Number of rules added to rules base
    """

    total_consultations: int = 0
    successful_consultations: int = 0
    total_satisfaction: float = 0.0
    total_comprehension: float = 0.0
    compliance_violations: int = 0
    cases_learned: int = 0
    rules_learned: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_consultations == 0:
            return 0.0
        return self.successful_consultations / self.total_consultations

    @property
    def avg_satisfaction(self) -> float:
        """Calculate average satisfaction."""
        if self.total_consultations == 0:
            return 0.0
        return self.total_satisfaction / self.total_consultations

    @property
    def avg_comprehension(self) -> float:
        """Calculate average comprehension."""
        if self.total_consultations == 0:
            return 0.0
        return self.total_comprehension / self.total_consultations

    @property
    def compliance_rate(self) -> float:
        """Calculate compliance rate."""
        if self.total_consultations == 0:
            return 1.0
        violations = self.compliance_violations
        return 1.0 - (violations / self.total_consultations)


class VirtualEnvironment:
    """Virtual training environment for advisor agents.

    The environment provides:
    - Time acceleration for rapid experience accumulation
    - Automated customer generation
    - Multi-turn consultation orchestration
    - Outcome simulation and learning integration
    - Progress tracking and metrics

    Example:
        >>> env = VirtualEnvironment(advisor_profile=profile)
        >>> env.run_training_session(num_consultations=1000)
        >>> metrics = env.get_metrics()
        >>> print(f"Success rate: {metrics.success_rate:.2%}")
    """

    def __init__(
        self,
        advisor_profile: AdvisorProfile,
        acceleration_factor: int = 60,
        max_turns_per_consultation: int = 20,
        progress_interval: int = 100,
        persist_consultations: bool = True,
        training_session_id: Optional[str] = None,
    ):
        """Initialize virtual environment.

        Args:
            advisor_profile: Profile for the advisor agent
            acceleration_factor: Time acceleration (default 60x)
            max_turns_per_consultation: Max conversation turns
            progress_interval: How often to display progress (every N consultations)
            persist_consultations: Whether to save consultations to database
            training_session_id: Optional session ID for grouping consultations
        """
        self.advisor = AdvisorAgent(profile=advisor_profile)
        self.time_manager = VirtualTimeManager(acceleration_factor=acceleration_factor)
        self.orchestrator = EventOrchestrator(max_turns=max_turns_per_consultation)
        self.metrics = TrainingMetrics()
        self.progress_interval = progress_interval
        self.persist_consultations = persist_consultations
        self.training_session_id = training_session_id or str(uuid4())

        # Generate advisor ID if not present
        self.advisor_id = uuid4()

        # Initialize learning infrastructure
        session = get_session()
        self.case_base = CaseBase(session=session)
        self.rules_base = RulesBase(session=session)
        self.db_session = session

    def run_single_consultation(self) -> ConsultationResult:
        """Run a single consultation with a generated customer.

        Returns:
            ConsultationResult with conversation and outcome

        Example:
            >>> result = env.run_single_consultation()
            >>> print(f"Turns: {result.turn_count}")
            >>> print(f"Success: {result.outcome.successful}")
        """
        # Generate customer
        customer_profile = generate_customer_profile()
        customer = CustomerAgent(profile=customer_profile)

        # Record virtual timestamp
        consultation_start = self.time_manager.get_virtual_time()

        # Run consultation
        result = self.orchestrator.run_consultation(self.advisor, customer)

        # Calculate consultation end time
        consultation_end = self.time_manager.get_virtual_time()
        duration = int((consultation_end - consultation_start).total_seconds())

        # Advance time (typical consultation = 30-60 minutes)
        # In virtual time with 60x acceleration: 0.5 hours real = 30 hours virtual
        self.time_manager.advance(hours=0.5)

        # Save consultation to database if enabled
        if self.persist_consultations:
            self._save_consultation(
                customer_profile=customer_profile,
                conversation_history=result.conversation_history,
                outcome=result.outcome,
                start_time=consultation_start,
                end_time=consultation_end,
                duration_seconds=duration,
            )

        # Process outcome and learn
        self._process_outcome(customer_profile, result.conversation_history, result.outcome)

        return result

    def run_training_session(
        self,
        num_consultations: int,
        display_progress: bool = True,
    ) -> TrainingMetrics:
        """Run a training session with multiple consultations.

        Args:
            num_consultations: Number of consultations to run
            display_progress: Whether to display progress updates

        Returns:
            TrainingMetrics with session statistics

        Example:
            >>> metrics = env.run_training_session(num_consultations=1000)
            >>> print(f"Completed {metrics.total_consultations} consultations")
            >>> print(f"Success rate: {metrics.success_rate:.2%}")
        """
        print(f"Starting training session: {num_consultations} consultations")
        print(f"Time acceleration: {self.time_manager.acceleration_factor}x")
        print(f"Virtual start time: {self.time_manager.get_virtual_time()}")
        print("-" * 60)

        for i in range(num_consultations):
            # Run consultation
            result = self.run_single_consultation()

            # Update metrics
            self.metrics.total_consultations += 1
            if result.outcome.successful:
                self.metrics.successful_consultations += 1

            self.metrics.total_satisfaction += result.outcome.customer_satisfaction
            self.metrics.total_comprehension += result.outcome.comprehension

            if not result.outcome.fca_compliant:
                self.metrics.compliance_violations += 1

            # Display progress
            if display_progress and (i + 1) % self.progress_interval == 0:
                self._display_progress(
                    current=i + 1,
                    total=num_consultations,
                    success_rate=self.metrics.success_rate,
                    avg_satisfaction=self.metrics.avg_satisfaction,
                    compliance_rate=self.metrics.compliance_rate,
                )

        # Final summary
        print("\n" + "=" * 60)
        print("Training session complete!")
        print(f"Total consultations: {self.metrics.total_consultations}")
        print(f"Success rate: {self.metrics.success_rate:.2%}")
        print(f"Avg satisfaction: {self.metrics.avg_satisfaction:.2f}/10")
        print(f"Avg comprehension: {self.metrics.avg_comprehension:.2f}/10")
        print(f"Compliance rate: {self.metrics.compliance_rate:.2%}")
        print(f"Cases learned: {self.metrics.cases_learned}")
        print(f"Rules learned: {self.metrics.rules_learned}")
        print(f"Virtual time elapsed: {self.time_manager.get_elapsed_virtual_time()}")
        print("=" * 60)

        return self.metrics

    def get_metrics(self) -> TrainingMetrics:
        """Get current training metrics.

        Returns:
            TrainingMetrics object with current statistics
        """
        return self.metrics

    def _process_outcome(
        self,
        customer_profile: CustomerProfile,
        conversation_history: list,
        outcome: OutcomeResult,
    ) -> None:
        """Process consultation outcome and trigger learning.

        Args:
            customer_profile: Customer profile
            conversation_history: Full conversation
            outcome: Consultation outcome
        """
        # Extract guidance from conversation (last advisor message before outcome)
        advisor_messages = [
            msg["content"]
            for msg in conversation_history
            if msg["role"] == "advisor"
        ]
        guidance_provided = " ".join(advisor_messages) if advisor_messages else ""

        if outcome.successful:
            # Learn from success
            learn_from_successful_consultation(
                case_base=self.case_base,
                customer_profile=customer_profile,
                guidance_provided=guidance_provided,
                outcome=outcome,
            )
            self.metrics.cases_learned += 1
        else:
            # Learn from failure
            try:
                reflection = learn_from_failure(
                    rules_base=self.rules_base,
                    customer_profile=customer_profile,
                    guidance_provided=guidance_provided,
                    outcome=outcome,
                )
                if reflection:  # If a rule was successfully generated
                    self.metrics.rules_learned += 1
            except Exception:
                # Don't fail training if learning fails
                pass

    def _display_progress(
        self,
        current: int,
        total: int,
        success_rate: float,
        avg_satisfaction: float,
        compliance_rate: float,
    ) -> None:
        """Display progress update.

        Args:
            current: Current consultation number
            total: Total consultations
            success_rate: Current success rate
            avg_satisfaction: Average satisfaction
            compliance_rate: Compliance rate
        """
        pct = (current / total) * 100
        print(
            f"[{current}/{total}] {pct:5.1f}% | "
            f"Success: {success_rate:5.1%} | "
            f"Satisfaction: {avg_satisfaction:4.2f} | "
            f"Compliance: {compliance_rate:5.1%}"
        )

    def _save_consultation(
        self,
        customer_profile: CustomerProfile,
        conversation_history: list,
        outcome: OutcomeResult,
        start_time: datetime,
        end_time: datetime,
        duration_seconds: int,
    ) -> None:
        """Save consultation to database.

        Args:
            customer_profile: Customer profile
            conversation_history: Full conversation history
            outcome: Consultation outcome
            start_time: Start timestamp
            end_time: End timestamp
            duration_seconds: Duration in seconds
        """
        try:
            consultation = Consultation(
                id=uuid4(),
                customer_id=customer_profile.customer_id,
                advisor_id=self.advisor_id,
                conversation=conversation_history,
                outcome=outcome.to_dict(),
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                meta={
                    "training_session_id": self.training_session_id,
                    "acceleration_factor": self.time_manager.acceleration_factor,
                    "customer_age": customer_profile.demographics.age if customer_profile.demographics else None,
                    "customer_gender": customer_profile.demographics.gender if customer_profile.demographics else None,
                    "advisor_name": self.advisor.profile.name,
                },
            )
            self.db_session.add(consultation)
            self.db_session.commit()
        except Exception as e:
            # Don't fail training if database save fails
            print(f"Warning: Failed to save consultation: {e}")
            self.db_session.rollback()
