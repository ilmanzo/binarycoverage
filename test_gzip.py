# test_ping.py

from subprocess import run

def test_help(capfd):
    process=run(['/usr/bin/gzip','-h'])
    stdout, stderr = capfd.readouterr()
    assert process.returncode == 0
    assert "Usage:" in stdout 
