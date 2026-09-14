# DNS Blocklist

This repository combines the sources listed in `adlist.txt` into a single DNS blocklist.

## Download

The latest generated blocklist is published as a GitHub Release asset:

[Download the latest DNS blocklist](https://github.com/arobass/dns-blocklist/releases/download/dns-blocklist-latest/merged-dns-blocklist.txt)

The release uses the stable tag `dns-blocklist-latest`, so this URL always points to the newest published file.

## Updates

GitHub Actions regenerates the blocklist hourly and when changes are pushed to `master`. The generated file is intentionally not committed to Git because it exceeds GitHub's file size limit; it is uploaded to the release instead.

Pull request runs generate and validate the file but do not publish a release asset.

## Local generation

Run the generator with Python:

```sh
python import-merge-blocklist.py
```

This creates `merged-dns-blocklist.txt` locally. The file is ignored by Git.
