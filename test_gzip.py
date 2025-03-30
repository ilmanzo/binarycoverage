# test_gzip.py
import os,re
from subprocess import run

PROGRAM='/usr/bin/gzip'

# program should display help
def test_help(capfd):
    process=run([PROGRAM,'-h'])
    stdout, stderr = capfd.readouterr()     
    assert process.returncode == 0
    assert "Usage:" in stdout 

# program should display version information
def test_version(capfd):
    process=run([PROGRAM,'-V'])
    stdout, stderr = capfd.readouterr()
    assert process.returncode == 0
    assert "This is free software" in stdout 
    assert re.search(r"gzip \d.\d\d", stdout)

# program should fail when given a non existing file
def test_compress_non_existent():
    process=run([PROGRAM,'foobar'])
    assert process.returncode==1

# program should display a license
def test_license(capfd):
    process=run([PROGRAM,'--license'])
    assert process.returncode==0
    stdout, stderr = capfd.readouterr()
    assert 'the GNU General Public License' in stdout

SAMPLE_FILE='sample.txt'

# program should compress and de-compress a file
def test_compress_decompress(capfd):
    create_test_file(SAMPLE_FILE)
    with open(SAMPLE_FILE) as file:
        content=file.readlines()
    process=run([PROGRAM,SAMPLE_FILE])
    assert process.returncode == 0
    compressed_file=SAMPLE_FILE+".gz"
    # decompress and read back content
    process=run([PROGRAM,'-d',compressed_file])
    assert process.returncode == 0
    with open(SAMPLE_FILE) as file:
        assert(file.readlines()==content)
    os.remove(SAMPLE_FILE)

# program should give error on a damaged compressed file
def test_decompress_error(capfd):
    wrong_file='dummy.txt'
    create_test_file(wrong_file)
    wrong_compressed=wrong_file+'.gz'
    process=run([PROGRAM,wrong_file])
    # now damage the compressed file by writing a random byte
    with open(wrong_compressed, "r+b") as file:
        file.seek(32)
        file.write(bytes(0xFF))
    # decompression should fail        
    process=run([PROGRAM,'-d',wrong_compressed])
    stdout, stderr = capfd.readouterr()
    assert process.returncode==1
    assert 'invalid compressed data' in stderr
    os.remove(wrong_file+'.gz')

# utility function
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
