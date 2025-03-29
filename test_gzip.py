# test_ping.py
import os
from subprocess import run

def create_test_file(file_name):
    sample_text = """This is a dummy sample text file.
    It contains some random lines of text.
    This is line 3 of the text file.
    Here is line 4, just for testing purposes.
    Feel free to modify or extend this text.
    """
    # Open the file in write mode ('w') and write the sample text to it
    with open(file_name, 'w') as file:
        file.write(sample_text)

def test_help(capfd):
    process=run(['/usr/bin/gzip','-h'])
    stdout, stderr = capfd.readouterr()
    assert process.returncode == 0
    assert "Usage:" in stdout 

def test_compress_decompress(capfd):
    create_test_file("sample.txt")
    process=run(['/usr/bin/gzip','sample.txt'])
    stdout, stderr = capfd.readouterr()
    assert process.returncode == 0
    process=run(['/usr/bin/gzip','-d','sample.txt'])
    stdout, stderr = capfd.readouterr()
    with open("sample.txt") as file:
        assert(file.readline().startswith("This is a dummy sample"))
    os.remove("sample.txt")

