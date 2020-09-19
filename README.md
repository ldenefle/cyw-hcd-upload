# CYW HCD Uploader

This is an implementation of the Cypress HCI protocols in python. It focuses on the ram loading of a `hcd` file which is a cypress defined format to store a firmware as a succession of HCI commands in order to be loaded directly in a slave ram from a master through UART HCI commands as specified [here](https://cypresssemiconductorco.github.io/btsdk-docs/BT-SDK/WICED-HCI-Control-Protocol.pdf).

## Installation

The project supports `nix-shell` if you're a nix user, otherwise simply install the `requirements.txt` through pip.

## Installation

```
Usage: cyw-hdc-upload.py [OPTIONS]

  Load a cypress firmware in hcd format in ram

Options:
  --fw FILENAME    HCD Firmware file path  [required]
  -p, --port TEXT  Serial port to use to communicate HCI commands  [required]
  -v, --verbose    Make the output verbose
  --help           Show this message and exit.
```
