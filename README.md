# MicroPython package template

[![Downloads](https://pepy.tech/badge/micropython-package-template)](https://pepy.tech/project/micropython-package-template)
![Release](https://img.shields.io/github/v/release/brainelectronics/micropython-package-template?include_prereleases&color=success)
![MicroPython](https://img.shields.io/badge/micropython-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/github/brainelectronics/micropython-package-template/branch/main/graph/badge.svg)](https://app.codecov.io/github/brainelectronics/micropython-package-template)
[![CI](https://github.com/brainelectronics/micropython-package-template/actions/workflows/release.yml/badge.svg)](https://github.com/brainelectronics/micropython-package-template/actions/workflows/release.yml)

MicroPython PyPi package template project with auto deploy

---------------

## General

MicroPython PyPi package template with GitHub Action based testing and deploy

📚 The latest documentation is available at
[MicroPython Package Template ReadTheDocs][ref-rtd-micropython-package-template] 📚

<!-- MarkdownTOC -->

- [Installation](#installation)
	- [Install required tools](#install-required-tools)
- [Setup](#setup)
	- [Install package with upip](#install-package-with-upip)
		- [General](#general)
		- [Specific version](#specific-version)
		- [Test version](#test-version)
	- [Manually](#manually)
		- [Upload files to board](#upload-files-to-board)
- [Usage](#usage)
- [Create a PyPi \(micropython\) package](#create-a-pypi-micropython-package)
	- [Setup](#setup-1)
	- [Create a distribution](#create-a-distribution)
	- [Upload to PyPi](#upload-to-pypi)
- [Contributing](#contributing)
	- [Unittests](#unittests)
- [Steps after using this template](#steps-after-using-this-template)
- [Credits](#credits)

<!-- /MarkdownTOC -->

## Installation

### Install required tools

Python3 must be installed on your system. Check the current Python version
with the following command

```bash
python --version
python3 --version
```

Depending on which command `Python 3.x.y` (with x.y as some numbers) is
returned, use that command to proceed.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Setup

### Install package with upip

Connect the MicroPython device to a network (if possible)

```python
import network
station = network.WLAN(network.STA_IF)
station.connect('SSID', 'PASSWORD')
station.isconnected()
```

#### General

Install the latest package version of this lib on the MicroPython device

```python
import mip
mip.install("github:brainelectronics/micropython-package-template")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import upip
upip.install('micropython-package-template')
```

#### Specific version

Install a specific, fixed package version of this lib on the MicroPython device

```python
import mip
# install a verions of a specific branch
mip.install("github:brainelectronics/micropython-package-template", version="feature/initial-implementation")
# install a tag version
mip.install("github:brainelectronics/micropython-package-template", version="0.6.0")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import upip
upip.install('micropython-package-template==0.1.1')
```

#### Test version

Install a specific release candidate version uploaded to
[Test Python Package Index](https://test.pypi.org/) on every PR on the
MicroPython device. If no specific version is set, the latest stable version
will be used.

```python
import mip
mip.install("github:brainelectronics/micropython-package-template", version="0.6.0-rc9.dev13")
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import upip
# overwrite index_urls to only take artifacts from test.pypi.org
upip.index_urls = ['https://test.pypi.org/pypi']
upip.install('micropython-package-template==0.2.0rc1.dev6')
```

See also [brainelectronics Test PyPi Server in Docker][ref-brainelectronics-test-pypiserver]
for a test PyPi server running on Docker.

### Manually

#### Upload files to board

Copy the module to the MicroPython board and import them as shown below
using [Remote MicroPython shell][ref-remote-upy-shell]

Open the remote shell with the following command. Additionally use `-b 115200`
in case no CP210x is used but a CH34x.

```bash
rshell --port /dev/tty.SLAB_USBtoUART --editor nano
```

Perform the following command inside the `rshell` to copy all files and
folders to the device

```bash
mkdir /pyboard/lib
mkdir /pyboard/lib/be_upy_blink

cp be_upy_blink/* /pyboard/lib/be_upy_blink

cp examples/main.py /pyboard
cp examples/boot.py /pyboard
```

## Usage

```python
from be_upy_blink import flash_led
from machine import Pin

led_pin = Pin(4, Pin.OUT)

flash_led(pin=led_pin, amount=3)
# flash_led(pin=led_pin, amount=3, on_time=1, off_time=3)
```

## Create a PyPi (micropython) package

### Setup

Install the required python package with the following command in a virtual
environment to avoid any conflicts with other packages installed on your local
system.

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install twine
```

### Create a distribution

This module overrides distutils (also compatible with setuptools) `sdist`
command to perform pre- and post-processing as required for MicroPython's
upip package manager. This script is taken from
[pfalcon's picoweb][ref-pfalcon-picoweb-sdist-upip] and updated to be PEP8
conform.

```bash
python setup.py sdist
```

A new folder `dist` will be created. The [`sdist_upip`](sdist_upip.py) will be
used to create everything necessary.

### Upload to PyPi

**Be aware: [pypi.org][ref-pypi] and [test.pypi.org][ref-test-pypi] are different**

You can **NOT** login to [test.pypi.org][ref-test-pypi] with the
[pypi.org][ref-pypi] account unless you created the same on the other. See
[invalid auth help page of **test** pypi][ref-invalid-auth-test-pypi]

For testing purposes add `--repository testpypi` to
upload it to [test.pypi.org][ref-test-pypi]

```bash
twine upload dist/micropython-package-template-*.tar.gz -u PYPI_USERNAME -p PYPI_PASSWORD
```

## Contributing

### Unittests

Run the unittests locally with the following command after installing this
package in a virtual environment

```bash
# run all tests
nose2 --config tests/unittest.cfg

# run only one specific tests
nose2 tests.test_blink.TestBlink.test_flash_led
```

Generate the coverage files with

```bash
python create_report_dirs.py
coverage html
```

The coverage report is placed at `reports/coverage/html/index.html`

## Steps after using this template

In order to use this template for a new MicroPython package to following steps
should be done and changes to these file being made

| File | Changes | More details |
| ---- | ------- | -------------|
| `.coveragerc` | Path to `version.py` file | Omit version file from coverage |
| `.coveragerc` | Path to `include` folder | Include the package folder for coverage |
| `.github/workflows/release.yml` | Path to `version.py` file | Use package version file to set changelog based version |
| `.github/workflows/test-release.yml` | Path to `version.py` file | Use package version file to set changelog based version |
| `.github/workflows/test.yml` | Path to `version.py` file | Use package version file to set changelog based version |
| `README.md` | Links in header section and installation instructions | |
| `changelog.md` | Cleanup changelog from informations of template | Keep usage of SemVer |
| `docs/DOCUMENTATION.md` | Kink to ReadTheDocs | |
| `docs/conf.py` | List to modules to be mocked, package import, path to `version.py` file, update `author`, `project` and `linkcheck_ignore` | |
| `docs/index.rst` | Header name and included modules | Replace `be_upy_blink` with new `.rst` file of new package |
| `docs/NEW_MODULE_NAME.rst` | Create a new `.rst` file  named as the package | Use `docs/be_upy_blink.rst` as template |
| `package.json` | Files and paths to new package and repo | Used by `mip` |
| `setup.py` | Path to `version.py` file, `name`, `description`, `url`, `author`, `author_email`, `keywords`, `project_urls`, `packages`, `install_requires` | Used to create the package and its informations published at e.g. PyPI |

## Credits

Based on the [PyPa sample project][ref-pypa-sample].

<!-- Links -->
[ref-rtd-micropython-package-template]: https://micropython-package-template.readthedocs.io/en/latest/
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-brainelectronics-test-pypiserver]: https://github.com/brainelectronics/test-pypiserver
[ref-pypa-sample]: https://github.com/pypa/sampleproject
[ref-pfalcon-picoweb-sdist-upip]: https://github.com/pfalcon/picoweb/blob/b74428ebdde97ed1795338c13a3bdf05d71366a0/sdist_upip.py
[ref-test-pypi]: https://test.pypi.org/
[ref-pypi]: https://pypi.org/
[ref-invalid-auth-test-pypi]: https://test.pypi.org/help/#invalid-auth
