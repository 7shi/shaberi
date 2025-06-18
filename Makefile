PREFIX := gemini-2.5-pro

ifneq ($(filter answer judge ,$(MAKECMDGOALS)),)
ifndef DATE
$(error DATE is not defined. Please run with: make DATE=MM-DD)
endif
endif

GEMINI := $(PREFIX)-preview-$(DATE)

# For Free Tier usage, uncomment "-n 1" to limit parallel processing
OPTIONS := -m $(GEMINI) -d shaberi3 -t 131072 #-n 1

all:
	@echo "targets: answer, judge, archive"

answer:
	uv run generate_answers.py $(OPTIONS)

judge:
	uv run judge_answers.py -e gemini-2.5-flash-preview-05-20 $(OPTIONS)

archive:
	tar cvzf $(PREFIX).tar.gz `find data results -name "$(PREFIX)*"`

clean:
	#find . -name "*$(PREFIX)*"
	#find . -name "*$(PREFIX)*" -delete
	find ~/.cache/huggingface/datasets/ -name "cache-*.arrow"
	find ~/.cache/huggingface/datasets/ -name "cache-*.arrow" -delete

check:
	find data/model_answers -name "$(PREFIX)*.json" | xargs grep '"ModelAnswer":null' | wc -l
	find data/judgements -name "$(PREFIX)*.json" | xargs grep ',"score":null' | wc -l
