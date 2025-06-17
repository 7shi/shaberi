PREFIX := gemini-2.5-pro-preview

ifneq ($(filter answer judge archive,$(MAKECMDGOALS)),)
ifndef DATE
$(error DATE is not defined. Please run with: make DATE=MM-DD)
endif
endif

GEMINI := $(PREFIX)-$(DATE)

all:
	@echo "targets: answer, judge, archive"

answer:
	uv run generate_answers.py -m $(GEMINI) -d shaberi3

judge:
	uv run judge_answers.py -m $(GEMINI) --evaluation_model gemini-2.5-flash-preview-05-20 -d shaberi3

archive:
	tar cvzf $(GEMINI).tar.gz `find data -name $(GEMINI).json`

clean:
	find . -name "*$(PREFIX)*"
	find . -name "*$(PREFIX)*" -delete
	find ~/.cache/huggingface/datasets/ -name "cache-*.arrow"
	find ~/.cache/huggingface/datasets/ -name "cache-*.arrow" -delete
