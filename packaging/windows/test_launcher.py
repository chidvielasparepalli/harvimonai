"""Run with Python: check the distribution archive's path boundary."""
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile
from launcher import extract

with TemporaryDirectory() as directory:
    root = Path(directory)
    for entry, safe in [('app/main.py', True), ('../escape.txt', False),
                        ('C:/escape.txt', False), ('app/../../escape.txt', False)]:
        archive = root / 'test.zip'
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr(entry, 'check')
        try:
            extract(archive, root / 'out')
        except ValueError:
            assert not safe, entry
        else:
            assert safe, entry
    assert (root / 'out/app/main.py').read_text() == 'check'
print('Archive extraction boundary passed')
