"""Tests for admin settings API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch


@pytest.fixture
def admin_headers():
    """Admin authorization headers."""
    return {"Authorization": "Bearer admin-token"}


@pytest.fixture
def sample_settings():
    """Sample settings data."""
    return {
        "systemName": "Pension Guidance Service",
        "supportEmail": "support@pensionguidance.com",
        "sessionTimeout": 30,
        "fcaComplianceEnabled": True,
        "riskAssessmentRequired": True,
        "autoArchive": False,
        "emailNotifications": True,
        "complianceAlerts": True,
        "dailyDigest": False,
        "aiModel": "gpt-4",
        "temperature": 0.7,
        "maxTokens": 2000
    }


@pytest.mark.asyncio
async def test_get_settings_success(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test getting admin settings successfully."""
    response = await client_with_real_db.get("/api/admin/settings", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # Check required fields are present
    assert "systemName" in data
    assert "supportEmail" in data
    assert "sessionTimeout" in data
    assert "fcaComplianceEnabled" in data
    assert "riskAssessmentRequired" in data
    assert "autoArchive" in data
    assert "emailNotifications" in data
    assert "complianceAlerts" in data
    assert "dailyDigest" in data
    assert "aiModel" in data
    assert "temperature" in data
    assert "maxTokens" in data

    # Check data types
    assert isinstance(data["systemName"], str)
    assert isinstance(data["supportEmail"], str)
    assert isinstance(data["sessionTimeout"], int)
    assert isinstance(data["fcaComplianceEnabled"], bool)
    assert isinstance(data["riskAssessmentRequired"], bool)
    assert isinstance(data["autoArchive"], bool)
    assert isinstance(data["emailNotifications"], bool)
    assert isinstance(data["complianceAlerts"], bool)
    assert isinstance(data["dailyDigest"], bool)
    assert isinstance(data["aiModel"], str)
    assert isinstance(data["temperature"], (int, float))
    assert isinstance(data["maxTokens"], int)


@pytest.mark.asyncio
async def test_get_settings_no_auth(client: AsyncClient):
    """Test getting settings without admin auth."""
    response = await client.get("/api/admin/settings")

    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_settings_success(
    client_with_real_db: AsyncClient, admin_headers, sample_settings
):
    """Test updating admin settings successfully."""
    # Save original settings to restore later
    original_response = await client_with_real_db.get("/api/admin/settings", headers=admin_headers)
    original_settings = original_response.json()

    # Update some settings
    updated_settings = sample_settings.copy()
    updated_settings["systemName"] = "Updated Pension Service"
    updated_settings["sessionTimeout"] = 45
    updated_settings["fcaComplianceEnabled"] = False
    updated_settings["temperature"] = 0.8

    response = await client_with_real_db.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=updated_settings
    )

    assert response.status_code == 200
    data = response.json()

    # Check updated values are returned
    assert data["systemName"] == "Updated Pension Service"
    assert data["sessionTimeout"] == 45
    assert data["fcaComplianceEnabled"] is False
    assert data["temperature"] == 0.8

    # Verify settings persist by fetching again
    get_response = await client_with_real_db.get("/api/admin/settings", headers=admin_headers)
    assert get_response.status_code == 200
    get_data = get_response.json()

    assert get_data["systemName"] == "Updated Pension Service"
    assert get_data["sessionTimeout"] == 45
    assert get_data["fcaComplianceEnabled"] is False
    assert get_data["temperature"] == 0.8

    # Restore original settings for other tests
    await client_with_real_db.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=original_settings
    )


@pytest.mark.asyncio
async def test_update_settings_no_auth(client: AsyncClient, sample_settings):
    """Test updating settings without admin auth."""
    response = await client.put("/api/admin/settings", json=sample_settings)

    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_settings_invalid_email(
    client: AsyncClient, admin_headers, sample_settings
):
    """Test updating settings with invalid email."""
    invalid_settings = sample_settings.copy()
    invalid_settings["supportEmail"] = "not-an-email"

    response = await client.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=invalid_settings
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_settings_invalid_session_timeout(
    client: AsyncClient, admin_headers, sample_settings
):
    """Test updating settings with invalid session timeout."""
    invalid_settings = sample_settings.copy()
    invalid_settings["sessionTimeout"] = -5

    response = await client.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=invalid_settings
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_settings_invalid_temperature(
    client: AsyncClient, admin_headers, sample_settings
):
    """Test updating settings with invalid temperature."""
    invalid_settings = sample_settings.copy()
    invalid_settings["temperature"] = 3.0  # Max is 2.0

    response = await client.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=invalid_settings
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_settings_invalid_max_tokens(
    client: AsyncClient, admin_headers, sample_settings
):
    """Test updating settings with invalid max tokens."""
    invalid_settings = sample_settings.copy()
    invalid_settings["maxTokens"] = -100

    response = await client.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=invalid_settings
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_settings_missing_fields(
    client: AsyncClient, admin_headers
):
    """Test updating settings with missing required fields."""
    incomplete_settings = {
        "systemName": "Test"
        # Missing other required fields
    }

    response = await client.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=incomplete_settings
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_settings_default_values(
    client_with_real_db: AsyncClient, admin_headers
):
    """Test that settings have sensible default values on first access."""
    response = await client_with_real_db.get("/api/admin/settings", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()

    # Check values are reasonable (not checking exact defaults since DB might have been modified by other tests)
    assert isinstance(data["systemName"], str) and len(data["systemName"]) > 0
    assert "@" in data["supportEmail"] and "." in data["supportEmail"]
    assert data["sessionTimeout"] >= 1  # Minimum from constraint
    assert data["temperature"] >= 0.0 and data["temperature"] <= 2.0
    assert data["maxTokens"] >= 1  # Minimum from constraint


@pytest.mark.asyncio
async def test_settings_persistence_across_requests(
    client_with_real_db: AsyncClient, admin_headers, sample_settings
):
    """Test that settings persist across multiple requests."""
    # Save original settings to restore later
    original_response = await client_with_real_db.get("/api/admin/settings", headers=admin_headers)
    original_settings = original_response.json()

    # First update
    updated_settings = sample_settings.copy()
    updated_settings["systemName"] = "Persistent Service"

    response1 = await client_with_real_db.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=updated_settings
    )
    assert response1.status_code == 200

    # Multiple gets should return the same values
    for _ in range(3):
        response = await client_with_real_db.get("/api/admin/settings", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["systemName"] == "Persistent Service"

    # Another update
    updated_settings["systemName"] = "Twice Updated Service"
    response2 = await client_with_real_db.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=updated_settings
    )
    assert response2.status_code == 200

    # Verify new value persists
    response3 = await client_with_real_db.get("/api/admin/settings", headers=admin_headers)
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["systemName"] == "Twice Updated Service"

    # Restore original settings for other tests
    await client_with_real_db.put(
        "/api/admin/settings",
        headers=admin_headers,
        json=original_settings
    )
