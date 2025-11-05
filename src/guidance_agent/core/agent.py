"""Base agent class for the guidance agent system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from guidance_agent.core.memory import MemoryStream, MemoryNode
from guidance_agent.core.types import MemoryType


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    agent_id: UUID = None
    name: str = "Agent"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000

    def __post_init__(self):
        if self.agent_id is None:
            self.agent_id = uuid4()


class BaseAgent(ABC):
    """Base class for all agents in the system.

    Implements core agent capabilities:
    - Memory stream for maintaining agent state
    - Perception of environment
    - Planning future actions
    - Reflection on experiences
    """

    def __init__(self, config: AgentConfig):
        """Initialize base agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.memory_stream = MemoryStream()
        self.current_time = datetime.now(timezone.utc)

    def perceive(self, observation: str, importance: Optional[float] = None) -> MemoryNode:
        """Perceive and store an observation.

        Args:
            observation: Text description of observation
            importance: Importance score (0-1), will be rated by LLM if None

        Returns:
            Created memory node
        """
        if importance is None:
            importance = self._rate_importance(observation)

        memory = MemoryNode(
            description=observation,
            timestamp=self.current_time,
            importance=importance,
            memory_type=MemoryType.OBSERVATION,
        )

        self.memory_stream.add(memory)
        return memory

    def reflect(self, trigger_threshold: int = 100) -> list[MemoryNode]:
        """Generate reflections when importance threshold is reached.

        Implements reflection mechanism from Simulacra paper:
        - Triggered when cumulative importance exceeds threshold
        - Generates higher-level insights from recent observations
        - Creates reflection memories with appropriate importance

        Args:
            trigger_threshold: Cumulative importance threshold for reflection

        Returns:
            List of generated reflection memories
        """
        # Get recent observations
        recent_memories = self.memory_stream.retrieve_recent(hours=24, limit=100)

        # Calculate cumulative importance
        cumulative_importance = sum(m.importance for m in recent_memories)

        if cumulative_importance < trigger_threshold:
            return []

        # Generate reflections (to be implemented by subclasses)
        reflections = self._generate_reflections(recent_memories)

        # Add reflections to memory stream
        for reflection_text in reflections:
            reflection = MemoryNode(
                description=reflection_text,
                timestamp=self.current_time,
                importance=self._rate_importance(reflection_text),
                memory_type=MemoryType.REFLECTION,
                citations=[str(m.memory_id) for m in recent_memories[:5]],
            )
            self.memory_stream.add(reflection)

        return [m for m in self.memory_stream.memories if m.memory_type == MemoryType.REFLECTION]

    def plan(self, goal: str) -> MemoryNode:
        """Create a plan to achieve a goal.

        Args:
            goal: Goal to plan for

        Returns:
            Plan memory node
        """
        plan_text = self._generate_plan(goal)

        plan_memory = MemoryNode(
            description=plan_text,
            timestamp=self.current_time,
            importance=0.8,  # Plans are typically important
            memory_type=MemoryType.PLAN,
        )

        self.memory_stream.add(plan_memory)
        return plan_memory

    def update_time(self, new_time: datetime) -> None:
        """Update agent's current time (for virtual time).

        Args:
            new_time: New current time
        """
        self.current_time = new_time

    @abstractmethod
    def _rate_importance(self, observation: str) -> float:
        """Rate the importance of an observation (0-1).

        To be implemented by subclasses using LLM.

        Args:
            observation: Text to rate

        Returns:
            Importance score between 0 and 1
        """
        pass

    @abstractmethod
    def _generate_reflections(self, memories: list[MemoryNode]) -> list[str]:
        """Generate reflection insights from memories.

        To be implemented by subclasses using LLM.

        Args:
            memories: List of memories to reflect on

        Returns:
            List of reflection text strings
        """
        pass

    @abstractmethod
    def _generate_plan(self, goal: str) -> str:
        """Generate a plan to achieve a goal.

        To be implemented by subclasses using LLM.

        Args:
            goal: Goal description

        Returns:
            Plan text
        """
        pass

    def get_state(self) -> dict:
        """Get current agent state.

        Returns:
            Dictionary containing agent state
        """
        return {
            "agent_id": str(self.config.agent_id),
            "name": self.config.name,
            "current_time": self.current_time.isoformat(),
            "memory_count": self.memory_stream.get_memory_count(),
        }

    def save(self, filepath: str) -> None:
        """Save agent state to file.

        Args:
            filepath: Path to save file
        """
        import json

        state = {
            "config": {
                "agent_id": str(self.config.agent_id),
                "name": self.config.name,
                "model": self.config.model,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            },
            "current_time": self.current_time.isoformat(),
            "memories": [m.to_dict() for m in self.memory_stream.memories],
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "BaseAgent":
        """Load agent state from file.

        Args:
            filepath: Path to load file

        Returns:
            Loaded agent instance
        """
        import json
        from guidance_agent.core.memory import MemoryNode

        with open(filepath, "r") as f:
            state = json.load(f)

        config = AgentConfig(
            agent_id=UUID(state["config"]["agent_id"]),
            name=state["config"]["name"],
            model=state["config"]["model"],
            temperature=state["config"]["temperature"],
            max_tokens=state["config"]["max_tokens"],
        )

        agent = cls(config)
        agent.current_time = datetime.fromisoformat(state["current_time"])

        # Restore memories
        for memory_data in state["memories"]:
            memory = MemoryNode.from_dict(memory_data)
            agent.memory_stream.add(memory)

        return agent
