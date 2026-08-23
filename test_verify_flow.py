import unittest

from verify_flow import Signup, verification_message


class SignupDecisionTest(unittest.TestCase):
    def test_email_address_requires_verification_message(self):
        signup = Signup("tenant@example.com", "Mina", "tap", "lease.pdf", "inspection")
        decision = verification_message(signup, "https://example.com/verify/1")
        self.assertTrue(decision["needs_verification"])
        self.assertEqual(decision["to"], "tenant@example.com")
        self.assertIn("Verify email", decision["html"])


if __name__ == "__main__":
    unittest.main()
