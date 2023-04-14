<p align="center">
  <h1 align="center">ipsw-py</h1>
  <h4><p align="center"><code>ipsw</code> SDK for Python 🚧</p></h4>
  <p align="center">
    <a href="https://github.com/blacktop/ipsw-py/actionss" alt="Actions">
          <img src="https://github.com/blacktop/ipsw-py/actions/workflows/python-publish.yml/badge.svg" /></a>
    <a href="https://pypi.org/project/ipsw/" alt="PyPi - Package">
          <img src="https://img.shields.io/pypi/v/ipsw.svg" /></a>    
    <a href="https://pypi.org/project/ipsw/" alt="PyPi - Downloads">    
          <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/ipsw?color=orange"></a>      
    <a href="http://doge.mit-license.org" alt="LICENSE">
          <img src="https://img.shields.io/:license-mit-blue.svg" /></a>          
</p>
<br>

## `NOTE:` This is a work in progress ⚠️

## Getting Started

Start the `ipsw` daemon:

### macOS

```bash
brew install blacktop/tap/ipswd
brew services start blacktop/tap/ipswd
```

### Linux

> ⚠️ UNTESTED ⚠️

```bash
sudo snap install ipswd
```

### Docker

```bash
docker run -d -p 3993:3993 -v `pwd`:/data blacktop/ipswd start
```

## Installing

The latest stable version is [available on PyPI](https://pypi.org/project/ipsw/). Either add `ipsw` to your `requirements.txt` file or install with **pip**:

```bash
pip install ipsw
```

## Geting Started

Get IPSW info

```python
import ipsw

client = ipsw.IpswClient(base_url='tcp://127.0.0.1:3993')

info = client.info.get("iPhone15,2_16.5_20F5028e_Restore.ipsw")
print(f'{info.version} ({info.build})')
for device in info.devices:
    print(f'- {device}')
```
```bash
16.5 (20F5028e)
- iPhone 14 Pro
```

Get DSC info

```python
import ipsw

client = ipsw.IpswClient(base_url='tcp://127.0.0.1:3993')

dsc = client.dsc.get_info("20F5028e__iPhone15,2/dyld_shared_cache_arm64e")
print(dsc)
print(dsc.dylibs[0])

dylib = client.dsc.get_dylib("20F5028e__iPhone15,2/dyld_shared_cache_arm64e", "libswiftCore.dylib")
print(dylib)
```
```bash
<DSC: '(dyld_v1  arm64e) - iOS - FAEC7714-4CCD-3B99-B18F-F5EAB60DE31E'>
{'index': 1, 'name': '/usr/lib/libobjc.A.dylib', 'version': '876.0.0.0.0', 'uuid': '085A190C-6214-38EA-ACCB-428C3E8AFA65', 'load_address': 6443204608}

<Dylib: '64-bit MachO AARCH64 (ARM64e)'>
```

Get MachO info

```python
import ipsw

client = ipsw.IpswClient(base_url='tcp://127.0.0.1:3993')

macho = client.macho.get("/bin/ls", arch="arm64e")
print(macho)
```
```bash
<Macho: '64-bit MachO AARCH64 (ARM64e)'>
```

## Community

You have questions, need support and or just want to talk about `ipsw-py`?

Here are ways to get in touch with the `ipsw-py` community:

[![Join Discord](https://img.shields.io/badge/Join_our_Discord_server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/xx2y9yrcgs)
[![Follow Twitter](https://img.shields.io/badge/follow_on_twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/blacktop__)
[![Follow Mastodon](https://img.shields.io/badge/follow_on_mastodon-6364FF?style=for-the-badge&logo=mastodon&logoColor=white)](https://mastodon.social/@blacktop)
[![GitHub Discussions](https://img.shields.io/badge/GITHUB_DISCUSSION-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/blacktop/ipsw/discussions)

## License

MIT Copyright (c) 2023 **blacktop**
