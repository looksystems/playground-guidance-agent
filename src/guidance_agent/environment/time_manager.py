"""Virtual time management for rapid training acceleration.

This module provides time acceleration functionality, allowing virtual time to pass
faster than real time. This enables advisors to gain years of experience in days.

Based on Agent Hospital's time acceleration approach.
"""

from datetime import datetime, timedelta
from typing import Optional


class VirtualTimeManager:
    """Manages virtual time acceleration for training environment.

    Virtual time passes faster than real time by an acceleration factor.
    Default factor of 60 means:
    - 1 real second = 60 virtual seconds (1 virtual minute)
    - 1 real hour = 60 virtual hours (2.5 virtual days)
    - 1 real day = 60 virtual days (~2 virtual months)
    - 1 real week = ~1 virtual year

    This allows advisors to accumulate experience rapidly while maintaining
    realistic timestamps for consultation records.

    Example:
        >>> tm = VirtualTimeManager(acceleration_factor=60)
        >>> start = tm.get_virtual_time()
        >>> tm.advance(hours=1)  # 1 real hour passes
        >>> end = tm.get_virtual_time()
        >>> # 60 virtual hours (2.5 days) have passed
    """

    def __init__(
        self,
        acceleration_factor: int = 60,
        virtual_start_time: Optional[datetime] = None,
    ):
        """Initialize virtual time manager.

        Args:
            acceleration_factor: How many virtual time units per real time unit.
                Default 60 means 1 real hour = 60 virtual hours.
            virtual_start_time: Starting virtual time. Defaults to current time.
        """
        self.acceleration_factor = acceleration_factor
        self.virtual_time = virtual_start_time or datetime.now()
        self._initial_virtual_time = self.virtual_time  # Store initial virtual time
        self.real_time_start = datetime.now()

    def get_virtual_time(self) -> datetime:
        """Get current virtual time.

        Returns:
            Current virtual time as datetime
        """
        return self.virtual_time

    def advance(
        self,
        seconds: float = 0,
        minutes: float = 0,
        hours: float = 0,
        days: float = 0,
    ) -> None:
        """Advance virtual time based on real time elapsed.

        All time units are in REAL time, and will be multiplied by
        acceleration_factor to get virtual time advancement.

        Args:
            seconds: Real seconds elapsed
            minutes: Real minutes elapsed
            hours: Real hours elapsed
            days: Real days elapsed

        Example:
            >>> tm = VirtualTimeManager(acceleration_factor=60)
            >>> tm.advance(hours=1)  # 1 real hour = 60 virtual hours
        """
        # Convert all to seconds
        total_real_seconds = (
            seconds
            + (minutes * 60)
            + (hours * 3600)
            + (days * 86400)
        )

        # Apply acceleration
        virtual_seconds = total_real_seconds * self.acceleration_factor

        # Advance virtual time
        self.virtual_time += timedelta(seconds=virtual_seconds)

    def get_elapsed_real_time(self) -> timedelta:
        """Get elapsed real time since initialization.

        Returns:
            Timedelta of real time elapsed
        """
        return datetime.now() - self.real_time_start

    def get_elapsed_virtual_time(self) -> timedelta:
        """Get elapsed virtual time since initialization.

        Returns:
            Timedelta of virtual time elapsed
        """
        return self.virtual_time - self._initial_virtual_time

    def calculate_virtual_duration(self, real_duration: timedelta) -> timedelta:
        """Calculate virtual duration from real duration.

        Args:
            real_duration: Duration in real time

        Returns:
            Equivalent duration in virtual time

        Example:
            >>> tm = VirtualTimeManager(acceleration_factor=60)
            >>> real = timedelta(hours=1)
            >>> virtual = tm.calculate_virtual_duration(real)
            >>> # virtual is 60 hours (2.5 days)
        """
        virtual_seconds = real_duration.total_seconds() * self.acceleration_factor
        return timedelta(seconds=virtual_seconds)

    def calculate_real_duration(self, virtual_duration: timedelta) -> timedelta:
        """Calculate real duration from virtual duration.

        Args:
            virtual_duration: Duration in virtual time

        Returns:
            Equivalent duration in real time

        Example:
            >>> tm = VirtualTimeManager(acceleration_factor=60)
            >>> virtual = timedelta(hours=60)
            >>> real = tm.calculate_real_duration(virtual)
            >>> # real is 1 hour
        """
        real_seconds = virtual_duration.total_seconds() / self.acceleration_factor
        return timedelta(seconds=real_seconds)

    def time_until_event(self, event_time: datetime) -> timedelta:
        """Calculate real time until virtual event.

        Args:
            event_time: Virtual time when event occurs

        Returns:
            Real time until event (may be negative if event is in past)

        Example:
            >>> tm = VirtualTimeManager(acceleration_factor=60)
            >>> event = tm.get_virtual_time() + timedelta(hours=60)
            >>> real_time = tm.time_until_event(event)
            >>> # real_time is 1 hour
        """
        virtual_delta = event_time - self.virtual_time
        return self.calculate_real_duration(virtual_delta)

    def reset_to(self, virtual_time: datetime) -> None:
        """Reset virtual time to a specific time.

        Args:
            virtual_time: New virtual time to set
        """
        self.virtual_time = virtual_time

    def __repr__(self) -> str:
        """String representation of time manager.

        Returns:
            String showing acceleration factor and current times
        """
        return (
            f"VirtualTimeManager(acceleration={self.acceleration_factor}x, "
            f"virtual_time={self.virtual_time.isoformat()})"
        )
