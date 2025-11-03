"""Unit tests for VirtualTimeManager."""

import pytest
from datetime import datetime, timedelta
import time

from guidance_agent.environment.time_manager import VirtualTimeManager


class TestVirtualTimeManager:
    """Test virtual time management."""

    def test_initialization_default_acceleration(self):
        """Test time manager initializes with default 60x acceleration."""
        tm = VirtualTimeManager()

        assert tm.acceleration_factor == 60
        assert tm.virtual_time is not None
        assert tm.real_time_start is not None

    def test_initialization_custom_acceleration(self):
        """Test time manager initializes with custom acceleration."""
        tm = VirtualTimeManager(acceleration_factor=100)

        assert tm.acceleration_factor == 100

    def test_initialization_custom_start_time(self):
        """Test time manager initializes with custom start time."""
        start_time = datetime(2025, 1, 1, 9, 0, 0)
        tm = VirtualTimeManager(virtual_start_time=start_time)

        assert tm.virtual_time == start_time

    def test_get_current_virtual_time(self):
        """Test getting current virtual time."""
        tm = VirtualTimeManager()

        current = tm.get_virtual_time()
        assert isinstance(current, datetime)

    def test_advance_by_seconds(self):
        """Test advancing virtual time by seconds."""
        tm = VirtualTimeManager(acceleration_factor=60)
        start = tm.get_virtual_time()

        # Advance 1 real second = 60 virtual seconds
        tm.advance(seconds=1)

        end = tm.get_virtual_time()
        delta = (end - start).total_seconds()

        # Should be 60 seconds (1 minute)
        assert abs(delta - 60) < 1  # Allow small floating point error

    def test_advance_by_minutes(self):
        """Test advancing virtual time by minutes."""
        tm = VirtualTimeManager(acceleration_factor=60)
        start = tm.get_virtual_time()

        # Advance 1 real minute = 60 virtual minutes = 1 virtual hour
        tm.advance(minutes=1)

        end = tm.get_virtual_time()
        delta_hours = (end - start).total_seconds() / 3600

        assert abs(delta_hours - 1) < 0.01

    def test_advance_by_hours(self):
        """Test advancing virtual time by hours."""
        tm = VirtualTimeManager(acceleration_factor=60)
        start = tm.get_virtual_time()

        # Advance 1 real hour = 60 virtual hours = 2.5 virtual days
        tm.advance(hours=1)

        end = tm.get_virtual_time()
        delta_days = (end - start).total_seconds() / 86400

        assert abs(delta_days - 2.5) < 0.01

    def test_advance_by_days(self):
        """Test advancing virtual time by days."""
        tm = VirtualTimeManager(acceleration_factor=60)
        start = tm.get_virtual_time()

        # Advance 1 real day = 60 virtual days
        tm.advance(days=1)

        end = tm.get_virtual_time()
        delta_days = (end - start).total_seconds() / 86400

        assert abs(delta_days - 60) < 0.01

    def test_advance_does_not_affect_real_time(self):
        """Test that advancing virtual time doesn't affect real time tracking."""
        tm = VirtualTimeManager()
        real_start = tm.real_time_start

        tm.advance(hours=1)

        # Real time start should not change
        assert tm.real_time_start == real_start

    def test_get_elapsed_real_time(self):
        """Test getting elapsed real time."""
        tm = VirtualTimeManager()

        # Sleep a tiny bit
        time.sleep(0.01)

        elapsed = tm.get_elapsed_real_time()

        assert elapsed.total_seconds() > 0
        assert elapsed.total_seconds() < 1  # Should be milliseconds

    def test_get_elapsed_virtual_time(self):
        """Test getting elapsed virtual time."""
        tm = VirtualTimeManager(acceleration_factor=60)
        virtual_start = tm.virtual_time

        tm.advance(seconds=10)

        elapsed = tm.get_elapsed_virtual_time()

        # 10 real seconds * 60 = 600 virtual seconds = 10 minutes
        assert abs(elapsed.total_seconds() - 600) < 1

    def test_calculate_virtual_duration(self):
        """Test calculating virtual duration from real duration."""
        tm = VirtualTimeManager(acceleration_factor=60)

        real_duration = timedelta(hours=1)
        virtual_duration = tm.calculate_virtual_duration(real_duration)

        # 1 real hour * 60 = 60 virtual hours = 2.5 days
        expected_days = 2.5
        actual_days = virtual_duration.total_seconds() / 86400

        assert abs(actual_days - expected_days) < 0.01

    def test_calculate_real_duration(self):
        """Test calculating real duration from virtual duration."""
        tm = VirtualTimeManager(acceleration_factor=60)

        virtual_duration = timedelta(hours=60)
        real_duration = tm.calculate_real_duration(virtual_duration)

        # 60 virtual hours / 60 = 1 real hour
        assert abs(real_duration.total_seconds() - 3600) < 1

    def test_time_until_virtual_event(self):
        """Test calculating time until virtual event."""
        tm = VirtualTimeManager(acceleration_factor=60)

        # Event in 60 virtual hours (2.5 virtual days)
        event_time = tm.get_virtual_time() + timedelta(hours=60)

        real_time_until = tm.time_until_event(event_time)

        # Should be 1 real hour
        assert abs(real_time_until.total_seconds() - 3600) < 1

    def test_time_until_past_event(self):
        """Test calculating time until past event (negative)."""
        tm = VirtualTimeManager(acceleration_factor=60)

        # Event in the past
        event_time = tm.get_virtual_time() - timedelta(hours=60)

        real_time_until = tm.time_until_event(event_time)

        # Should be negative
        assert real_time_until.total_seconds() < 0

    def test_reset_to_time(self):
        """Test resetting virtual time to specific time."""
        tm = VirtualTimeManager()

        new_time = datetime(2025, 6, 1, 12, 0, 0)
        tm.reset_to(new_time)

        assert tm.get_virtual_time() == new_time

    def test_different_acceleration_factors(self):
        """Test different acceleration factors."""
        # Test 1x (no acceleration)
        tm1 = VirtualTimeManager(acceleration_factor=1)
        start1 = tm1.get_virtual_time()
        tm1.advance(seconds=10)
        delta1 = (tm1.get_virtual_time() - start1).total_seconds()
        assert abs(delta1 - 10) < 1

        # Test 100x
        tm100 = VirtualTimeManager(acceleration_factor=100)
        start100 = tm100.get_virtual_time()
        tm100.advance(seconds=10)
        delta100 = (tm100.get_virtual_time() - start100).total_seconds()
        assert abs(delta100 - 1000) < 1

    def test_virtual_time_string_representation(self):
        """Test string representation of virtual time."""
        tm = VirtualTimeManager()

        repr_str = repr(tm)

        assert "VirtualTimeManager" in repr_str
        assert "acceleration" in repr_str.lower()
