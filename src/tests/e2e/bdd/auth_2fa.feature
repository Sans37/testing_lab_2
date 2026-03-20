Feature: Two-factor authentication and password change
  As a system user
  I want to authenticate with 2FA and change password securely
  So that access is protected and controlled

  Scenario: Successful login with 2FA
    Given a technical user exists
    When the user logs in with correct password
    Then 2FA is required
    When the user verifies the 2FA code
    Then an access token is issued

  Scenario: Lockout and recovery after failed attempts
    Given a technical user exists
    When the user submits an incorrect password 3 times
    Then the account is locked
    When the user requests unlock and confirms the code
    Then login works again

  Scenario: Planned password change with 2FA
    Given a technical user exists
    And the user is logged in with 2FA
    When the user requests a password change OTP
    And the user confirms password change
    Then login with the new password succeeds
