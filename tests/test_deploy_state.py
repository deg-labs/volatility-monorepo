import os
import re
import subprocess
import tarfile
import tempfile
import unittest
from urllib.request import urlopen
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DeploymentStateTests(unittest.TestCase):
    def test_redeploy_keeps_client_ids_server_data_and_pending_journal(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text()
        match = re.search(r"gce-deploy\.yml@([0-9a-f]{40})", workflow)
        self.assertIsNotNone(match, "shared workflow must be pinned to a commit")
        url = (
            "https://raw.githubusercontent.com/deg-labs/github-workflows/"
            f"{match.group(1)}/scripts/deploy_remote.sh"
        )
        with urlopen(url, timeout=30) as response:
            command = response.read().decode()
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
            (home / "gce-123-1-env").write_text("configuration")
            release = home / "release"
            release.mkdir()
            (release / "docker-compose.yml").write_text("new compose")
            with tarfile.open(home / "gce-123-1-archive.tgz", "w:gz") as archive:
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
            command = command.replace('target="/opt/apps/$app"', f'target="{target}"')
            env = dict(
                os.environ,
                HOME=str(home),
                PATH=str(binaries) + os.pathsep + os.environ["PATH"],
                DOCKER_LOG=str(home / "docker.log"),
            )
            result = subprocess.run(
                ["bash", "-eu", "-s", "--", "compose", "volatility-monorepo", "", "gce-123-1"], input=command, env=env, capture_output=True, text=True
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
                (home / "docker.log").read_text().splitlines()[0], "compose up -d --build --remove-orphans"
            )


if __name__ == "__main__":
    unittest.main()
