import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.factory.session import SessionState, load_session


class TestSession(unittest.TestCase):
    def test_session_save_and_load_roundtrip(self) -> None:
        with TemporaryDirectory() as tmp:
            session_dir = Path(tmp)
            session = SessionState.new()
            session.add_turn("user", "hello")
            session.save(session_dir)

            loaded = load_session(session_dir, session.session_id)
            self.assertEqual(loaded.session_id, session.session_id)
            self.assertEqual(len(loaded.turns), 1)
            self.assertEqual(loaded.turns[0]["content"], "hello")


if __name__ == "__main__":
    unittest.main()
