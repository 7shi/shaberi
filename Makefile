ifndef DATE
$(error DATE is not defined. Please run with: make DATE=MM-DD)
endif

GEMINI := gemini-2.5-pro-preview-$(DATE)

all:
	@echo "targets: answer, judge, archive"

answer:
	uv run generate_answers.py -m $(GEMINI) -d shaberi3

judge:
	uv run judge_answers.py -m $(GEMINI) --evaluation_model gemini-2.5-flash-preview-05-20 -d shaberi3

archive:
	tar cvzf $(GEMINI).tar.gz `find data -name $(GEMINI).json`
