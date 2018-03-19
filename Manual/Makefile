# Makefile for LaTeXing
# Currently to take care of bibliography via biber
# Target "clean" deletes temporary LaTeX files

# Copyright (c) 2018, Till Biskup
# 2018-03-19

LATEXBASEFILE = SimPel_Manual.tex

pdf:
	pdflatex $(LATEXBASEFILE)

bib:
	pdflatex $(LATEXBASEFILE)
	biber $(LATEXBASEFILE)
	pdflatex $(LATEXBASEFILE)
	pdflatex $(LATEXBASEFILE)

clean:
	rm -f *aux *lo? *xml *out *toc *bbl *bcf *blg *mtc* *maf

