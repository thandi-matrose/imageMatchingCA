# syCAMOR

The novel Cellular Automata Matching of Optical and Radar Imagery
algorithm presented in this research, comprising a cellular automata feature extraction and semantic segmentation pipeline for SAR imagery matched to an optical classification via mutual information-based raster registration

### Requirements

- Python 3.14
- conda: manages sycamor environment

## Installation

Clone this repo

```bash
git clone https://github.com/thandi-matrose/imageMatchingCA
```

## Usage

### Create Environment

To install dependencies the root directory, run the following command

```bash
make env_create
```

### Retrieve Aerial Imagery

```bash
make aerial
```

### Retrieve SAR Imagery

1. Register an account on [Copernicus Dataspace Sentinel Hub](https://shapps.dataspace.copernicus.eu/dashboard/#/)
2. Create an OAuth client by navigating to the User Settings in the bottom of the left sidebar and, in the OAuth client frame, click create and follow the dialogs
3. Paste the client API key and the in the .env file in this root directory

```bash
...
```

4. Run

```bash
make aerial
```

## Documentation

[Accompanying Thesis](https://github.com/thandi-matrose/honoursthesis/blob/e445c416e207b8a5d50cf13d0daf6846792567bb/Thesis.pdf)

## License

MIT License

Copyright (c) [2026] [Thandi Matrose]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
