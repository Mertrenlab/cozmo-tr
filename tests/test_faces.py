"""Tests for generated OLED expressions without physical hardware."""

import unittest

from cozmo_tr.faces import FACE_HEIGHT, FACE_WIDTH, render_face


class FaceRendererTests(unittest.TestCase):
    """Ensure every supported expression is a Cozmo-sized monochrome image."""

    def test_renders_supported_expressions(self) -> None:
        for name in ("happy", "sad", "surprised", "angry", "neutral"):
            with self.subTest(name=name):
                image = render_face(name)
                self.assertEqual(image.size, (FACE_WIDTH, FACE_HEIGHT))
                self.assertEqual(image.mode, "1")

    def test_rejects_unknown_expression(self) -> None:
        with self.assertRaises(ValueError):
            render_face("sleepy")


if __name__ == "__main__":
    unittest.main()
