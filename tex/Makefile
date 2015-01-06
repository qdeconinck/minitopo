MAINDOC=main.pdf
MAINDOCSRC= $(MAINDOC:.pdf=.tex)
TEX_FILES= main.tex include/why.tex include/goals.tex
PDFLATEX=pdflatex

all: $(MAINDOC)

$(MAINDOC): $(TEX_FILES)
	$(PDFLATEX) $(MAINDOCSRC)	
