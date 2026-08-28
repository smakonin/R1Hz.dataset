# Manuscript source

`ieeedata_descriptor.tex` is the IEEE Data Descriptions manuscript source and `ieeedata_descriptor.pdf` is its compiled output. The local bundle includes the journal class, bibliography style, and logo needed by the template.

With a current TeX Live installation, compile from this directory with:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error ieeedata_descriptor.tex
```

Article DOI and received/revised/accepted/publication dates remain publisher-assigned fields.
