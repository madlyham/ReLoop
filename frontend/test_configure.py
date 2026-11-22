import pathlib
import tempfile
import unittest

import configure


class ConfigureFrontendTests(unittest.TestCase):
    def test_stamps_all_placeholders_and_strips_trailing_slash(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            src = tmp_path / "dist"
            out = tmp_path / "build"
            (src / "assets").mkdir(parents=True)
            (src / "index.html").write_text("<html>ReLoop</html>", encoding="utf-8")
            (src / "assets" / "app.js").write_text(
                'const d="__COGNITO_DOMAIN__",c="__COGNITO_CLIENT_ID__",p="__COGNITO_USER_POOL_ID__";',
                encoding="utf-8",
            )

            configure.configure_bundle(
                src_dir=src,
                out_dir=out,
                pool_id="ap-southeast-1_AbCdEf123",
                client_id="1234567890abcdefghijklmno",
                domain="https://demo-auth.auth.ap-southeast-1.amazoncognito.com/",
            )

            stamped = (out / "assets" / "app.js").read_text(encoding="utf-8")
            self.assertNotIn("__COGNITO_", stamped)
            self.assertIn("ap-southeast-1_AbCdEf123", stamped)
            self.assertIn("1234567890abcdefghijklmno", stamped)
            self.assertIn(
                '"https://demo-auth.auth.ap-southeast-1.amazoncognito.com"',
                stamped,
            )
            self.assertEqual(
                (out / "index.html").read_text(encoding="utf-8"),
                "<html>ReLoop</html>",
            )

    def test_rejects_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            src = tmp_path / "dist"
            out = tmp_path / "build"
            src.mkdir()
            (src / "app.js").write_text(
                "__COGNITO_DOMAIN__ __COGNITO_CLIENT_ID__ __COGNITO_USER_POOL_ID__",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                configure.configure_bundle(
                    src, out, "bad-pool", "1234567890abcdefghijklmno",
                    "https://demo.auth.ap-southeast-1.amazoncognito.com",
                )
            with self.assertRaises(ValueError):
                configure.configure_bundle(
                    src, out, "ap-southeast-1_AbCdEf123", "bad client!",
                    "https://demo.auth.ap-southeast-1.amazoncognito.com",
                )
            with self.assertRaises(ValueError):
                configure.configure_bundle(
                    src, out, "ap-southeast-1_AbCdEf123", "1234567890abcdefghijklmno",
                    "http://insecure.example.com",
                )

    def test_fails_when_placeholder_missing_from_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            src = tmp_path / "dist"
            out = tmp_path / "build"
            src.mkdir()
            (src / "app.js").write_text("console.log('no placeholders');", encoding="utf-8")

            with self.assertRaises(RuntimeError):
                configure.configure_bundle(
                    src,
                    out,
                    "ap-southeast-1_AbCdEf123",
                    "1234567890abcdefghijklmno",
                    "https://demo.auth.ap-southeast-1.amazoncognito.com",
                )


if __name__ == "__main__":
    unittest.main()
