# TECK

Status: still in dev and personal use, not ready to release.

## Features

- Working on all platform(Only tested on macOS and Windows)
- Config with YAML
- Auto switch deck by active application, also can toggle off the feature
- Handle multiple keys press combination
- Use icons from FontAwesome or other open source icons
- Trigger any commands can be called by Python
- Generate text as Image and auto update, e.g. clock, price of stock 

## Dependencies

Please refer to [Default LibUSB HIDAPI Backend] for details for all OSs.

```shell
brew install hidapi

git clone --depth 1 https://github.com/FortAwesome/Font-Awesome.git assets/fontawesome
```

### Windows

```powershell
# If using custom repository
# $env:REQUESTS_CA_BUNDLE="assets/cacert.pem"
poetry install
```

[Default LibUSB HIDAPI Backend]: https://python-elgato-streamdeck.readthedocs.io/en/stable/pages/backend_libusb_hidapi.html
