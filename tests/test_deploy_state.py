import os
import subprocess
import tarfile
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DeploymentStateTests(unittest.TestCase):
    def test_redeploy_keeps_client_ids_server_data_and_pending_journal(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text()
        command = textwrap.dedent(
            workflow.split("      remote_deploy_command: |\n", 1)[1]
        )
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / "application"
            for relative, content in [
                ("docker-compose.yml", b"old compose"),
                ("client/ncmma/data/ncmma.db", b"ID ledger"),
                ("client/ncmma/data/ncmma.db.discord-pending/100.json", b"pending ID"),
                ("server/data/cmma.db", b"market database"),
            ]:
                file = target / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(content)
            (home / ".env").write_text("configuration")
            release = home / "release"
            release.mkdir()
            (release / "docker-compose.yml").write_text("new compose")
            with tarfile.open(home / "app.tar.gz", "w:gz") as archive:
                archive.add(
                    release / "docker-compose.yml", arcname="./docker-compose.yml"
                )
            binaries = home / "bin"
            binaries.mkdir()
            (binaries / "sudo").write_text('#!/bin/sh\nexec "$@"\n')
            (binaries / "docker").write_text(
                '#!/bin/sh\nprintf "%s\\n" "$*" >> "$DOCKER_LOG"\n'
            )
            for file in binaries.iterdir():
                file.chmod(0o755)
            command = command.replace(
                "TARGET_DIR='/opt/apps/volatility-monorepo'", f"TARGET_DIR='{target}'"
            )
            env = dict(
                os.environ,
                HOME=str(home),
                PATH=str(binaries) + os.pathsep + os.environ["PATH"],
                DOCKER_LOG=str(home / "docker.log"),
            )
            result = subprocess.run(
                ["bash", "-euc", command], env=env, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (target / "client/ncmma/data/ncmma.db").read_bytes(), b"ID ledger"
            )
            self.assertEqual(
                (
                    target / "client/ncmma/data/ncmma.db.discord-pending/100.json"
                ).read_bytes(),
                b"pending ID",
            )
            self.assertEqual(
                (target / "server/data/cmma.db").read_bytes(), b"market database"
            )
            self.assertEqual((target / "docker-compose.yml").read_text(), "new compose")
            self.assertEqual(
                (home / "docker.log").read_text().splitlines()[0], "compose down"
            )


if __name__ == "__main__":
    unittest.main()
