JOBNAME := eaai22_bgmmwlf

$(JOBNAME).pdf: $(JOBNAME).tex *.tex *.bib
	pdflatex $(JOBNAME).tex
	bibtex $(JOBNAME).aux
	pdflatex $(JOBNAME).tex
	pdflatex $(JOBNAME).tex

.PHONY: clean
clean:
	rm -rf $(wildcard *.aux) \
		$(wildcard *.out) \
		$(wildcard *.js) \
		$(wildcard *.log) \
		$(wildcard *.pdf) \
		$(wildcard *.toc) \
		$(wildcard *.bbl) \
		$(wildcard *.bcf) \
		$(wildcard *.blg) \
		$(wildcard *.dvi) \
		$(wildcard *.xml) \
		$(wildcard *.gz)
