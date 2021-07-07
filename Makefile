data: data/lexicons/locations.tsv data/lexicons/occupations.tsv data/lexicons/relations.tsv data/lexicons/objects.tsv data/htr_corrections.json

data/lexicons/locations.tsv: scripts/extract_lexicons.py ../golden-agents-thesauri/locations/observations.csv
	scripts/extract_lexicons.py

data/lexicons/occupations.tsv: scripts/extract_lexicons.py ../golden-agents-thesauri/occupations/observations.csv
	scripts/extract_lexicons.py

data/lexicons/relations.tsv: scripts/extract_lexicons.py ../golden-agents-thesauri/relations/observations.csv
	scripts/extract_lexicons.py

data/lexicons/objects.tsv: scripts/extract_lexicons.py ../golden-agents-htr/resources/objects.csv
	scripts/extract_lexicons.py

data/htr_corrections.json: scripts/process_corrections.py ../golden-agents-htr/experiments/htr_verbeterd_1.tsv
	scripts/process_corrections.py

clean:
	-rm data/lexicons/locations.tsv data/lexicons/occupations.tsv data/lexicons/relations.tsv data/lexicons/objects.tsv data/htr_corrections.json

help:
	@echo Options:
	@echo - make
	@echo - make clean