# TECK

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